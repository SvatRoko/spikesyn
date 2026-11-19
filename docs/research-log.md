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

## 2026-11-19 - M01 exploratory filtering and epochs

Reviewed full-run/all-channel overview plots and one-second raw peak-to-peak
heatmap. Repeated frontal transients remain a quality concern; the largest
one-second window is Fp1 at 19-20 s (898 uV). Overview resolution does not support
a definitive artifact diagnosis. No amplitude-based exclusion is justified yet.

Implemented a tracked exploratory config and offline preprocessing command:
preserve the recorded reference and all channels, filter each run continuously
with an 8-30 Hz, 265-tap, zero-phase Hamming FIR, then extract [1,4) s imagery
windows without baseline subtraction or resampling. The filter has 2/7.5 Hz
transition widths and 0.825 s half-support. These are provisional choices, not
a frozen evaluation protocol; reasons and limits are in m01-preprocessing.md.

Observed output: 14 x 64 x 480 samples, 7 left and 7 right. The final left trial
(cue 120.4 s, S001R04-a29) is excluded because its epoch would require reflected
run-end data for FIR support. All 15 candidates and explicit reasons are retained
in the local trial ledger. Balanced counts are incidental, not a selection goal.
No artifact exclusions are performed. Retained filtered epochs still reach
401.83 uV peak-to-peak; band-pass filtering does not establish artifact removal.

Generated local epochs, trial identities/labels, filter coefficients, effective
configuration, source/config hashes, versions and quality/comparison plots.
Raw EDF checksum remained unchanged. Reviewed the filter-response and measured
spectral comparison. Outputs stay ignored; only code/config and text findings
are tracked.

Validation: 37 offline tests passed. New tests check passband amplitude/phase,
out-of-band attenuation, FIR symmetry, exact half-open sample/label alignment,
raw immutability, invalid configs, task and filter-support boundary exclusions,
and repeated export arrays/identities. Ruff lint/format, offline package build
and Git whitespace checks passed. Synthetic fixtures were shared across tests.

Initial single-recording M01 now has the required working processing foundation.
Limitations: noncausal filtering can mix neighboring task/rest activity; frontal
contamination persists; no reference/artifact policy is frozen for M02. Before
model work, review those choices with the owner and define an evaluation protocol
that discloses S001's exploratory use. No classifier or future engine was added.
