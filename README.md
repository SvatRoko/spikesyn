# Spikesyn

Spikesyn is a research-oriented Python project investigating EEG motor-imagery
decoding and, in later milestones, spiking neural networks. The long-term question
is whether an SNN can compete with a CSP + LDA baseline and what computational
trade-offs emerge. No decoding results or functional BCI are available yet.

## Current scope

M00 is complete. Initial M01 retrieves and inspects Subject 001, Run 04 of
EEGMMIDB, with reproducible quality plots, exploratory filtering/epochs, and validation.
Classifiers, SNNs, commands, interfaces, cloud infrastructure, and live acquisition
are outside this batch. See [About.md](About.md) for the full roadmap.

## Setup on Windows PowerShell

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then run:

```powershell
uv python install 3.11
uv sync --locked
uv run --locked python -c "import spikesyn; print(spikesyn.__doc__)"
```

The project currently supports Python 3.11 only. `.python-version` selects that
minor series; `uv.lock` pins Python package dependencies. Record the exact Python
patch version for experiments. Setup requires network access; tests do not.
If uv is installed through pip and is absent from PATH, use `python -m uv` in
place of `uv`. On systems using a trusted enterprise certificate, uv supports
`--system-certs`; do not disable TLS verification.

## Development checks

After syncing, these checks require no network or EEG downloads:

```powershell
uv run --offline --locked pytest
uv run --offline --locked ruff check .
uv run --offline --locked ruff format --check .
```

Create a distributable with `uv build`. M01 uses MNE-Python, NumPy, SciPy and
Matplotlib. Tests use synthetic signals and mocked downloads; real-recording
inspection is a separate command.

## M01: retrieve and inspect S001R04

From the repository root, after `uv sync --locked`:

```powershell
uv run --locked python -m spikesyn.inspection fetch
uv run --offline --locked python -m spikesyn.inspection inspect
```

`fetch` retrieves only the official S001R04 EDF and checks its published SHA-256.
It never replaces an existing recording; a checksum mismatch is an error.
`inspect` needs no network. It validates metadata and events and produces a JSON
report, central-channel traces and a Welch spectrum, without altering raw signals.
The original file and retrieval manifest remain under ignored `data/eegmmidb/`;
reports and figures remain under ignored `results/m01-s001r04/`. Existing generated
reports are replaced when inspection is rerun. Optional `--recording` and `--output`
flags accept local paths; `--recording` still requires the exact S001R04 checksum.

See [inspection findings](docs/m01-s001r04-inspection.md). To run the provisional
preprocessing pipeline and regenerate the full-run quality review:

```powershell
uv run --offline --locked python -m spikesyn.preprocessing
```

It currently produces 14 epochs of 64 channels by 480 samples (7 left, 7 right),
with one recording-edge exclusion. Results stay in ignored
`results/m01-s001r04/preprocessing/`. Configuration lives in
[configs/m01-exploration.json](configs/m01-exploration.json); see
[settings, exclusions and limitations](docs/m01-preprocessing.md). This completes
the initial single-recording M01 pipeline. Artifact/reference policy and final
evaluation settings still need review before M02; no classifier exists yet.

## Research documentation

- [Research plan](docs/research-plan.md): question, hypotheses, scope, gates.
- [Dataset](docs/dataset.md): provenance and task interpretation.
- [Preliminary protocol](docs/experiment-protocol.md): exploration and evaluation.
- [Research log](docs/research-log.md): decisions, validation, limitations.
- [Sources](docs/sources.md): primary references and their relevance.
- [M01 protocol review](docs/m01-protocol-review.md): findings, fixes and M02 gates.
- [Proposed M02 protocol](docs/m02-evaluation-protocol.md): fixed baseline and evaluation design.
- [Data handling](data/README.md) and [outputs](results/README.md).

## Branch workflow

Use a short-lived branch for each bounded task and submit changes through a pull
request. Keep `main` stable. PRs describe behavior changes, validation and scientific
limitations; run the offline checks above before review. Leave merging to an
explicit owner decision. This workflow is a project convention, not a claim that
GitHub branch protections or automated CI are already configured.

## License

Spikesyn is open source under the [MIT License](LICENSE). The repository is public.
EEGMMIDB data retain their separate dataset licensing terms; see the
[dataset documentation](docs/dataset.md).
