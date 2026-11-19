# Research plan

## Question and hypotheses

Can an SNN decode imagined left versus right fist movement from EEG competitively
with CSP + LDA, and what differences arise in accuracy, inference latency, model
complexity, and computational activity?

- H1: CSP + LDA can extract discriminative information for this task.
- H2: A simple SNN can perform above an appropriate chance baseline.
- H3: The approaches exhibit different computational trade-offs.

These are untested hypotheses. SNN accuracy or energy superiority is not assumed.
Spike counts alone do not measure energy; actual claims require hardware
measurements or a justified model with explicit limitations.

## Milestone gates

| Milestone | Scope | Exit evidence |
| --- | --- | --- |
| M00 | Environment and research foundation | Locked install, package import, offline checks, protocol and log |
| M01 | EEG exploration and preprocessing | Validated metadata/events, reproducible figures/epochs, tests and documented choices |
| M02 | CSP + LDA baseline | Run-held-out evaluation, uncertainty and transparent report |
| M03 | Simple SNN and comparison | Matched splits, documented representation differences and measured trade-offs |
| M04 | Recorded-data command demonstration | Reproducible playback, uncertainty handling and qualified capabilities |

Only M00 is authorized for this implementation batch. Do not scaffold future
engines, add their dependencies, or interpret installation tests as EEG evidence.

## Open scientific decisions

M01 must investigate referencing, channel selection, filter design and boundary
handling, epoch windows, baseline correction, and artifact policies. Approximately
8-30 Hz is a proposal from About.md, not a validated optimum. Record decisions and
reasons before applying them to evaluation data. Major methodological decisions
require owner review. Choose the cohort, tuning strategy, and uncertainty procedure
before expanding M02; do not select participants based on favorable accuracy.

A useful outcome includes a conventional baseline outperforming the SNN or no
convincing decoding evidence. Preserve those findings and all disclosed protocol
changes. This project makes no clinical or unrestricted thought-reading claims.
