# P-002 M1 — engine plan

**Goal:** a working, tested FrameScribe engine slice on real video, dogfooding the P-003
plan-time gate on this manifest before dispatch.

**Scope (M1):** frame extraction, figure-activity detection, boundary segmentation,
stability-aware sampling, a pluggable describer (stub + kilo CLI), Markdown assembly, and a
CLI. Model-backed description uses the selected primary **`kilo/google/gemma-4-31b-it`**
(fallback `kilo/z-ai/glm-5.3-flash`), per `evals/report.md`.

**Non-goals (M1):** real-time, non-Markdown outputs, model fine-tuning, a web service.

**Acceptance:** `python -m framescribe run <video> --describer stub` produces `notes.md` +
`segments.json` on a small real clip; `uv run pytest` passes offline; the plan passes the
P-003 gate.

**Gate:** `plan/m1-engine-manifest.json`, reviewed by `tools/p003/gate.py`; dispatch only if
GREEN. The reviewed manifest's canonical hash is the dispatch contract.
