# M02-P01: proposed conventional baseline protocol

Version 0.1, 2026-11-19. Status: proposed, pending owner review through this PR.
Merging the protocol PR accepts this design; implementation and cohort execution
remain separate bounded tasks. No classifier, dataset expansion or evaluation has
been performed in this batch. This is a local prospective plan, not an externally
registered study or evidence of scientific novelty.

Machine-readable decisions: [m02-protocol.json](../configs/m02-protocol.json).
This document defines policy semantics; the existing M01 CLI does not enforce all
of these new requirements. Do not pass the complete protocol JSON to that CLI.

## Question and stages

Can a fixed CSP + LDA pipeline distinguish the dataset's imagined left/right fist
conditions on a held-out recording run? This measures condition discrimination,
not proof that predictions originate exclusively from neural motor imagery.

1. Development: S001, runs 4/8/12. Establish end-to-end correctness and inspect
   failures. S001R04 has already influenced exploration; all S001 results are
   development findings, even with a run held out. Do not call them confirmatory.
2. Planned cohort: S002-S011, all three runs each. The ten IDs are selected in
   numerical order before performance is observed, not for expected quality.
   Cohort retrieval/execution needs separate owner authorization after the
   development implementation is validated. No unlisted substitute participants.

Before cohort execution, freeze protocol/config hash, code revision and locked
environment. If development reveals a defect or changes are needed, document a
new protocol version and its reason before cohort evaluation. Never quietly reuse
cohort results to select settings. The cohort is a small convenience sample;
there is no claim it represents the whole dataset or a broader population.

## Primary preprocessing and artifact policy

Keep M01's 160 Hz sampling, all 64 EEG channels, and recorded reference. Use
8-30 Hz zero-phase FIR, 265 Hamming/firwin taps, 2 Hz lower and 7.5 Hz upper
transition widths, filtering each continuous run independently. No run joins,
resampling, baseline subtraction, ICA, interpolation, scaling or projections.

Change the primary epoch to **[1,3) s**, exactly 320 samples. This is a prospective
design choice based on filter support and annotation timing, not classifier scores.
With 132-sample half-support, its conservative envelope is [0.175,3.825) s relative
to the cue. It fits the observed 4.1-second imagery intervals. Other recordings
must be checked; do not assume all annotations have that duration. MNE's inclusive
endpoint must be expressed as tmax = 3 - 1/160 = 2.99375 s.

An eligible trial must have both its extracted samples and its full FIR support
inside its own T1/T2 annotation and inside the real recording. Exclude and record
any violation. Annotation start/end and sample-grid checks must use an explicit
numerical tolerance. Source bytes/checksums, original and normalized names, labels,
run/subject identities and annotation indices must be preserved. Reject malformed
metadata, unexpected annotation meanings, nonfinite samples, preexisting marked
bad channels/projections or missing required channels; never silently repair them.

The primary artifact policy is deliberately **no automatic correction and no
amplitude rejection**. This defines an uncorrected benchmark and avoids inventing
a threshold from S001's excursions. It does not resolve the contamination found
in M01. Report raw and filtered amplitude summaries and retained/excluded counts
by run and class. Artifacts inside an eligible task can still affect features;
task containment does not make signals clean or exclude cue-related effects.

The recorded reference remains physiologically unverified locally. Do not silently
replace it with average reference. Any later rereferencing is a versioned analysis
change with rank and bad-channel consequences, not a repair applied after seeing
accuracy. Offline noncausal processing provides no live-feasibility evidence.

## Fixed model and leakage controls

For each participant, create three outer folds: hold out run 4, 8 or 12 and train
on the other two. A run is wholly training or wholly evaluation in each fold.
Keep trial IDs and subject/run groups in every output; each retained trial receives
one out-of-fold prediction. Never use a random trial/window split as a substitute.

Fit one fresh scikit-learn Pipeline per fold:

- MNE CSP: 4 components; covariance shrinkage 0.1; concatenated class covariance;
  log average-power features; no trace normalization; rank estimated from training
  data; restricting subspace transform; mutual-information component ordering.
- LDA: lsqr solver, automatic shrinkage, fixed equal class priors [0.5,0.5].

These are prespecified regularized starting settings, not validated optima.
No hyperparameter search or feature selection is planned. Automatic LDA shrinkage
and CSP rank/covariance estimates must be computed only during training fit.
Apply the trained CSP unchanged to the held-out run. No test-run means, covariance,
labels or score may influence any fitted operation. Fixed per-run filtering has
no learned parameters. Any proposed tuning needs a new protocol and training-only
validation respecting runs; the outer test run remains excluded.

Both classes must exist in training and evaluation. Rank must support four CSP
components. A missing run, invalid data, empty/one-class fold, insufficient rank or
numerical fit failure makes that participant's primary three-fold result incomplete.
Record the failure and any available fold diagnostics, without silently averaging
only successful folds, changing components or replacing the participant.

## Metrics, comparison and uncertainty

Primary participant score: arithmetic mean of the three held-out-run balanced
accuracies, equally weighting runs. Primary cohort score: arithmetic mean of the
ten complete participant scores, equally weighting participants. Balanced accuracy
is unadjusted mean per-class recall, with class order [1 left,2 right].

Also report fold/participant accuracy, confusion matrices (rows true, columns
predicted), per-class recall, train/test class counts, trial IDs, exclusions and
one out-of-fold prediction per retained trial. Summed confusion matrices and pooled
trial metrics are descriptive; do not substitute them for the primary run/subject
weighted scores. Preserve all failures and negative or below-chance findings.

Fit a training-majority DummyClassifier within each fold and evaluate it on that
same held-out run. Use deterministic class ordering for majority ties. Its balanced
accuracy is 0.5 when both test classes are present, while raw accuracy depends on
imbalance. Uniform guessing has expected balanced accuracy 0.5; neither reference
is an observed Spikesyn model result. Slightly exceeding 0.5 establishes nothing
by itself. Do not use a trial-independent binomial test on dependent EEG trials.

For S001, show all three fold scores and their min/max range. Do not treat three
overlapping-training folds as independent replicates or publish a confidence
interval/p-value from them. This pilot does not support participant-population
uncertainty claims.

For the planned complete ten-person cohort, use 20,000 seeded bootstrap samples
of participant IDs with replacement (seed 20261119). Each draw resamples complete
participant scores, retaining the three-fold aggregation; never independently
resample folds or pooled trials. Report the 2.5th/97.5th percentiles of cohort
means as an exploratory 95% participant-bootstrap interval, stating exchangeability
and small convenience-sample limitations. It does not account for protocol choice
or all training uncertainty. If any planned participant is incomplete, report
the full failure table and descriptive complete-case results but omit this planned
cohort CI and mark the primary cohort analysis incomplete. Do not backfill IDs.
No confirmatory significance test or permutation p-value is planned.

## Prespecified sensitivity analysis

Repeat the same folds and model settings on nine anatomically selected central
channels: FC3, FCz, FC4, C3, Cz, C4, CP3, CPz, CP4. Keep the recorded reference and
exact primary trial set; selecting channels must not hide a malformed required
recording or change exclusions. Present paired participant differences descriptively
alongside both scores. This is a secondary analysis, not a search for a winning
pipeline or proof that eye/muscle artifacts are eliminated. Do not promote it to
primary after scores are known. Other windows, references and component counts
are outside M02-P01 and require a versioned follow-up.

## Implementation acceptance criteria

Future implementation must add supported retrieval/provenance for the authorized
runs, enforce task-contained FIR support, and export subject/run/trial identities.
Existing M01 outputs/config remain a separate exploratory reference, not overwritten
as though these new windows had always been used. Offline tests must verify:

- Exact sample/label alignment and all task/run-support exclusions.
- Complete run separation and exactly one out-of-fold prediction per trial.
- Train-only CSP/LDA fitting, including invariance of fitted parameters when
  held-out labels or values change, tested with controlled synthetic fixtures.
- Primary aggregation, class order, incomplete-fold failures and chance baseline.
- Deterministic participant bootstrap and exported prediction/manifest contracts.

Record protocol ID/hash, source revision, software/hardware, seeds, dataset file
hashes, effective model parameters and failures with each experiment. Keep raw
recordings and generated results outside Git; tests must not fetch EEG.

## Primary implementation references

These sources specify APIs, not the optimal scientific choices for Spikesyn:

- [MNE CSP](https://mne.tools/stable/generated/mne.decoding.CSP.html).
- [scikit-learn LDA](https://scikit-learn.org/stable/modules/generated/sklearn.discriminant_analysis.LinearDiscriminantAnalysis.html).
- [LeaveOneGroupOut](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.LeaveOneGroupOut.html).
- [Balanced accuracy](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.balanced_accuracy_score.html).

## Checks performed while drafting

Parsed the proposed JSON and used its preprocessing parameters with the existing
M01 numerical helper on the verified S001R04 recording. Observed shape:
(15,64,320), with 8 left and 7 right trials; all retained filter-support envelopes
were inside their task annotations. This is a geometry/feasibility check only,
not an implementation of the new M02 enforcement policy, a classifier test or
evidence of predictive performance. The ignored local diagnostic is
results/m02-protocol-feasibility.json. M01's config and outputs remain unchanged.

All 41 existing offline tests, Ruff lint/format and whitespace checks passed.
No new runtime dependency was installed and no other EEG run was retrieved.
