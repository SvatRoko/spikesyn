# Generated outputs

Keep figures, metadata exports, experiment manifests, metrics, and models outside
Git. Everything here except this note is ignored. Include reproducible commands,
configuration, seeds, source revision, exact Python and dependency versions, and
hardware in local experiment records. Track scientific interpretation and
negative findings as text in docs, with identifiers referring to local outputs.

M00 produced no scientific outputs. Initial M01 writes inspection.json,
raw-central.png, welch-psd.png and welch-psd.npz under m01-s001r04/. Regenerate
with `uv run --offline --locked python -m spikesyn.inspection inspect` from the
repository root after fetching the recording. These are descriptive inspection
outputs, not decoding results.

Exploratory filtering/epoch outputs are in m01-s001r04/preprocessing/. Regenerate
using `uv run --offline --locked python -m spikesyn.preprocessing` from the root.
See [the preprocessing record](../docs/m01-preprocessing.md) for array units,
labels, trial identities, exclusions and limitations. No decoding results exist.
