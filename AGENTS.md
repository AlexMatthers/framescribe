# AGENTS.md — FrameScribe

Operating notes for LLM coding agents working in this repository.

## What this is

FrameScribe turns talk videos into **diagrammatic, figure-aware Markdown notes**. See
`README.md` and `docs/design.md`. The output contract lives in
`src/framescribe/contract.py` — treat it as the interface and change it deliberately.

## Environment

- Python 3.12+, managed **exclusively with `uv`**.
- **This repo may be developed inside another repo's tree** (a git worktree for an
  auxiliary project). Therefore **always run `uv` with `--no-workspace`** so it is not
  adopted as a member of a parent workspace:
  `uv sync --dev --no-workspace`, `uv add --dev --no-workspace <pkg>`.

## Conventions

- Format/lint: `uv run ruff check .` (line length 100). Tests: `uv run pytest`.
- Public-facing repository: keep `README`, `LICENSE` (Apache-2.0), and `pyproject`
  metadata current; no secrets, no personal paths, no vendored third-party code.
- Commits: concise, conventional-commits style (`feat:`, `fix:`, `docs:`, `test:`).
- Disclose LLM-agent participation in substantive changes (see README).

## Out of scope (for now)

- Batch/web service, GPU training, and non-Markdown output formats.
