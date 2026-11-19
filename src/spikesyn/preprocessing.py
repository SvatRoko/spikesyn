"""Provisional offline filtering and epoch extraction for verified S001R04."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from importlib.metadata import version
from pathlib import Path

import mne
import numpy as np
from scipy.signal import freqz, welch

from spikesyn.inspection import DEFAULT_EDF, summarize_raw, verify_recording
from spikesyn.quality import save_quality_review

DEFAULT_CONFIG = Path("configs/m01-exploration.json")
DEFAULT_OUTPUT = Path("results/m01-s001r04/preprocessing")


@dataclass(frozen=True)
class ExplorationConfig:
    """All adjustable parameters; other pipeline policies are fixed and reported."""

    low_hz: float
    high_hz: float
    low_transition_hz: float
    high_transition_hz: float
    filter_length: int
    epoch_start_s: float
    epoch_stop_s: float

    def validate(self, sfreq: float) -> None:
        numeric = list(asdict(self).values())
        if any(isinstance(v, bool) or not isinstance(v, (int, float)) for v in numeric):
            raise ValueError("Configuration values must be numeric")
        if not np.isfinite(numeric).all():
            raise ValueError("Configuration must be finite")
        if not 0 < self.low_hz < self.high_hz < sfreq / 2:
            raise ValueError("Filter passband must be strictly inside Nyquist")
        if not 0 < self.low_transition_hz <= self.low_hz:
            raise ValueError("Invalid low transition width")
        if not 0 < self.high_transition_hz <= sfreq / 2 - self.high_hz:
            raise ValueError("Invalid high transition width")
        if not isinstance(self.filter_length, int) or self.filter_length < 3:
            raise ValueError("Filter length must be an integer >= 3")
        if self.filter_length % 2 == 0:
            raise ValueError("Zero-phase FIR requires an odd filter length")
        if not 0 <= self.epoch_start_s < self.epoch_stop_s:
            raise ValueError("Epoch must have nonnegative start and later stop")
        for endpoint in (self.epoch_start_s, self.epoch_stop_s):
            if not np.isclose(
                endpoint * sfreq, round(endpoint * sfreq), atol=1e-8, rtol=0
            ):
                raise ValueError("Epoch endpoints must align to samples")


def filter_arguments(config: ExplorationConfig) -> dict:
    return {
        "l_freq": config.low_hz,
        "h_freq": config.high_hz,
        "l_trans_bandwidth": config.low_transition_hz,
        "h_trans_bandwidth": config.high_transition_hz,
        "filter_length": config.filter_length,
        "method": "fir",
        "phase": "zero",
        "fir_window": "hamming",
        "fir_design": "firwin",
    }


def prepare_epochs(
    raw: mne.io.BaseRaw, config: ExplorationConfig
) -> tuple[mne.io.BaseRaw, mne.Epochs, np.ndarray, list[dict]]:
    """Filter a copy of a whole run and return epochs plus a full trial ledger.

    Keep the recorded reference and all channels. No baseline correction,
    projections, resampling, amplitude rejection or learned transformations.
    Reject epochs with incomplete task duration or real-data FIR support.
    """
    config.validate(float(raw.info["sfreq"]))
    summary = summarize_raw(raw)
    if raw.info["bads"] or raw.info["projs"]:
        raise ValueError("Resolve preexisting bad channels/projections explicitly")
    sfreq = float(raw.info["sfreq"])
    if raw.n_times <= config.filter_length:
        raise ValueError("Recording is too short for the configured filter")
    taps = mne.filter.create_filter(
        None, sfreq, **filter_arguments(config), verbose=False
    )
    half_support = (len(taps) - 1) // 2
    filtered = raw.copy().load_data()
    mne.datasets.eegbci.standardize(filtered)
    filtered.filter(
        **filter_arguments(config),
        picks="eeg",
        pad="reflect_limited",
        skip_by_annotation=(),
        n_jobs=1,
        verbose=False,
    )
    start_offset = int(round(config.epoch_start_s * sfreq))
    stop_offset = int(round(config.epoch_stop_s * sfreq))
    ledger = []
    events = []
    for index, annotation in enumerate(summary["annotations"]):
        if annotation["code"] == "T0":
            continue
        onset = annotation["onset_sample"]
        if not np.isclose(onset / sfreq, annotation["onset_s"], atol=1e-8, rtol=0):
            raise ValueError("Task onset is not sample-aligned")
        start, stop = onset + start_offset, onset + stop_offset
        reasons = []
        if config.epoch_stop_s > annotation["duration_s"] + 1e-8:
            reasons.append("epoch_exceeds_task_annotation")
        if start - half_support < 0 or stop + half_support > raw.n_times:
            reasons.append("insufficient_real_data_for_fir_support")
        label = {"T1": 1, "T2": 2}[annotation["code"]]
        row = {
            "trial_id": f"S001R04-a{index:02d}",
            "annotation_index": index,
            "annotation_code": annotation["code"],
            "label": label,
            "event_sample": onset,
            "start_sample": start,
            "stop_sample_exclusive": stop,
            "retained": not reasons,
            "exclusion_reasons": reasons,
        }
        ledger.append(row)
        if not reasons:
            events.append([onset, 0, label])
    if not events:
        raise ValueError("No eligible imagery windows remain")
    present = {event[2] for event in events}
    event_id = {
        name: label
        for name, label in {"imagined_left_fist": 1, "imagined_right_fist": 2}.items()
        if label in present
    }
    epochs = mne.Epochs(
        filtered,
        np.asarray(events, dtype=int),
        event_id=event_id,
        tmin=config.epoch_start_s,
        tmax=(stop_offset - 1) / sfreq,
        baseline=None,
        picks=filtered.ch_names,
        proj=False,
        preload=True,
        reject=None,
        flat=None,
        reject_by_annotation=True,
        detrend=None,
        verbose=False,
    )
    if len(epochs) != len(events):
        raise RuntimeError(f"Unexpected MNE epoch drops: {epochs.drop_log}")
    expected = (len(events), 64, stop_offset - start_offset)
    if epochs.get_data().shape != expected or not np.isfinite(epochs.get_data()).all():
        raise RuntimeError("Invalid epoch dimensions or non-finite data")
    return filtered, epochs, taps, ledger


def save_comparison(
    raw: mne.io.BaseRaw,
    filtered: mne.io.BaseRaw,
    taps: np.ndarray,
    config: ExplorationConfig,
    output: Path,
) -> None:
    """Plot measured spectral changes and the designed FIR frequency response."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))
    for recording, label in (
        (raw, "as recorded"),
        (filtered, f"{config.low_hz:g}-{config.high_hz:g} Hz FIR"),
    ):
        frequencies, power = welch(
            recording.get_data(),
            fs=160,
            window="hann",
            nperseg=640,
            noverlap=320,
            detrend="constant",
            scaling="density",
            axis=-1,
        )
        axes[0].semilogy(frequencies, np.median(power, axis=0) * 1e12, label=label)
    axes[0].set(
        xlim=(0, 80),
        xlabel="Frequency (Hz)",
        ylabel="Median PSD (uV^2/Hz)",
        title="Whole-run PSD: before and after exploratory filtering",
    )
    frequencies, response = freqz(taps, worN=4096, fs=160)
    axes[1].plot(frequencies, 20 * np.log10(np.maximum(abs(response), 1e-8)))
    axes[1].axvspan(config.low_hz, config.high_hz, alpha=0.12, color="green")
    axes[1].set(
        xlim=(0, 80),
        ylim=(-100, 5),
        xlabel="Frequency (Hz)",
        ylabel="Amplitude response (dB)",
        title="Configured zero-phase FIR",
    )
    for ax in axes:
        ax.grid(alpha=0.2)
    axes[0].legend()
    fig.tight_layout()
    fig.savefig(output / "filter-comparison.png", dpi=140)
    plt.close(fig)


def run(recording: Path, config_path: Path, output: Path) -> dict:
    digest = verify_recording(recording)
    if recording.resolve().is_relative_to(output.resolve()):
        raise ValueError("Output must not contain the raw recording")
    config_bytes = config_path.read_bytes()
    config = ExplorationConfig(**json.loads(config_bytes))
    raw = mne.io.read_raw_edf(recording, preload=True, verbose=False)
    filtered, epochs, taps, ledger = prepare_epochs(raw, config)
    output.mkdir(parents=True, exist_ok=True)
    quality = save_quality_review(raw, output / "quality-review")
    save_comparison(raw, filtered, taps, config, output)
    retained = [row for row in ledger if row["retained"]]
    np.savez_compressed(
        output / "epochs.npz",
        X_v=epochs.get_data(),
        y=epochs.events[:, 2],
        times_s=epochs.times,
        channel_names=np.array(epochs.ch_names),
        event_samples=epochs.events[:, 0],
        annotation_indices=np.array([row["annotation_index"] for row in retained]),
        trial_ids=np.array([row["trial_id"] for row in retained]),
    )
    np.save(output / "filter-taps.npy", taps)
    raw_data = raw.get_data()
    filtered_data = filtered.get_data()
    for row in retained:
        start, stop = row["start_sample"], row["stop_sample_exclusive"]
        row["raw_max_channel_peak_to_peak_uv"] = float(
            np.ptp(raw_data[:, start:stop], axis=1).max() * 1e6
        )
        row["filtered_max_channel_peak_to_peak_uv"] = float(
            np.ptp(filtered_data[:, start:stop], axis=1).max() * 1e6
        )
    report = {
        "recording": "S001R04",
        "raw_sha256": digest,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "status": "exploratory preprocessing; not a final evaluation protocol",
        "config": asdict(config),
        "config_sha256": hashlib.sha256(config_bytes).hexdigest(),
        "source_hashes": {
            p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in (
                Path(__file__),
                Path(__file__).with_name("quality.py"),
                Path(__file__).with_name("inspection.py"),
            )
        },
        "versions": {
            name: version(name)
            for name in ("spikesyn", "mne", "numpy", "scipy", "matplotlib")
        },
        "python_version": platform.python_version(),
        "policies": {
            "reference": "as recorded",
            "channels": "all 64 EEG",
            "baseline": None,
            "artifact_rejection": None,
            "filter": filter_arguments(config),
            "pad": "reflect_limited",
            "epoch_interval": "half-open [start,stop)",
            "edge_policy": "exclude epochs requiring reflected FIR support",
            "resampling": None,
        },
        "fir_taps": len(taps),
        "fir_half_support_s": (len(taps) - 1) / 2 / 160,
        "epoch_shape": list(epochs.get_data().shape),
        "label_mapping": {"1": "imagined_left_fist", "2": "imagined_right_fist"},
        "retained_counts": {
            str(label): int(np.sum(epochs.events[:, 2] == label)) for label in (1, 2)
        },
        "trial_ledger": ledger,
        "quality_review": quality,
        "limitations": [
            "noncausal offline filter",
            "no established artifact removal",
            "continuous filter can mix neighboring rest/task activity",
            "S001 used for exploratory choices; no decoding evidence",
        ],
    }
    verify_recording(recording)
    (output / "preprocessing.json").write_text(
        json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--recording", type=Path, default=DEFAULT_EDF)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    report = run(args.recording, args.config, args.output)
    print(
        json.dumps(
            {
                key: report[key]
                for key in ("epoch_shape", "retained_counts", "fir_half_support_s")
            },
            indent=2,
        )
    )
    print(f"Report and arrays: {args.output}")


if __name__ == "__main__":
    main()
