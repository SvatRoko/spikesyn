"""Scientific invariants for exploratory preprocessing; entirely synthetic."""

from dataclasses import replace

import mne
import numpy as np
import pytest

from spikesyn.preprocessing import ExplorationConfig, prepare_epochs


@pytest.fixture
def config():
    return ExplorationConfig(8, 30, 2, 7.5, 265, 1, 4)


@pytest.fixture
def recording(raw):
    sfreq = 160
    time = np.arange(40 * sfreq) / sfreq
    signal = (
        30 * np.sin(2 * np.pi * 2 * time)
        + 15 * np.sin(2 * np.pi * 10 * time)
        + 5 * np.sin(2 * np.pi * 60 * time)
    ) * 1e-6
    data = (1 + np.arange(64)[:, None] / 64) * signal
    result = mne.io.RawArray(data, raw.info.copy(), verbose=False)
    result.set_annotations(
        mne.Annotations(
            [0, 4.2, 8.3, 12.5, 16.6, 20.8, 24.9, 29.1, 33.2, 35.4],
            [4.2, 4.1, 4.2, 4.1, 4.2, 4.1, 4.2, 4.1, 2.2, 4.1],
            ["T0", "T1", "T0", "T2", "T0", "T1", "T0", "T2", "T0", "T1"],
        )
    )
    return result


def test_exact_epoch_alignment_and_boundary_ledger(recording, config):
    before = recording.get_data().copy()
    names = recording.ch_names.copy()
    filtered, epochs, taps, ledger = prepare_epochs(recording, config)
    assert len(taps) == 265
    np.testing.assert_allclose(taps, taps[::-1], atol=1e-14)
    assert epochs.get_data().shape == (4, 64, 480)
    np.testing.assert_array_equal(epochs.events[:, 2], [1, 2, 1, 2])
    assert epochs.baseline is None
    assert epochs.times[0] == 1.0
    assert epochs.times[-1] == 4 - 1 / 160
    retained = [row for row in ledger if row["retained"]]
    assert len(ledger) == 5
    assert retained[0]["trial_id"] == "S001R04-a01"
    for epoch, row in zip(epochs.get_data(), retained, strict=True):
        expected = filtered.get_data()[
            :, row["start_sample"] : row["stop_sample_exclusive"]
        ]
        np.testing.assert_allclose(epoch, expected, atol=1e-14)
    assert ledger[-1]["exclusion_reasons"] == ["insufficient_real_data_for_fir_support"]
    assert not ledger[-1]["retained"]
    np.testing.assert_array_equal(recording.get_data(), before)
    assert recording.ch_names == names
    assert recording.info["highpass"] == 0
    assert filtered.info["highpass"] == 8
    assert filtered.info["lowpass"] == 30


def test_filter_preserves_passband_phase_and_suppresses_outside(recording, config):
    filtered, _, _, _ = prepare_epochs(recording, config)
    # Evaluate well away from run edges over an integer number of periods.
    time = np.arange(3 * 160, 36 * 160) / 160
    signal = filtered.get_data()[0, 3 * 160 : 36 * 160]
    amplitudes = {}
    for frequency in (2, 10, 60):
        sine = np.sin(2 * np.pi * frequency * time)
        cosine = np.cos(2 * np.pi * frequency * time)
        amplitudes[frequency] = 2 * np.dot(signal, sine) / len(signal)
        if frequency == 10:
            assert abs(2 * np.dot(signal, cosine) / len(signal)) < 1e-9
    assert amplitudes[10] == pytest.approx(15e-6, rel=0.02)
    assert abs(amplitudes[2]) < 30e-6 * 0.01
    assert abs(amplitudes[60]) < 5e-6 * 0.01
    # Identical shared activity is retained: no implicit average rereference.
    assert np.std(signal) > 5e-6


def test_short_annotation_excluded_with_reason(recording, config):
    recording.annotations.duration[1] = 3.5
    _, epochs, _, ledger = prepare_epochs(recording, config)
    assert len(epochs) == 3
    assert ledger[0]["exclusion_reasons"] == ["epoch_exceeds_task_annotation"]


def test_no_eligible_windows_fails(recording, config):
    with pytest.raises(ValueError, match="No eligible"):
        prepare_epochs(recording, replace(config, epoch_stop_s=5))


def test_preexisting_bad_channels_not_silently_included(recording, config):
    recording.info["bads"] = [recording.ch_names[0]]
    with pytest.raises(ValueError, match="bad channels"):
        prepare_epochs(recording, config)


@pytest.mark.parametrize(
    "changes",
    [
        {"low_hz": 0},
        {"high_hz": 80},
        {"low_hz": 31},
        {"low_transition_hz": 0},
        {"high_transition_hz": 51},
        {"filter_length": 264},
        {"filter_length": 265.0},
        {"epoch_start_s": -1},
        {"epoch_stop_s": 1},
        {"epoch_start_s": 1.001},
        {"low_hz": float("nan")},
        {"low_hz": True},
    ],
)
def test_invalid_config_rejected(config, changes):
    with pytest.raises(ValueError):
        replace(config, **changes).validate(160)


def test_export_keeps_trial_identity_units_and_reproducible_arrays(
    recording, config, tmp_path, monkeypatch
):
    import hashlib
    import json
    from dataclasses import asdict

    from spikesyn import inspection, preprocessing

    payload = b"synthetic EDF reader fixture"
    source = tmp_path / "S001R04.edf"
    source.write_bytes(payload)
    monkeypatch.setattr(inspection, "SHA256", hashlib.sha256(payload).hexdigest())
    monkeypatch.setattr(preprocessing.mne.io, "read_raw_edf", lambda *a, **k: recording)
    monkeypatch.setattr(preprocessing, "save_quality_review", lambda *a: {})
    monkeypatch.setattr(preprocessing, "save_comparison", lambda *a: None)
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(asdict(config)))
    output = tmp_path / "results"
    report = preprocessing.run(source, config_path, output)
    saved_report = json.loads((output / "preprocessing.json").read_text())
    assert report == saved_report
    assert report["epoch_shape"] == [4, 64, 480]
    assert report["retained_counts"] == {"1": 2, "2": 2}
    retained = [r for r in report["trial_ledger"] if r["retained"]]
    with np.load(output / "epochs.npz", allow_pickle=False) as exported:
        assert exported["X_v"].shape == (4, 64, 480)
        np.testing.assert_array_equal(exported["y"], [r["label"] for r in retained])
        np.testing.assert_array_equal(
            exported["trial_ids"], [r["trial_id"] for r in retained]
        )
        np.testing.assert_array_equal(
            exported["event_samples"], [672, 2000, 3328, 4656]
        )
        original_arrays = {key: exported[key].copy() for key in exported.files}
    preprocessing.run(source, config_path, output)
    with np.load(output / "epochs.npz", allow_pickle=False) as exported:
        for key, expected in original_arrays.items():
            np.testing.assert_array_equal(exported[key], expected)
    assert source.read_bytes() == payload
