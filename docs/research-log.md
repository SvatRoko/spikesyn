# Research log

## 2026-11-19 - Restart and M00 foundation

Question: what minimum foundation supports reproducible EEG exploration without
prematurely implementing the full research roadmap?

Decisions: retain About.md as the master specification. Establish a src-layout
package, Python 3.11, uv lockfile, pytest and Ruff. No runtime scientific
libraries are required yet. Keep data and generated outputs ignored. Create the
first GitHub repository privately because the software license is undecided.

Protocol: separate S001R04 exploration from later run-held-out evaluation. Keep
filter/epoch/artifact choices provisional. Record leakage controls and uncertainty
questions before modeling. No EEG has been retrieved and no scientific result
has been observed. Primary sources are recorded in sources.md.

Environment observation: initial uv managed-Python download failed certificate
validation (UnknownIssuer). Retried using uv's system certificate store, without
disabling certificate verification. Validation results will be recorded below.

Limitations: installation tests do not validate EEG loading or signal processing.
The cohort, preprocessing choices, uncertainty method and software license are
unresolved. No literature review or efficiency comparison has been completed.

Next bounded batch after M00: retrieve and inspect S001R04, validating provenance,
metadata and task annotations before selecting preprocessing parameters.

### M00 validation

Environment: Windows, CPython 3.11.18, uv 0.13.9, pytest 9.2.0, Ruff 0.17.6.
Locked sync succeeded. Package import succeeded. Offline pytest: 2 passed.
Ruff lint and format checks passed. Source distribution and wheel built successfully.
Git ignore checks confirmed sample raw/derived data, figures, environment and build
artifacts are excluded. No raw EEG or generated results are staged.

The first metadata test failed because the build backend reordered the equivalent
Requires-Python constraints. Corrected the test to compare constraint sets, then
reran the checks successfully. This was a test assumption, not a package defect.
No scientific tests or experiments have been run; M00 validates packaging only.

## 2026-11-19 - MIT license and public repository

The owner selected the MIT License and made the GitHub repository public.
Added LICENSE, declared MIT in package metadata, and updated current licensing
notes. This resolves the software-license question recorded above; the earlier
entries retain the historical M00 decisions. EEGMMIDB licensing remains separate.
