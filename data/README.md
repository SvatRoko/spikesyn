# Local EEG data

Raw recordings and derived data must remain outside Git. This directory ignores
everything except this note. External storage is also acceptable.

M00 downloaded no recordings. Initial M01 retrieves only EEGMMIDB v1.0.0 S001R04
using `uv run --locked python -m spikesyn.inspection fetch` from the repository root. Preserve the original EDF+ file. Record
source URL, retrieval timestamp, SHA-256 and subject/run in the ignored retrieval
manifest. The inspection report records loader and scientific-library versions. Never overwrite raw files during preprocessing.

Dataset definitions and licensing: [dataset documentation](../docs/dataset.md).
