"""Check physical time coordinates in the descriptive quality heatmap."""

import matplotlib
import numpy as np

matplotlib.use("Agg")
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from spikesyn.quality import save_quality_review


def test_partial_final_second_has_correct_heatmap_width(raw, tmp_path, monkeypatch):
    raw.crop(tmax=9.5 - 1 / 160)
    captured = []
    original = Axes.pcolormesh

    def capture(self, *args, **kwargs):
        if len(args) >= 3 and np.asarray(args[2]).shape == (64, 10):
            captured.append(np.asarray(args[0]).copy())
        return original(self, *args, **kwargs)

    monkeypatch.setattr(Axes, "pcolormesh", capture)
    monkeypatch.setattr(Figure, "savefig", lambda *args, **kwargs: None)
    save_quality_review(raw, tmp_path)
    with np.load(tmp_path / "raw-window-amplitudes.npz", allow_pickle=False) as data:
        np.testing.assert_array_equal(data["start_s"], np.arange(10))
        np.testing.assert_array_equal(data["stop_s"], [*range(1, 10), 9.5])
    np.testing.assert_array_equal(captured[0], [*range(10), 9.5])
