# M01 protocol and implementation review

Date: 2026-11-19. Branch: research/m01-protocol-review. Reviewed base: faf4309.
Scope: S001R04 validation, quality summaries, filtering, epochs, exports, tests and
the transition gate toward M02. No classifier was implemented.

## Verdict

Qualified pass for initial M01 exploration. Verified acquisition, explicit labels,
reproducible filtering, exact sample alignment, immutable raw data and an auditable
trial ledger provide a useful processing foundation. This does not establish clean
neural signals, motor-imagery separability or a final evaluation protocol.

Two implementation defects were fixed on this branch. Real-recording epoch arrays
remain exactly equal to those generated before review: 14 x 64 x 480, 7 left and
7 right. None of the exploratory settings or exclusion rules changed.

## Findings, ordered by consequence

### R1: Filtered samples contain neighboring-task context

Scientific limitation, still requires protocol review before M02. Stored epoch
bounds do not describe all data influencing the samples. The symmetric FIR extends
132 samples each way. Relative to the cue, the [1,4) s epoch has a conservative
half-open support envelope [0.175,4.825) s. Each imagery annotation lasts 4.1 s,
so the envelope extends 0.725 s past it.

All 14 retained S001R04 epochs have this condition; the next annotation is rest.
This is expected noncausal filtering behavior, not proof of cross-fold leakage:
filtering runs independently before a whole-run holdout does not itself mix
training and held-out runs. It limits claims that features reflect only imagery;
a rest-period transient may affect the epoch. See [MNE filtering background](https://mne.tools/stable/auto_tutorials/preprocessing/25_background_filtering.html).

Added per-trial filter-support bounds and before/after-task context to the ledger.
A synthetic impulse in the following rest period changes the first epoch; an
impulse beyond its support does not, within numerical tolerance. These diagnostics
do not introduce exclusions.

Recommendation: retain this config as an exploratory reference. Before M02,
explicitly accept contextual filtering for an offline benchmark or define a
task-contained window/filter policy. Do not choose a replacement using held-out
accuracy. No alternative configuration was optimized in this review.

### R2: Artifact and reference choices are not frozen

Unresolved scientific decision. Repeated frontal excursions and a retained filtered
peak-to-peak amplitude around 402 uV warrant investigation. A global maximum does
not establish artifact identity or a threshold. There is no independent EOG
confirmation; this is not a physiological cleanliness assessment. Spectral
reduction does not establish artifact removal.

Keeping the recorded reference avoids an undocumented transformation, but its
physical definition has not been established locally. Average rereferencing
changes signals and requires an explicit channel/bad-channel policy; it is not
a default repair. See [MNE reference guidance](https://mne.tools/stable/auto_tutorials/preprocessing/55_setting_eeg_reference.html).

Recommendation: decide whether the primary baseline intentionally uses uncorrected
data or an explicit artifact policy. Prespecify channels, reference, exclusions and
sensitivity analyses, keeping counts/reasons by class and run. Learned thresholds
or corrections must use training data only. The pipeline refuses preexisting bad
channels/projections rather than silently deciding their handling. General BAD
annotation support and artifact correction are not implemented. See [MNE bad-span guidance](https://mne.tools/stable/auto_tutorials/preprocessing/20_rejecting_bad_data.html).

### R3: Sub-sample annotation overlaps and overruns were accepted

Implementation defect, fixed. The previous one-sample tolerance accepted a start
0.003 s before the recording, a 0.003 s overlap, or an end 0.003 s beyond recording
bounds. It also hid gaps smaller than one sample. This contradicted the stated
continuous-time bounds/nonoverlap contract.

Replaced that allowance with 1e-8 s for floating-point comparisons, not as a claim
of measurement precision. Added regressions for small negative starts, overruns,
overlaps and reported gaps. S001R04 annotations pass unchanged.

### R4: Heatmap distorted partial final seconds

Implementation defect, fixed. A short final window was included but all image
columns were equally wide across the duration. A 9.5-second signal displayed ten
equal-width bins rather than nine one-second bins and one half-second bin.

Use a mesh with explicit sample-derived time edges and export start/stop times.
A regression checks exported intervals and plotting edges for a 9.5-second signal.
The 125-second S001R04 bin boundaries are unchanged; the regenerated heatmap was
visually inspected.

### R5: M02 requires a frozen evaluation plan

Planning gate, not a defect. Before benchmarking, record primary preprocessing and
artifact policies, CSP/LDA settings or training-only tuning, participant cohort,
uncertainty method and chance comparison. Keep subject-specific leave-one-run-out
outer splits. S001 informed exploration and must remain explicit development data
in reporting; do not describe later S001 results as untouched confirmation. Do not
expand the cohort based on favorable outcomes. No model performance is available.

## Verification

- 41 offline synthetic/mocked tests passed; Ruff lint and formatting passed.
- Real S001R04 processing passed with the original checksum unchanged.
- Every exported array exactly matches the pre-review run: amplitudes, labels,
  times, names, onset samples and trial identities.
- The last-trial exclusion is unchanged; 14/14 retained epochs now report their
  cross-task filter context. No amplitude or channel exclusions were introduced.
- Generated outputs remain local under ignored results/m01-protocol-review/.

Submit this review and fixes through a PR; leave main unchanged pending merge.
No branch-protection or automated CI guarantees have been configured by this work.
