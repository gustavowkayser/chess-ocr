# chess-ocr

[![CI](https://github.com/gustavowkayser/chess-ocr/actions/workflows/ci.yml/badge.svg)](https://github.com/gustavowkayser/chess-ocr/actions/workflows/ci.yml)

OCR for chess books that reads **piece figurines** correctly.

Chess books write moves with figurines (`♘f3`, `♗xf7+`) and evaluation symbols
(`±`, `⩲`, `∞`). General OCR models have never seen these as characters, so
they come out as junk:

```
OCR text layer of a real scanned chess book:   2 1 .lt:Jxe6   23.E!:c3t
what is printed on the page:                   21.♘xe6        23.♖c3±
```

Figurines come out as junk such as `lt:J`, `E!:` or `��`, or are dropped
entirely. Plain text extraction from digital books often loses them as well.

chess-ocr fine-tunes a general page-level OCR model with **LoRA** (QLoRA, which
fits an 8 GB GPU) so that it outputs real Unicode figurines and symbols, in
reading order, with board diagrams marked as `[DIAGRAM]`.

## Status

Pre-alpha. Work is planned and tracked in the
[GitHub milestones](https://github.com/gustavowkayser/chess-ocr/milestones)
toward **v1.0.0**:

| Milestone | Goal |
|---|---|
| M1: Project foundation | Scaffold, CI, environment, data guardrails |
| M2: Fischer dataset | Exact page labels extracted from *My 60 Memorable Games* |
| M3: Synthetic data & eval set | Copyright-free training pages; hand-corrected *Chess Structures* test set |
| M4: Backends & baseline | Swappable `OCRBackend` interface, metrics, zero-shot benchmark, base model choice |
| M5: LoRA fine-tuning | QLoRA training within 8 GB VRAM |
| M6: Inference & v1.0.0 | CLI (image/PDF → text), final eval report, release |
| Backlog: Diagram → FEN | Post-v1 |

## Documentation

- [docs/OUTPUT_FORMAT.md](docs/OUTPUT_FORMAT.md): what the OCR outputs. This
  is the contract.
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md): the pipeline, the swappable
  backend interface, the hardware budget and the metrics.
- [docs/DATASET.md](docs/DATASET.md): data sources, label extraction, splits
  and copyright rules.
- [CONTRIBUTING.md](CONTRIBUTING.md): the issue, branch and PR workflow.
- [CLAUDE.md](CLAUDE.md): context and rules for AI coding agents.

## Requirements

- An NVIDIA GPU with 8 GB or more VRAM for training. Developed on an RTX 5060
  (Blackwell), which needs PyTorch built for CUDA 12.8 or newer.
- 24 GB RAM recommended.
- Python 3.12 and [uv](https://docs.astral.sh/uv/).

## Setup

```bash
uv sync                  # Python 3.12 + dev tools + the CUDA stack (torch, bitsandbytes, ...)
uv run chess-ocr env     # check CUDA, bf16, sm_120 kernels and a 4-bit (NF4) matmul
```

`uv sync` installs the `gpu` dependency group by default. Torch comes from the
PyTorch CUDA 13.2 index (`cu132`), which needs an NVIDIA driver that supports
CUDA 13.2. Blackwell GPUs need CUDA 12.8 or newer. On a machine without a GPU,
use `uv sync --no-group gpu`.

GPU tests are skipped by default. Run them with:

```bash
uv run pytest --run-gpu -m gpu
```

## Quickstart

> Not implemented yet. This section is filled in by M6 (CLI).
> The planned interface:

```bash
uv run chess-ocr ocr page.png
uv run chess-ocr ocr book.pdf --pages 10-20 --out out/
```

## Data and copyright

The training and eval books are copyrighted and are **not** in this
repository. Neither is anything derived from them (page images, labels). See
[docs/DATASET.md](docs/DATASET.md). To reproduce the dataset, provide your own
copies in `assets/`.
