#!/usr/bin/env python3
"""Score vision-model (video) results against evals/clips-ground-truth.json.

Quality axes: label recall, connection recall, overlay recall, build-order recall; plus
the mean. Results live in evals/results/<model>.json (a JSON array of per-clip objects).

    uv run python evals/score.py
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
GT = {g["id"]: g for g in json.loads((ROOT / "clips-ground-truth.json").read_text(encoding="utf-8"))}


def norm(s: str) -> str:
    return "".join(c for c in str(s).lower() if c.isalnum() or c == " ").strip()


def _label_hit(label: str, pred_labels: list[str], final_state: str) -> bool:
    n = norm(label)
    if any(n and (n in norm(p) or norm(p) in n) for p in pred_labels):
        return True
    return bool(n) and n in norm(final_state)


def _step_hit(step: str, pred_steps: list[str]) -> bool:
    want = set(norm(step).split())
    for p in pred_steps:
        got = set(norm(p).split())
        if want and len(want & got) / len(want) >= 0.6:
            return True
    return False


def score(clips: list) -> dict:
    by = {str(c.get("figure_id")): c for c in clips if isinstance(c, dict)}
    tl = tlh = tc = tch = to = toh = tb = tbh = valid = 0
    for fid, g in GT.items():
        c = by.get(fid)
        if not c:
            continue
        d = c.get("diagram") if isinstance(c.get("diagram"), dict) else {}
        plabels = [str(x) for x in (d.get("labels") or [])]
        fs = str(c.get("final_state", ""))
        tl += len(g["labels"])
        tlh += sum(1 for L in g["labels"] if _label_hit(L, plabels, fs))

        pconn = {tuple(norm(x) for x in p) for p in (d.get("connections") or [])
                 if isinstance(p, list) and len(p) == 2}
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

        psteps = [str(s) for s in (c.get("build_order") or [])]
        tb += len(g["build_order"])
        tbh += sum(1 for s in g["build_order"] if _step_hit(s, psteps))

        if d and psteps is not None:
            valid += 1

    def r(a: int, b: int) -> float:
        return round(a / b, 3) if b else 1.0

    lr, cr, orr, br = r(tlh, tl), r(tch, tc), r(toh, to), r(tbh, tb)
    return {"clips_scored": valid, "label_recall": lr, "connection_recall": cr,
            "overlay_recall": orr, "build_order_recall": br,
            "mean_recall": round((lr + cr + orr + br) / 4, 3)}


def main() -> int:
    results = ROOT / "results"
    results.mkdir(exist_ok=True)
    rows = []
    for f in sorted(results.glob("*.json")):
        try:
            clips = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            rows.append({"model": f.stem, "error": "invalid JSON"})
            continue
        if isinstance(clips, dict):
            clips = clips.get("clips", clips.get("figures", []))
        rows.append({"model": f.stem, **score(clips)})
    print(json.dumps(rows, indent=2))
    (ROOT / "report.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
