# Initial dataset

The planned source is PhysioNet EEG Motor Movement/Imagery Dataset (EEGMMIDB),
version 1.0.0, by Gerwin Schalk (2009), DOI
[10.13026/C28G6P](https://doi.org/10.13026/C28G6P).
The [official dataset page](https://physionet.org/content/eegmmidb/1.0.0/)
describes 109 participants, 64 EEG channels, 160 Hz sampling, EDF+ recordings,
and task annotations. These are source expectations, not local observations.

For imagined unilateral fist movements, use runs 4, 8, and 12 only:

| Annotation | Meaning in these runs | Initial binary task |
| --- | --- | --- |
| T0 | Rest | Excluded from target labels |
| T1 | Imagined left fist | Left |
| T2 | Imagined right fist | Right |

Annotation meanings depend on the task/run. Do not reuse this mapping for other
runs. Begin exploration with S001R04; a single recording cannot support a
run-held-out comparison. Validate actual files rather than assuming every
recording matches nominal metadata. See the protocol for validation requirements.

Use a supported MNE EEGBCI loader or direct official download in M01. Record the
exact retrieval command, source version/URL, download time, checksum and local
path. Keep original files intact and out of Git. Check dataset usage terms before
redistribution; the official page currently lists Open Data Commons Attribution
License v1.0. The dataset license is separate from Spikesyn's undecided license.

No EEG has been downloaded or inspected in M00. Counts, duration, signal quality,
and channel locations remain unverified locally. Cite the dataset and the
associated publications requested by PhysioNet when reporting experiments.
