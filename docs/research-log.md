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

## 2026-11-19 - Initial M01: verified S001R04 inspection

Implemented separate fetch and offline inspect commands. Added MNE, NumPy, SciPy
and Matplotlib with locked versions. The EDF matches PhysioNet's published SHA-256;
original bytes and retrieval provenance remain ignored. The report includes channel
name mapping, annotation timing/counts, channel amplitudes, versions and inspector
source hash. Generated central traces and full-run Welch spectra remain local.

Observed: 64 EEG channels, 160 Hz, 20,000 samples, 125 s. T0/T1/T2 counts are 15/8/7.
Imagery intervals last 4.1 s; [124.5,125.0) s is unannotated. All samples are finite
and no channel is entirely flat. All EEG header units are uV; MNE returns volts.
The EDF lacks a montage; normalized names match colin27_1005 template positions.

Quality observations: frontal excursions reach about 971 uV peak-to-peak in Fp1;
PSD has a narrow 60 Hz peak and prominent low frequencies. No artifact cause is
established, no exclusions are made, and no decoding performance is inferred.
Visual review covered the generated central-channel first-20-second trace plot
and the full-run spectral summary, not all channels throughout the recording.

Decisions: preserve signals and existing reference, report unannotated data rather
than assigning rest, and keep 8-30 Hz provisional. Welch uses four-second Hann
windows, 50% overlap and constant segment detrending for descriptive density only.
MNE 1.13 deprecated the standard_1005 alias; use colin27_1005 explicitly. Initial
JSON export encountered a NumPy integer; explicit conversion and a serialization
test now cover that path. See m01-s001r04-inspection.md for the full observations.

Validation: 19 offline tests passed, including synthetic signal/annotation failures,
unit and spectral scaling checks, and mocked retrieval integrity/preservation.
Ruff lint/format passed; source distribution and wheel built. Real-recording
inspection completed and source checksum remained unchanged. Git ignore checks
confirmed the EDF, provenance manifest and all generated outputs are excluded.

Limitations/next step: M01 is not complete. Review full-run channel quality and
propose reference/channel/filter/epoch policies before implementing preprocessing.
No classifier, SNN, artifact correction, epoch extraction or command interface was
implemented in this batch.
