"""Synthetic scientific checks; no EEG downloads or real recordings needed."""

import hashlib
import io
import json

import mne
import numpy as np
import pytest

from spikesyn import inspection


def test_summary_preserves_data_names_and_units(raw):
    before = raw.get_data().copy()
    names = raw.ch_names.copy()
    summary = inspection.summarize_raw(raw)
    json.dumps(summary, allow_nan=False)
    assert summary["unannotated_intervals_s"] == [[6.0, 10.0]]
    assert summary["n_samples"] == 1600
    assert summary["duration_s"] == 10
    assert summary["last_sample_time_s"] == 1599 / 160
    assert summary["annotation_counts"] == {"T0": 1, "T1": 1, "T2": 1}
    assert summary["annotations"][1]["meaning"] == "imagined_left_fist"
    assert summary["annotations"][2]["meaning"] == "imagined_right_fist"
    assert summary["annotations"][1]["onset_sample"] == 320
    assert summary["channel_statistics"][0]["peak_to_peak_uv"] == pytest.approx(20)
    assert summary["channel_statistics"][0]["std_uv"] == pytest.approx(10 / np.sqrt(2))
    assert summary["channel_name_mapping"]["C3."] == "C3"
    assert not summary["original_montage_present"]
    assert raw.get_montage() is None
    assert raw.ch_names == names
    np.testing.assert_array_equal(raw.get_data(), before)


@pytest.mark.parametrize("fault", ["channels", "rate", "type", "nonfinite", "cropped"])
def test_invalid_recording_metadata_rejected(raw, fault):
    if fault == "channels":
        raw.drop_channels([raw.ch_names[0]])
    elif fault == "rate":
        raw.resample(128, verbose=False)
    elif fault == "type":
        raw.set_channel_types({raw.ch_names[0]: "eog"}, verbose=False)
    elif fault == "nonfinite":
        raw.apply_function(lambda signal: signal * np.nan, verbose=False)
    else:
        raw.crop(tmin=1)
    with pytest.raises(ValueError):
        inspection.summarize_raw(raw)


@pytest.mark.parametrize(
    "onsets,durations,labels",
    [
        ([0, 2, 4], [2, 2, 2], ["T0", "T1", "UNKNOWN"]),
        ([0, 2], [2, 2], ["T0", "T1"]),
        ([0, 1, 4], [2, 2, 2], ["T0", "T1", "T2"]),
        ([0, 2, 4], [2, 0, 2], ["T0", "T1", "T2"]),
    ],
)
def test_invalid_annotations_rejected(raw, onsets, durations, labels):
    raw.set_annotations(mne.Annotations(onsets, durations, labels))
    with pytest.raises(ValueError):
        inspection.summarize_raw(raw)


def test_corrupt_existing_recording_never_downloaded_or_overwritten(
    tmp_path, monkeypatch
):
    path = tmp_path / "S001R04.edf"
    path.write_bytes(b"corrupted")

    def forbidden(*args, **kwargs):
        pytest.fail("Network must not be used for an existing recording")

    monkeypatch.setattr(inspection, "urlopen", forbidden)
    with pytest.raises(ValueError, match="checksum"):
        inspection.fetch_recording(path)
    assert path.read_bytes() == b"corrupted"


def test_fetch_verifies_and_preserves_provenance(tmp_path, monkeypatch):
    payload = b"synthetic fixture, not EEG"
    monkeypatch.setattr(inspection, "SHA256", hashlib.sha256(payload).hexdigest())
    calls = []

    def fake_open(url, timeout):
        calls.append(url)
        return io.BytesIO(payload)

    monkeypatch.setattr(inspection, "urlopen", fake_open)
    path = tmp_path / "nested" / "S001R04.edf"
    inspection.fetch_recording(path)
    manifest = path.with_suffix(".provenance.json").read_bytes()
    inspection.fetch_recording(path)
    assert path.read_bytes() == payload
    assert path.with_suffix(".provenance.json").read_bytes() == manifest
    assert len(calls) == 1
    assert json.loads(manifest)["sha256"] == hashlib.sha256(payload).hexdigest()


def test_bad_download_not_saved(tmp_path, monkeypatch):
    monkeypatch.setattr(inspection, "urlopen", lambda *a, **k: io.BytesIO(b"bad"))
    path = tmp_path / "S001R04.edf"
    with pytest.raises(ValueError, match="checksum"):
        inspection.fetch_recording(path)
    assert not path.exists()


def test_figures_and_spectrum_use_correct_scaling(raw, tmp_path):
    inspection.save_figures(raw, tmp_path)
    assert (tmp_path / "raw-central.png").is_file()
    assert (tmp_path / "welch-psd.png").is_file()
    with np.load(tmp_path / "welch-psd.npz") as spectrum:
        frequencies = spectrum["frequencies_hz"]
        power = spectrum["psd_v2_hz"]
        assert power.shape == (64, 321)
        assert frequencies[np.argmax(power[0])] == 10
        # Integral of the one-sided density equals sine variance (V^2).
        assert np.sum(power[0]) * 0.25 == pytest.approx((10e-6) ** 2 / 2)


@pytest.mark.parametrize(
    "fault",
    ["past_end", "before_start", "nonfinite_time", "small_overlap", "small_gap"],
)
def test_annotation_boundaries_and_finite_timing(raw, fault):
    # Mutate public annotation arrays after construction to avoid MNE clipping
    # invalid intervals before this validator can exercise its failure paths.
    if fault == "past_end":
        raw.annotations.duration[-1] = 6.003
    elif fault == "before_start":
        raw.annotations.onset[0] = -0.003
    elif fault == "small_overlap":
        raw.annotations.onset[1] -= 0.003
    elif fault == "small_gap":
        raw.annotations.onset[1] += 0.003
        raw.annotations.duration[1] -= 0.003
        summary = inspection.summarize_raw(raw)
        assert summary["unannotated_intervals_s"][0] == [2.0, 2.003]
        return
    else:
        raw.annotations.duration[-1] = np.nan
    with pytest.raises(ValueError):
        inspection.summarize_raw(raw)
