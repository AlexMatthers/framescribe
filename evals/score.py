#!/usr/bin/env python3
"""Score vision-model results against evals/ground-truth.json.

    uv run python evals/score.py
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
GT = {g["id"]: g for g in json.loads((ROOT / "ground-truth.json").read_text(encoding="utf-8"))}


def norm(s: str) -> str:
    return "".join(c for c in str(s).lower() if c.isalnum() or c == " ").strip()


def _label_hit(label: str, pred_labels: list[str], final_state: str) -> bool:
    n = norm(label)
    if any(n and (n in norm(p) or norm(p) in n) for p in pred_labels):
        return True
    return bool(n) and n in norm(final_state)


def score(figs: list) -> dict:
    by = {str(f.get("figure_id")): f for f in figs if isinstance(f, dict)}
    tl = tlh = tc = tch = to = toh = valid = 0
    for fid, g in GT.items():
        f = by.get(fid)
        if not f:
            continue
        d = f.get("diagram") if isinstance(f.get("diagram"), dict) else {}
        plabels = [str(x) for x in (d.get("labels") or [])]
        fs = str(f.get("final_state", ""))
        tl += len(g["labels"])
        tlh += sum(1 for L in g["labels"] if _label_hit(L, plabels, fs))
        pconn = {tuple(norm(x) for x in c) for c in (d.get("connections") or [])
                 if isinstance(c, list) and len(c) == 2}
        tc += len(g["connections"])
        tch += sum(1 for a, b in g["connections"] if (norm(a), norm(b)) in pconn)
        pov = [o for o in (d.get("overlays") or []) if isinstance(o, dict)]

        def ov_hit(o: dict) -> bool:
            t, k = norm(o.get("target", "")), norm(o.get("kind", ""))
            for p in pov:
                pt, pk = norm(p.get("target", "")), norm(p.get("kind", ""))
                if t and t == pt:
                    return True
                if k and k == pk and t and (t in pt or pt in t):
                    return True
            return False

        to += len(g["overlays"])
        toh += sum(1 for o in g["overlays"] if ov_hit(o))
        if d:
            valid += 1

    def r(a: int, b: int) -> float:
        return round(a / b, 3) if b else 1.0

    lr, cr, orr = r(tlh, tl), r(tch, tc), r(toh, to)
    return {"figures_scored": valid, "label_recall": lr, "connection_recall": cr,
            "overlay_recall": orr, "mean_recall": round((lr + cr + orr) / 3, 3)}


def main() -> int:
    results = ROOT / "results"
    results.mkdir(exist_ok=True)
    rows = []
    for f in sorted(results.glob("*.json")):
        try:
            figs = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            rows.append({"model": f.stem, "error": "invalid JSON"})
            continue
        if isinstance(figs, dict):
            figs = figs.get("figures", [])
        rows.append({"model": f.stem, **score(figs)})
    print(json.dumps(rows, indent=2))
    (ROOT / "report.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
