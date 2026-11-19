"""Offline checks of the installed package and distribution metadata."""

from importlib.metadata import metadata
from pathlib import Path

import spikesyn


def test_installed_package_uses_src_layout():
    package_path = Path(spikesyn.__file__).resolve()
    assert package_path.parent.name == "spikesyn"
    assert package_path.parent.parent.name == "src"


def test_distribution_metadata():
    distribution = metadata("spikesyn")
    assert distribution["Name"] == "spikesyn"
    assert distribution["Version"] == "0.1.0"
    assert set(distribution["Requires-Python"].split(",")) == {">=3.11", "<3.12"}
