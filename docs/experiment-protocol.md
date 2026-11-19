# Preliminary experimental protocol

Status: version 0.3, 2026-11-19. Initial S001R04 retrieval and descriptive
inspection have been executed; see [M01 findings](m01-s001r04-inspection.md).
A provisional filtering/epoch pipeline has now been executed; see
[M01 preprocessing](m01-preprocessing.md). Model evaluation remains unexecuted.

## M01 exploration

1. Retrieve S001R04 from EEGMMIDB v1.0.0; preserve provenance and checksum.
2. Load using MNE without modifying the original file. Inspect channel count,
   names/types, sampling rate, sample count/duration, units, finite values,
   channel locations, annotation onset/duration, and label counts.
3. Compare observed metadata against source expectations. Record discrepancies,
   corrections and exclusions explicitly. Preserve original-to-normalized channel
   name mappings and distinguish template locations from measured coordinates.
4. Regenerate raw traces and spectral summaries using documented commands.
5. Investigate the proposed 8-30 Hz band, reference, filter type/order/phase,
   padding and transients. Choose epoch start/end, endpoint convention, baseline
   and artifact policy after inspecting event timing. Record rejected trials and
   reasons. Do not silently replace missing or unexpected annotations.
6. Validate T1/T2 interpretation for the selected run, epoch labels and dimensions,
   sampling/units, and boundaries. Add deterministic synthetic tests for scientific
   invariants and failures. Real-data inspection is separate from offline tests.

Descriptive spectra use four-second Hann segments, 50% overlap, constant
detrending and density scaling. This detrending applies only inside the spectral
estimator, not to the stored signals. The plot highlights the proposed 8-30 Hz
band without applying a filter. Central traces show the first 20 seconds only.
Raw channel names are retained; normalized names and a colin27_1005 template
are checked on an in-memory copy. Template positions are not subject measurements.

No preprocessing choices or exploratory visual findings demonstrate successful
decoding. The exploratory window is [1,4) s and the filter is 8-30 Hz zero-phase
FIR. These settings are documented, tested proposals, not a frozen evaluation
protocol. No amplitude artifact threshold has been selected.

## Future M02 evaluation

First validate the procedure for one participant using runs 4, 8, and 12. Each
outer fold holds out one whole run and trains on the other two. Preserve run and
trial identifiers; never randomly split neighboring windows from the same trial
across training and evaluation. Process runs separately to avoid filtering across
run boundaries. Record any use of noncausal filtering; offline results do not
establish live feasibility.

Fit CSP, scaling, feature selection, learned artifact corrections and all other
trainable transformations on training data only. Use a pipeline. If tuning is
needed, use training-only validation with run grouping; never tune on the outer
test run. Freeze preprocessing, cohort, primary metric and tuning procedure before
expanded evaluation. Log changes and distinguish exploratory from confirmatory
analysis. S001 exploration means later S001 results need that caveat.

Report accuracy, balanced accuracy, confusion matrices, per-class recall, trial
counts, exclusions and each fold/participant result. Use balanced accuracy as the
provisional primary metric. Report class distributions and an appropriate chance
comparison. A result slightly above 50% is not sufficient evidence. Decide and
justify uncertainty estimates before evaluation, respecting dependent trials,
folds and participants; do not treat all pooled trials as independent subjects.

## Future comparison and experiment records

SNN experiments must use the same participants, labels and held-out runs as the
baseline. Disclose representation and preprocessing differences. Record experiment
ID, question, code revision, config, splits, seeds, exact software versions,
hardware, training settings, timing method, outputs, interpretation and limitations.
Measure latency with documented warm-up, batch size and device synchronization.
Keep spike activity distinct from energy consumption. Retain negative results.

No classifier, SNN, model tuning, command translation or live control is part of M00.
