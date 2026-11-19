"""Reproducible, offline inspection of the first EEGMMIDB recording.

Only ``fetch`` performs network access. Raw EDF bytes are never modified.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
from collections import Counter
from datetime import UTC, datetime
from importlib.metadata import version
from pathlib import Path
from urllib.request import urlopen

import mne
import numpy as np
from scipy.signal import welch

SOURCE = "https://physionet.org/files/eegmmidb/1.0.0/S001/S001R04.edf"
CHECKSUM_SOURCE = "https://physionet.org/files/eegmmidb/1.0.0/SHA256SUMS.txt"
SHA256 = "3d161f88e1c00632585287d2ce584c2bc0f08862438eb255ea8723e00fac693d"
LABELS = {"T0": "rest", "T1": "imagined_left_fist", "T2": "imagined_right_fist"}
DEFAULT_EDF = Path("data/eegmmidb/1.0.0/S001/S001R04.edf")
DEFAULT_OUTPUT = Path("results/m01-s001r04")


def verify_recording(path: Path) -> str:
    """Reject bytes differing from the official S001R04 checksum."""
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != SHA256:
        raise ValueError(f"S001R04 checksum mismatch: {digest}")
    return digest


def fetch_recording(path: Path) -> Path:
    """Retrieve this one recording, verifying before saving; never overwrite it."""
    if path.exists():
        verify_recording(path)
        return path
    with urlopen(SOURCE, timeout=60) as response:
        payload = response.read()
    digest = hashlib.sha256(payload).hexdigest()
    if digest != SHA256:
        raise ValueError("Downloaded S001R04 checksum mismatch; file not saved")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as target:
        target.write(payload)
    manifest = {
        "dataset": "EEGMMIDB",
        "dataset_version": "1.0.0",
        "subject": 1,
        "run": 4,
        "source_url": SOURCE,
        "checksum_source": CHECKSUM_SOURCE,
        "sha256": digest,
        "retrieved_at_utc": datetime.now(UTC).isoformat(),
        "size_bytes": len(payload),
        "path": str(path.resolve()),
        "retrieval_method": "Python urllib.request.urlopen; TLS verification enabled",
        "python_version": platform.python_version(),
    }
    path.with_suffix(".provenance.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    return path


def summarize_raw(raw: mne.io.BaseRaw) -> dict:
    """Validate metadata/events and summarize signals without filtering or rejection.

    This validator is specific to an uncropped unilateral-imagery run starting at
    sample zero. MNE supplies EEG amplitudes in SI volts. Template locations are
    attached only to an in-memory copy for name/location compatibility checks.
    """
    if raw.first_samp != 0:
        raise ValueError("Inspection requires an uncropped run starting at sample zero")
    if len(raw.ch_names) != 64 or set(raw.get_channel_types()) != {"eeg"}:
        raise ValueError("Expected exactly 64 EEG channels")
    sfreq = float(raw.info["sfreq"])
    if sfreq != 160.0:
        raise ValueError(f"Expected 160 Hz, found {sfreq}")
    data = raw.get_data()
    if not np.isfinite(data).all():
        raise ValueError("Non-finite EEG sample detected")
    duration = raw.n_times / sfreq
    annotations = []
    previous_end = 0.0
    uncovered = []
    for onset, length, label in zip(
        raw.annotations.onset,
        raw.annotations.duration,
        raw.annotations.description,
        strict=True,
    ):
        if label not in LABELS:
            raise ValueError(f"Unexpected annotation: {label}")
        if not np.isfinite([onset, length]).all() or length <= 0:
            raise ValueError("Invalid annotation timing")
        if onset < previous_end - 1 / sfreq or onset + length > duration + 1 / sfreq:
            raise ValueError("Annotation overlaps or exceeds recording bounds")
        if onset - previous_end > 1 / sfreq:
            uncovered.append([float(previous_end), float(onset)])
        previous_end = onset + length
        annotations.append(
            {
                "onset_s": float(onset),
                "duration_s": float(length),
                "code": str(label),
                "meaning": LABELS[label],
                "onset_sample": int(round(onset * sfreq)),
            }
        )
    if duration - previous_end > 1 / sfreq:
        uncovered.append([float(previous_end), float(duration)])
    counts = dict(Counter(a["code"] for a in annotations))
    if set(counts) != set(LABELS):
        raise ValueError("Expected rest and both imagery labels")
    normalized = raw.copy()
    mne.datasets.eegbci.standardize(normalized)
    normalized.set_montage("colin27_1005", on_missing="raise", verbose=False)
    channel_mapping = dict(zip(raw.ch_names, normalized.ch_names, strict=True))
    stats = []
    for name, signal in zip(normalized.ch_names, data, strict=True):
        stats.append(
            {
                "channel": name,
                "mean_uv": float(signal.mean() * 1e6),
                "std_uv": float(signal.std() * 1e6),
                "peak_to_peak_uv": float(np.ptp(signal) * 1e6),
                "flat": bool(np.ptp(signal) == 0),
            }
        )
    return {
        "channels": len(raw.ch_names),
        "sampling_hz": sfreq,
        "n_samples": int(raw.n_times),
        "duration_s": duration,
        "last_sample_time_s": float(raw.times[-1]),
        "signal_units": "V (MNE SI); channel summary amplitudes in microvolts",
        "channel_name_mapping": channel_mapping,
        "original_montage_present": raw.get_montage() is not None,
        "location_check": "names match template; not measured participant locations",
        "annotation_counts": counts,
        "unannotated_intervals_s": uncovered,
        "annotation_timing_tolerance_s": 1 / sfreq,
        "template_montage": "colin27_1005",
        "annotations": annotations,
        "all_samples_finite": True,
        "channel_statistics": stats,
        "header_highpass_hz": float(raw.info["highpass"]),
        "header_lowpass_hz": float(raw.info["lowpass"]),
        "processing": "no filtering, rereferencing, resampling, epochs or rejection",
    }


def save_figures(raw: mne.io.BaseRaw, output: Path) -> None:
    """Save raw central traces and full-run Welch PSD; no GUI or data mutation."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    normalized = raw.copy()
    mne.datasets.eegbci.standardize(normalized)
    sfreq = float(raw.info["sfreq"])
    channels = ["C3", "Cz", "C4"]
    n = min(raw.n_times, int(20 * sfreq))
    fig, axes = plt.subplots(3, 1, figsize=(12, 7), sharex=True)
    for ax, name in zip(axes, channels, strict=True):
        ax.plot(raw.times[:n], normalized.get_data(picks=[name])[0, :n] * 1e6, lw=0.6)
        for onset, duration, label in zip(
            raw.annotations.onset,
            raw.annotations.duration,
            raw.annotations.description,
            strict=True,
        ):
            if onset >= 20:
                continue
            color = {"T0": "gray", "T1": "tab:blue", "T2": "tab:orange"}[label]
            ax.axvspan(onset, min(onset + duration, 20), color=color, alpha=0.12)
            ax.text(onset, 0.94, label, transform=ax.get_xaxis_transform(), fontsize=8)
        ax.set_ylabel(f"{name} (uV)")
        ax.grid(alpha=0.2)
    axes[-1].set_xlabel("Time from recording start (s)")
    fig.suptitle("S001R04: original signals, first 20 s; annotations T0/T1/T2")
    fig.tight_layout()
    fig.savefig(output / "raw-central.png", dpi=150)
    plt.close(fig)

    # Four-second Hann segments, 50% overlap, constant detrending, density scaling.
    frequencies, power = welch(
        raw.get_data(),
        fs=sfreq,
        window="hann",
        nperseg=640,
        noverlap=320,
        detrend="constant",
        scaling="density",
        axis=-1,
    )
    np.savez(output / "welch-psd.npz", frequencies_hz=frequencies, psd_v2_hz=power)
    fig, ax = plt.subplots(figsize=(10, 5))
    for name in channels:
        ax.semilogy(
            frequencies, power[normalized.ch_names.index(name)] * 1e12, label=name
        )
    ax.semilogy(
        frequencies,
        np.median(power, axis=0) * 1e12,
        color="black",
        lw=1.5,
        label="64-channel median",
    )
    ax.axvspan(8, 30, alpha=0.08, color="green", label="proposed 8-30 Hz band")
    ax.set(
        xlim=(0, 80),
        xlabel="Frequency (Hz)",
        ylabel="PSD (uV^2/Hz)",
        title="S001R04: full-run Welch PSD (0.25 Hz bins; no added filter)",
    )
    ax.legend()
    ax.grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(output / "welch-psd.png", dpi=150)
    plt.close(fig)


def inspect_recording(path: Path, output: Path) -> dict:
    """Verify bytes, load EDF, validate, and write a reproducible local report."""
    digest = verify_recording(path)
    if output.resolve() == path.resolve() or path.resolve().is_relative_to(
        output.resolve()
    ):
        raise ValueError("Output directory must not contain the source recording")
    raw = mne.io.read_raw_edf(path, preload=True, verbose=False)
    summary = summarize_raw(raw)
    summary.update(
        {
            "recording": "S001R04",
            "dataset_version": "1.0.0",
            "sha256": digest,
            "source_url": SOURCE,
            "checksum_source": CHECKSUM_SOURCE,
            "inspected_at_utc": datetime.now(UTC).isoformat(),
            "versions": {
                name: version(name)
                for name in ("spikesyn", "mne", "numpy", "scipy", "matplotlib")
            },
            "python_version": platform.python_version(),
            "inspection_source_sha256": hashlib.sha256(
                Path(__file__).read_bytes()
            ).hexdigest(),
            "welch": {
                "window": "hann",
                "nperseg": 640,
                "noverlap": 320,
                "detrend": "constant",
                "scaling": "density",
            },
        }
    )
    output.mkdir(parents=True, exist_ok=True)
    save_figures(raw, output)
    if verify_recording(path) != digest:
        raise ValueError("Source bytes changed during inspection")
    (output / "inspection.json").write_text(
        json.dumps(summary, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["fetch", "inspect"])
    parser.add_argument("--recording", type=Path, default=DEFAULT_EDF)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    if args.action == "fetch":
        print(fetch_recording(args.recording))
    else:
        summary = inspect_recording(args.recording, args.output)
        print(
            json.dumps(
                {
                    key: summary[key]
                    for key in (
                        "channels",
                        "sampling_hz",
                        "duration_s",
                        "annotation_counts",
                    )
                },
                indent=2,
            )
        )
        print(f"Local report: {args.output / 'inspection.json'}")


if __name__ == "__main__":
    main()
