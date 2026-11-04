# CLAUDE.md

Rules:

- Always plan the milestone before implementation and ask for approval.

## Project

chess-ocr fine-tunes a swappable, page-level OCR base model with QLoRA so that
pages from chess books come out as text with real Unicode figurines (♔♕♖♗♘),
evaluation symbols, and `[DIAGRAM]` markers. Read these before working:

- `docs/OUTPUT_FORMAT.md`: the target text spec. Labels, metrics and
  post-processing all follow it.
- `docs/ARCHITECTURE.md`: the pipeline, the `OCRBackend` interface, the
  package layout and the VRAM budget.
- `docs/DATASET.md`: data sources, extraction method, splits and copyright
  rules.
- `CONTRIBUTING.md`: the issue, branch and PR workflow and the issue template.

Planning lives on GitHub. Milestones M1–M6 lead to the v1.0.0 release, and
there is a post-v1 backlog milestone:
https://github.com/gustavowkayser/chess-ocr/milestones. Use the `gh` CLI. Start
any task by reading its issue and the issue's milestone description.

## Hard rules

- **Copyright.** `assets/*.pdf` are copyrighted books. Never commit, upload or
  paste their pages. The same goes for anything derived from them: rendered
  images, labels and manifests under `data/`, and model outputs on those pages.
  Do not put such content in issues, PRs, commit messages or test fixtures.
  Tests use synthetic fixtures only.
- **Backend isolation.** Model-specific imports (transformers model classes,
  processor code, etc.) live only in `src/chess_ocr/backends/<model>.py`.
- **The output spec is the contract.** If behaviour needs to differ from
  `docs/OUTPUT_FORMAT.md`, change the spec in the same PR and say so.
- **Plan, then implement.** Present the plan for a milestone or issue and wait
  for approval before writing code.

## Environment

- Windows 11. The shell is PowerShell, with Git Bash also available. Use
  forward slashes in Python paths.
- GPU: RTX 5060, 8 GB VRAM, Blackwell (sm_120). It needs a PyTorch build for
  CUDA 12.8 or newer. "No kernel image is available" means the wrong torch
  wheel is installed.
- 24 GB RAM. Load models in 4-bit, use batch size 1 with gradient accumulation
  and gradient checkpointing, and cap the input pixels per backend.
- Python 3.12 managed by uv. The system Python is 3.14; do not use it for the
  project.
- Commands: `uv sync`, `uv run pytest`, `uv run ruff check .`,
  `uv run ruff format .`.
- Poppler CLI tools (`pdfinfo`, `pdfimages`, `pdftotext`, `pdftoppm`) are
  installed. They are useful for inspecting the PDFs.

## Conventions

- Branch name: `<issue-number>-<slug>`. The PR body contains `Closes #N`.
- Type-hinted Python and small modules. Keep pytest tests CPU-only and fast.
  GPU tests are marked `@pytest.mark.gpu` and skipped in CI.
- Generated artefacts go to `data/` (datasets) or `runs/` (checkpoints,
  adapters, eval reports). Both are gitignored.
