"""Shared offline synthetic EEG fixtures."""

import mne
import numpy as np
import pytest


@pytest.fixture
def raw():
    names = [
        "FC5",
        "FC3",
        "FC1",
        "FCz",
        "FC2",
        "FC4",
        "FC6",
        "C5",
        "C3",
        "C1",
        "Cz",
        "C2",
        "C4",
        "C6",
        "CP5",
        "CP3",
        "CP1",
        "CPz",
        "CP2",
        "CP4",
        "CP6",
        "Fp1",
        "Fpz",
        "Fp2",
        "AF7",
        "AF3",
        "AFz",
        "AF4",
        "AF8",
        "F7",
        "F5",
        "F3",
        "F1",
        "Fz",
        "F2",
        "F4",
        "F6",
        "F8",
        "FT7",
        "FT8",
        "T7",
        "T8",
        "T9",
        "T10",
        "TP7",
        "TP8",
        "P7",
        "P5",
        "P3",
        "P1",
        "Pz",
        "P2",
        "P4",
        "P6",
        "P8",
        "PO7",
        "PO3",
        "POz",
        "PO4",
        "PO8",
        "O1",
        "Oz",
        "O2",
        "Iz",
    ]
    info = mne.create_info([name + "." for name in names], 160, "eeg")
    time = np.arange(1600) / 160
    data = np.tile(10e-6 * np.sin(2 * np.pi * 10 * time), (64, 1))
    recording = mne.io.RawArray(data, info, verbose=False)
    recording.set_annotations(mne.Annotations([0, 2, 4], [2, 2, 2], ["T0", "T1", "T2"]))
    return recording
