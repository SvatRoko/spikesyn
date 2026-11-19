# Local EEG data

Raw recordings and derived data must remain outside Git. This directory ignores
everything except this note. External storage is also acceptable.

M00 downloads no recordings. In M01, retrieve only EEGMMIDB v1.0.0 S001R04 using
a documented PhysioNet or MNE method. Preserve the original EDF+ file. Record
source URL, retrieval timestamp, SHA-256, subject/run, and loader version in an
ignored local manifest. Never overwrite raw files during preprocessing.

Dataset definitions and licensing: [dataset documentation](../docs/dataset.md).
