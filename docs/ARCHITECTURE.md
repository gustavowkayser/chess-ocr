# Architecture

## Pipeline

```
 PDF / image ──► page images ──► OCRBackend.predict ──► post-processing ──► text
                     ▲                  ▲  (base model + LoRA adapter)        (OUTPUT_FORMAT.md)
                     │                  │
               data/ rendering    training (QLoRA) on data/manifests
```

1. **Rendering.** PDFs are rasterized one page at a time (PyMuPDF). Image
   inputs pass straight through.
2. **Recognition.** A page-level OCR model reads the whole page and emits text
   in reading order, figurines and `[DIAGRAM]` markers included. We work at
   page level, not line level, because chess books mix two-column layouts,
   move tables and diagrams. A line-level pipeline would need its own layout
   analysis.
3. **Post-processing.** Deterministic cleanup to the output spec. For example,
   filled figurine glyphs are mapped to outline glyphs and whitespace is
   normalized. This step never guesses content.

## The `OCRBackend` interface

The base model is **swappable**. Nothing outside `chess_ocr/backends/` may
import a model-specific library or class. Each backend is an adapter behind one
interface:

```python
class OCRBackend(Protocol):
    name: str  # registry key, e.g. "paddleocr-vl"

    def load(self, *, adapter: Path | None = None, quantize_4bit: bool = True) -> None:
        """Load base weights (optionally 4-bit) and an optional LoRA adapter."""

    def predict(self, images: Sequence[Image.Image]) -> list[str]:
        """Page images -> raw text, one string per image."""

    def build_training_example(self, image: Image.Image, target: str) -> dict:
        """Model-specific preprocessing + tokenization for one (page, label) pair."""

    def lora_target_modules(self) -> list[str]:
        """Module names LoRA should wrap for this architecture."""
```

Backends are registered by name (`chess_ocr.backends.registry`). The training
and eval code ask the registry for a backend, so switching models is a config
change:

```yaml
backend: paddleocr-vl
```

Adding a model means writing one adapter file and its tests, and nothing else.

## Package layout (planned)

```
src/chess_ocr/
  backends/      base.py (protocol), registry.py, one module per model
  data/          render.py, fischer.py (M2), synthetic.py (M3), manifest.py, splits
  text/          figurines.py (glyph constants), normalize.py, postprocess.py
  eval/          metrics.py, report.py
  train/         lora.py (QLoRA loop), config.py
  cli.py         `chess-ocr` entry point (ocr / eval / train / data subcommands)
configs/         YAML for training and eval runs
tests/           pytest. CPU-only, no copyrighted fixtures
data/            gitignored, see DATASET.md
runs/            gitignored. Checkpoints, adapters, logs, eval reports
```

## Hardware budget

The target machine has an **RTX 5060 with 8 GB VRAM** (Blackwell, sm_120) and
**24 GB RAM**.

- Base weights load in 4-bit (NF4, bitsandbytes), and LoRA adapters train in
  bf16. This is QLoRA.
- Batch size 1 with gradient accumulation, and gradient checkpointing on.
- Input resolution is capped per backend (max pixels or max visual tokens) so
  that a full page fits in memory. The cap is part of the backend config.
- Base-model candidates must fit this budget during **training**, not just
  inference. That is a hard requirement in the M4 benchmark.
- Blackwell needs a PyTorch build with **CUDA 12.8 or newer**. Older wheels
  fail with "no kernel image is available".

## Evaluation metrics

| Metric | What it catches |
|---|---|
| CER / WER over the page | General recognition quality |
| Figurine precision / recall / F1 (per piece) | The core problem: missing, invented or wrong figurines |
| Move-token accuracy | Whole SAN tokens (`♘xe4`) right or wrong |
| `[DIAGRAM]` precision / recall | Diagram handling |

Reports are written to `runs/<run>/eval/` as JSON plus a short Markdown
summary. They are broken down by source (Fischer test split, Chess Structures).

## Key decisions

| Decision | Choice | Why |
|---|---|---|
| Modeling unit | Whole page | Layout-heavy pages; no separate layout pipeline |
| Fine-tuning | QLoRA | Fits in 8 GB VRAM; small adapters, base stays swappable |
| Figurine encoding | Outline Unicode glyphs | Matches the printed page; easy to convert to SAN letters later |
| Diagrams in v1 | `[DIAGRAM]` placeholder | Diagram→FEN is a separate vision task (backlog) |
| Tooling | uv, Python 3.12, ruff, pytest | Best Windows + CUDA wheel support |

The base model itself is chosen in M4 and recorded in
`docs/decisions/0001-base-model.md`.
