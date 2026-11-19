# M01: S001R04 retrieval and inspection

Date: 2026-11-19. Status: initial M01 inspection complete; preprocessing is pending.
This is descriptive exploration, not a classification experiment.

Follow-up: the [exploratory preprocessing pipeline](m01-preprocessing.md) has now
been implemented. The next-step and pending-work statements below describe the
state at the initial inspection, before that follow-up.

## Provenance and reproduction

Source: [official EDF](https://physionet.org/files/eegmmidb/1.0.0/S001/S001R04.edf),
EEGMMIDB v1.0.0. Retrieved with Python urllib over verified HTTPS. The 2,596,896-byte
file matched the entry in the [official checksum list](https://physionet.org/files/eegmmidb/1.0.0/SHA256SUMS.txt):

```text
3d161f88e1c00632585287d2ce584c2bc0f08862438eb255ea8723e00fac693d
```

From the repository root:

```powershell
uv sync --locked
uv run --locked python -m spikesyn.inspection fetch
uv run --offline --locked python -m spikesyn.inspection inspect
```

The fetch step preserves an ignored provenance manifest beside the EDF, including
retrieval UTC timestamp, URL, checksum and size. The inspector checks the pinned
checksum before loading and after plotting. An existing recording is never
replaced; a corrupt file produces an error. Inspection does not access the network.

Outputs under ignored results/m01-s001r04/: inspection.json (metadata, annotations,
name mapping, per-channel summaries, library versions and inspector source hash),
raw-central.png, welch-psd.png and welch-psd.npz. The NPZ stores frequencies in Hz
and spectral density in V^2/Hz. These generated files are not tracked in Git.

Observed environment: Python 3.11.18, MNE 1.13.2, NumPy 2.4.6, SciPy 1.17.1,
Matplotlib 3.11.2. Exact dependencies are in uv.lock.

## Observed metadata and annotations

| Item | Observed value |
| --- | --- |
| EEG channels | 64 |
| Sampling rate | 160 Hz |
| Samples per channel | 20,000 |
| Recording duration (samples / rate) | 125.0 s |
| Last sample time | 124.99375 s |
| T0 rest annotations | 15 |
| T1 imagined left-fist annotations | 8 |
| T2 imagined right-fist annotations | 7 |
| Imagery annotation duration | 4.1 s each |
| Rest annotation duration | 4.2 s each |
| Final unannotated interval | [124.5, 125.0) s |

All EEG samples are finite; no channel is entirely flat. Annotation intervals
are ordered, nonoverlapping and within recording bounds. Counts describe annotated
periods, not extracted epochs: no trials have been accepted or rejected yet.
The duration is 125 seconds; do not hard-code a nominal two-minute length.

Raw names include padding and dataset capitalization (e.g., C3.. and Fc5.).
Normalization on an in-memory copy maps these to C3 and FC5. All 64 normalized
names match MNE's colin27_1005 template. The EDF provides no montage; template
coordinates are not measured participant electrode locations. Original names
remain in the input and their mapping is recorded in the local report.

MNE loads EEG amplitudes in volts; summary statistics and trace plots convert to
microvolts. Direct header inspection found uV as the EEG physical dimension (the
annotation signal uses a different marker). Loader highpass/lowpass metadata are
0/80 Hz; these values do not independently establish acquisition filter settings.
No filter or reference change has been applied by Spikesyn.

## Signal observations and limitations

The first-20-second C3/Cz/C4 traces show substantial shared slow variation. Whole-run
channel standard deviations range from about 24.92 to 83.06 uV. Fp1 has the largest
peak-to-peak excursion, about 971 uV, followed by Fp2 at 880 uV. These are descriptive
quality flags, not proof of a particular artifact source or a basis for automatic
trial/channel exclusion. Finite and nonflat signals do not establish clean EEG.
Only central channels in the first 20 seconds have been visually inspected here;
full-run all-channel artifact review remains pending.

Welch spectra use 640-sample (4 s) periodic Hann windows, 320-sample overlap,
constant detrending, mean segment averaging and density scaling. Frequency spacing
is 0.25 Hz. The full-run central spectra and channel median show dominant low
frequencies and a narrow peak at 60 Hz. A feature near 13 Hz is visible in C3, but
this analysis pools rest and imagery and cannot establish task-specific mu/beta
modulation or class separability. The 8-30 Hz region is highlighted only; it is
not a selected or applied filter. PSD detrending occurs inside the estimator and
does not alter the raw recording.

The class counts are slightly imbalanced (8 versus 7). The final 0.5 seconds must
remain unlabeled rather than being silently treated as rest. No epochs, filtering,
rereferencing, artifact corrections, model inputs or decoding metrics were produced.
No scientific conclusions generalize beyond this recording from these checks.

## Validation and next bounded task

Synthetic offline tests check metadata failures, finite amplitudes, annotations,
label meanings, name/data preservation, microvolt conversion, spectral peak and
integrated density scaling. Mocked-download tests check checksum enforcement and
preservation of existing recordings/provenance. These checks complement the real
EDF inspection; they do not prove the data are artifact-free.

Next: review full-run channel quality, then propose and document the reference,
channel policy, filter design and epoch window. The observed 4.1-second imagery
intervals constrain candidate windows. Validate boundary behavior and synthetic
signal invariants before producing preprocessed epochs. Any exclusions require
recorded reasons. M01 remains incomplete until that processing work is validated.
