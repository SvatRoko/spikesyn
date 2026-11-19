# M01: exploratory filtering and epoch extraction

Date: 2026-11-19. This implements the single-recording exploratory M01 pipeline.
It is not a frozen M02 evaluation protocol and provides no decoding evidence.
The owner must review substantive protocol choices before final modeling.

## Full-run quality review

Generated and visually reviewed all-channel/full-run waveform overviews (four
pages of 16 channels), a channel-by-time heatmap of nonoverlapping one-second
peak-to-peak amplitudes, and the raw-versus-filtered spectral comparison. The
heatmap color cap of 500 uV is a display choice, not an exclusion threshold.
Waveforms share a symmetric scale determined from the recording's maximum absolute
amplitude (600 uV for this recording). No data are clipped for processing.
Overview plots compress time and are not a substitute for detailed artifact review.

Repeated frontal transients are visible. The largest one-second excursion is
898 uV at Fp1 in [19,20) s; Fp2 reaches 880 uV in the same second. Other prominent
frontal windows occur around 33, 56 and 77 s. These observations are compatible
with artifact contamination, but the plots do not establish its cause. No channel
is discarded solely on this basis. No ICA, interpolation, learned correction or
amplitude-based trial rejection is applied.

## Provisional configuration and reasons

Tracked configuration: [configs/m01-exploration.json](../configs/m01-exploration.json).

| Choice | Setting and rationale |
| --- | --- |
| Channels | All 64 EEG channels; avoid premature selection and retain frontal quality evidence |
| Reference | Preserve recorded signals; do not introduce a new reference before comparison/review |
| Passband | 8-30 Hz, the initial project proposal for mu/beta exploration; not proven optimal |
| FIR design | 265 taps, Hamming window, firwin, zero phase; explicit 2 Hz low and 7.5 Hz high transitions |
| Filtering scope | Continuous single run, before epoching; never concatenate runs |
| Boundary handling | reflect_limited for continuous output; exclude epochs whose FIR support needs reflected data |
| Epoch | Half-open [1,4) s after T1/T2 onset; avoid the first second and remain within observed 4.1-second tasks |
| Baseline and detrending | None on epochs; explore ongoing oscillations without evoked baseline subtraction |
| Resampling | None; retain 160 Hz |
| Artifact exclusions | None by amplitude; preserve the unresolved contamination issue explicitly |

These are engineering and exploratory research choices, not empirical evidence
that the settings are best. The 1-second onset exclusion is a provisional attempt
to reduce cue-onset influence, not proof that all cue effects are absent. Keeping
the recorded reference does not assert that its physiological definition is known
or optimal. An additional 60 Hz notch was not introduced because 60 Hz is already
outside the exploratory passband; no comparison of notch strategies was performed.

The symmetric FIR has 132 samples (0.825 s) of support on each side. Its zero-phase
application is noncausal and cannot support a live-operation claim. Continuous
filtering can mix activity from adjacent rest/task periods even when extracted
epoch samples lie within a task. Artifact transients can also spread through
filtering. Do not interpret these epochs as temporally isolated, artifact-free
imagery. The filtering policy must be reviewed before evaluation.

MNE includes the epoch endpoint by default. Passing tmax = 4 - 1/160 = 3.99375 s
implements [1,4) exactly: 480 samples per three-second epoch. Trial identities,
original annotation indices, onset samples, class labels and exclusions are saved.
No T0 or unannotated tail is assigned an imagery label.

## Actual output and exclusions

The run contains 15 imagery annotations. The pipeline retains 14 epochs with
shape **(14 trials, 64 channels, 480 samples)**: 7 T1/left and 7 T2/right.

Exactly one candidate is excluded: S001R04-a29, the final T1 annotation at 120.4 s
(event sample 19264). Its proposed [121.4,124.4) s epoch would require samples past
the recording's end when applying the FIR. The reason is explicitly stored as
insufficient_real_data_for_fir_support. The balanced retained counts are a
consequence of the boundary rule, not a balancing target or performance selection.
There are no additional annotation-duration or amplitude exclusions in this run.

Across retained windows, the maximum raw channel peak-to-peak amplitude is 799 uV.
After filtering, the maximum is about 401.83 uV, in trial S001R04-a15 (T1 cue at
62.3 s). These maxima need not correspond to the same channel/trial. Their reduction
does not establish artifact removal. An artifact policy remains a required topic
for M02 protocol review.

## Reproduction and outputs

From the repository root after syncing and fetching S001R04:

```powershell
uv run --offline --locked python -m spikesyn.preprocessing
uv run --offline --locked pytest
```

Optional flags: --recording, --config, --output. The source recording must match
the pinned S001R04 checksum. Generated files stay under ignored
results/m01-s001r04/preprocessing/ by default:

- preprocessing.json: effective config, policies, source/config hashes, versions,
  full imagery trial ledger, exclusion reasons and descriptive quality summaries.
- epochs.npz: X_v in volts, y (1 = left, 2 = right), times_s, channel_names,
  event_samples, annotation_indices and stable trial_ids. Load with
  numpy.load(..., allow_pickle=False); X axes are trial, channel, time.
- filter-taps.npy and filter-comparison.png: exact coefficients and measured/design
  response review.
- quality-review/: four full-run channel overviews, amplitude heatmap and its NPZ.

Rerunning replaces generated files. The original EDF remains byte-identical;
checksum verification occurs before and after processing. No network is accessed.
The config and source hashes distinguish exploratory variants; retain separate
output directories when comparing configurations.

## Validation and limits

Synthetic tests establish exact sample alignment, class/trial preservation, FIR
symmetry, passband phase/amplitude preservation, out-of-band attenuation, raw-data
immutability, config failures, incomplete-task exclusions and recording-edge guards.
An export integration test verifies labels/identities and exact repeated numerical
arrays. The real run and plotted comparison were also checked. These tests validate
implementation behavior, not physiological signal quality or decoding efficacy.

Initial M01 exploration now has a working, documented preprocessing path. Do not
start model training automatically: review the provisional settings and unresolved
artifact/reference policy, then define and freeze the M02 evaluation configuration.
S001 has influenced exploration and must be disclosed as such in later results.
