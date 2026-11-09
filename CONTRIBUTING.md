# Contributing

## Planning model

- **Release:** v1.0.0. Its scope is everything in milestones M1–M6.
- **Milestones:** one per stage, each with a goal and exit criteria in its
  GitHub description. Work on them in order. A milestone is closed when its
  exit criteria are met.
- **Issues:** one deliverable each, small enough for one commit. Every issue
  belongs to a milestone and has exactly one `area:*` label.

| Label | Scope |
|---|---|
| `area:infra` | Tooling, CI, environment, packaging |
| `area:data` | Rendering, extraction, synthetic data, labels, splits |
| `area:model` | Backends, model loading, inference |
| `area:training` | LoRA/QLoRA training |
| `area:eval` | Metrics, benchmarks, reports |
| `area:docs` | Documentation |

## Issue template

```markdown
## Context
Why this exists and what it unblocks.

## Tasks
- [ ] ...

## Acceptance criteria
- [ ] Verifiable statements (a command to run, a number to hit, a file that exists)

## Dependencies
Blocked by #N / none

## Notes for agents
Pointers to the relevant docs, pitfalls, and decisions already made.
```

## Workflow

1. **Plan before implementing.** Plan the milestone and each of its issues,
   and get approval before writing code.
2. **Branch** from `main`, one branch per milestone: `m<N>-<short-slug>`, for
   example `m2-fischer-dataset`.
3. **Commit** one commit per issue, with an imperative subject line that
   references the issue (`#7`). Verify before each commit:
   ```bash
   uv run ruff check . && uv run ruff format --check . && uv run pytest
   ```
4. **Open one PR** when the milestone's issues are done. The body has one
   `Closes #N` line per issue and the evidence for each (command output,
   metric numbers, sample-check notes). Do not include copyrighted page
   content.
5. **Merge** only with green CI. Delete the branch after merging.

## Rules that are never negotiable

- Never commit or upload the books in `assets/`, or anything derived from them
  (`data/`). Tests use synthetic fixtures only.
- Never import a model-specific library outside `src/chess_ocr/backends/`.
- Any change to the output format updates
  [docs/OUTPUT_FORMAT.md](docs/OUTPUT_FORMAT.md) in the same PR.
