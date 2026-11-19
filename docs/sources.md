# Primary sources

Checked 2026-11-19. This is a starter source register, not a completed literature
review. No model-performance findings have been extracted or reproduced.

- Gerwin Schalk (2009), EEG Motor Movement/Imagery Dataset, v1.0.0.
  https://physionet.org/content/eegmmidb/1.0.0/ ; DOI: 10.13026/C28G6P.
  Primary dataset documentation for acquisition, tasks, annotations and licensing.
  Supports planned metadata expectations; does not establish Spikesyn performance.
- MNE-Python, Motor imagery decoding from EEG data using the Common Spatial
  Pattern (CSP), official example, accessed 2026-11-19.
  https://mne.tools/stable/auto_examples/decoding/decoding_csp_eeg.html
  Implementation reference for future baseline work, not Spikesyn's evaluation
  protocol. Do not copy example splits or preprocessing without justification.
- Astral, uv: Locking and syncing, official documentation, accessed 2026-11-19.
  https://docs.astral.sh/uv/concepts/projects/sync/
  Reference for committed lockfiles and locked environment installation.

Before model development, expand the literature review with verified original
papers: authors/year, DOI, task/dataset, method, findings, limitations and relevance.

## M01 implementation references

- PhysioNet, EEGMMIDB v1.0.0 published checksums:
  https://physionet.org/files/eegmmidb/1.0.0/SHA256SUMS.txt
  Pins the integrity of S001/S001R04.edf. Checked 2026-11-19.
- MNE-Python, official EDF reader:
  https://mne.tools/stable/generated/mne.io.read_raw_edf.html
  Reference for loading EDF+ and embedded annotations.
- MNE-Python, EEGBCI channel-name standardization and standard montages:
  https://mne.tools/stable/generated/mne.datasets.eegbci.standardize.html
  https://mne.tools/stable/generated/mne.channels.make_standard_montage.html
  Name normalization and template-location checks, not measured coordinates.
  MNE 1.13 deprecates standard_1005 in favor of colin27_1005; the implementation
  uses the current name and requires MNE >=1.13. Checked 2026-11-19.
- SciPy, Welch spectral estimator:
  https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.welch.html
  Reference for segment overlap, detrending and V^2/Hz density scaling. This
  estimate describes spectra, not task discrimination. Checked 2026-11-19.
