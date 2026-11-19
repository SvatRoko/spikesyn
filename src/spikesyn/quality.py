"""Full-run descriptive quality plots; no artifact diagnoses or exclusions."""

from pathlib import Path

import mne
import numpy as np


def save_quality_review(raw: mne.io.BaseRaw, output: Path) -> dict:
    """Plot all channels and nonoverlapping one-second amplitude summaries.

    Partial final seconds are included, without padding. The color cap and shared
    trace scale affect display only and are never rejection thresholds.
    """
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    recording = raw.copy()
    mne.datasets.eegbci.standardize(recording)
    data = recording.get_data() * 1e6
    sfreq = float(recording.info["sfreq"])
    step = int(round(sfreq))
    starts = np.arange(0, recording.n_times, step)
    edges_s = np.append(starts, recording.n_times) / sfreq
    amplitudes = np.stack(
        [np.ptp(data[:, s : s + step], axis=1) for s in starts], axis=1
    )
    trace_limit = max(100, int(np.ceil(np.abs(data).max() / 100)) * 100)
    output.mkdir(parents=True, exist_ok=True)
    np.savez(
        output / "raw-window-amplitudes.npz",
        peak_to_peak_uv=amplitudes,
        start_s=edges_s[:-1],
        stop_s=edges_s[1:],
        channels=np.array(recording.ch_names),
    )
    fig, ax = plt.subplots(figsize=(14, 13))
    image = ax.pcolormesh(
        edges_s,
        np.arange(len(data) + 1) - 0.5,
        amplitudes,
        shading="flat",
        cmap="magma",
        vmin=0,
        vmax=500,
    )
    ax.invert_yaxis()
    ax.set_yticks(range(len(data)), recording.ch_names, fontsize=7)
    ax.set(
        xlabel="Time (s); nonoverlapping 1-second windows",
        ylabel="Channel",
        title="S001R04 raw peak-to-peak amplitude (display capped at 500 uV)",
    )
    fig.colorbar(image, ax=ax, label="Peak-to-peak amplitude (uV)")
    fig.tight_layout()
    fig.savefig(output / "raw-window-amplitudes.png", dpi=130)
    plt.close(fig)
    for group, first in enumerate(range(0, len(data), 16), start=1):
        fig, axes = plt.subplots(4, 4, figsize=(16, 10), sharex=True, sharey=True)
        for index, ax in enumerate(axes.flat):
            channel = first + index
            if channel >= len(data):
                ax.set_visible(False)
                continue
            ax.plot(recording.times, data[channel], lw=0.35)
            ax.set_title(recording.ch_names[channel], fontsize=9)
            ax.set_xlim(0, recording.n_times / sfreq)
            ax.set_ylim(-trace_limit, trace_limit)
            ax.grid(alpha=0.2)
        fig.supxlabel("Time (s)")
        fig.supylabel("Original amplitude (uV); shared display scale")
        fig.suptitle(f"S001R04 full-run raw overview {group}/4 (no correction)")
        fig.tight_layout()
        fig.savefig(output / f"raw-overview-{group}.png", dpi=110)
        plt.close(fig)
    largest = []
    for flat in np.argsort(amplitudes, axis=None)[-10:][::-1]:
        channel, window = np.unravel_index(flat, amplitudes.shape)
        largest.append(
            {
                "channel": recording.ch_names[channel],
                "start_s": float(starts[window] / sfreq),
                "peak_to_peak_uv": float(amplitudes[channel, window]),
            }
        )
    return {
        "window_s": 1.0,
        "color_cap_uv": 500,
        "trace_limits_uv": [-trace_limit, trace_limit],
        "largest_windows": largest,
        "interpretation": "descriptive only; no automatic artifact rejection",
    }
