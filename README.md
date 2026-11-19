# Spikesyn

Spikesyn is a research-oriented Python project investigating EEG motor-imagery
decoding and, in later milestones, spiking neural networks. The long-term question
is whether an SNN can compete with a CSP + LDA baseline and what computational
trade-offs emerge. No decoding results or functional BCI are available yet.

## Current scope

M00 establishes the environment, package, offline checks, and research protocol.
M01 will explore recorded EEG, beginning with Subject 001, Run 04 of EEGMMIDB.
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

Create a distributable with `uv build`. No runtime dependencies are needed in M00.
Add scientific dependencies only when their milestone requires them. Automated
tests must remain offline; future real-recording checks will be separate.

## Research documentation

- [Research plan](docs/research-plan.md): question, hypotheses, scope, gates.
- [Dataset](docs/dataset.md): provenance and task interpretation.
- [Preliminary protocol](docs/experiment-protocol.md): exploration and evaluation.
- [Research log](docs/research-log.md): decisions, validation, limitations.
- [Sources](docs/sources.md): primary references and their relevance.
- [Data handling](data/README.md) and [outputs](results/README.md).

## License

Spikesyn is open source under the [MIT License](LICENSE). The repository is public.
EEGMMIDB data retain their separate dataset licensing terms; see the
[dataset documentation](docs/dataset.md).
