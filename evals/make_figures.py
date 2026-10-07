#!/usr/bin/env python3
"""Generate the FrameScribe vision-model eval fixtures (deterministic).

Six small block diagrams with known labels, connections and one overlay each, rendered
with Pillow so the ground truth is exact. Used to compare vision models on the contract
task (final state + diagram structure + overlay inventory) before choosing a primary.

    uv run --with pillow python evals/make_figures.py
"""

from __future__ import annotations

import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
FIG = ROOT / "figures"
FIG.mkdir(exist_ok=True)
W, H = 1100, 620
FONT = ImageFont.truetype("arial.ttf", 26)
SMALL = ImageFont.truetype("arial.ttf", 22)


def _center(xy):
    return ((xy[0] + xy[2]) / 2, (xy[1] + xy[3]) / 2)


def _box(d, xy, label, highlight=False):
    d.rectangle(xy, fill=(255, 255, 255), outline=(0, 0, 0), width=3)
    if highlight:
        d.rectangle((xy[0] - 7, xy[1] - 7, xy[2] + 7, xy[3] + 7), outline=(205, 30, 30), width=6)
    tw = d.textlength(label, font=FONT)
    d.text(((xy[0] + xy[2]) / 2 - tw / 2, (xy[1] + xy[3]) / 2 - 15), label, fill=(0, 0, 0), font=FONT)


def _edge(xy, toward):
    """Point on the box boundary in the direction of `toward` (AABB ray hit)."""
    cx, cy = _center(xy)
    dx, dy = toward[0] - cx, toward[1] - cy
    hw, hh = (xy[2] - xy[0]) / 2, (xy[3] - xy[1]) / 2
    tx = hw / abs(dx) if dx else float("inf")
    ty = hh / abs(dy) if dy else float("inf")
    t = min(tx, ty)
    return (cx + dx * t, cy + dy * t)


def _arrow(d, xy1, xy2, color=(0, 0, 0), width=3):
    c1, c2 = _center(xy1), _center(xy2)
    p1, p2 = _edge(xy1, c2), _edge(xy2, c1)
    d.line([p1, p2], fill=color, width=width)
    ang = math.atan2(p2[1] - p1[1], p2[0] - p1[0])
    for da in (2.6, -2.6):
        d.line([p2, (p2[0] + 16 * math.cos(ang + da), p2[1] + 16 * math.sin(ang + da))],
               fill=color, width=width)


def _circle(d, xy):
    d.ellipse((xy[0] - 16, xy[1] - 16, xy[2] + 16, xy[3] + 16), outline=(205, 30, 30), width=6)


def render(fig):
    img = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(img)
    for b in fig["boxes"]:
        _box(d, tuple(b["xy"]), b["label"], b.get("highlight", False))
    for a in fig["arrows"]:
        _arrow(d, tuple(fig["by_label"][a[0]]), tuple(fig["by_label"][a[1]]))
    for o in fig.get("circles", []):
        _circle(d, tuple(fig["by_label"][o]))
    if fig.get("callout"):
        d.text(tuple(fig["callout"]["xy"]), fig["callout"]["text"], fill=(205, 30, 30), font=SMALL)
    img.save(FIG / f"{fig['id']}.png")


def main() -> None:
    figs, gt = [], []

    def F(fid, boxes, arrows, callout=None, circles=None, overlays=None):
        by = {b["label"]: b["xy"] for b in boxes}
        figs.append({"id": fid, "boxes": boxes, "arrows": arrows, "by_label": by,
                     "callout": callout, "circles": circles or []})
        gt.append({"id": fid,
                   "labels": [b["label"] for b in boxes],
                   "connections": [list(a) for a in arrows],
                   "overlays": overlays or []})

    F("f1-pipeline",
      [{"label": "Input", "xy": (70, 250, 260, 330)},
       {"label": "Encoder", "xy": (330, 250, 520, 330)},
       {"label": "Output", "xy": (590, 250, 780, 330)}],
      [("Input", "Encoder"), ("Encoder", "Output")])

    F("f2-bottleneck",
      [{"label": "Input", "xy": (20, 250, 180, 330)},
       {"label": "Encoder", "xy": (210, 250, 380, 330)},
       {"label": "Latent", "xy": (410, 250, 570, 330), "highlight": True},
       {"label": "Decoder", "xy": (600, 250, 770, 330)},
       {"label": "Output", "xy": (800, 250, 960, 330)}],
      [("Input", "Encoder"), ("Encoder", "Latent"), ("Latent", "Decoder"), ("Decoder", "Output")],
      overlays=[{"kind": "highlight", "target": "Latent"}])

    F("f3-compare",
      [{"label": "Data", "xy": (60, 240, 240, 320)},
       {"label": "Baseline", "xy": (360, 90, 560, 170)},
       {"label": "Ours", "xy": (360, 390, 560, 470)}],
      [("Data", "Baseline"), ("Data", "Ours")],
      callout={"text": "2x faster", "xy": (640, 415)},
      overlays=[{"kind": "callout", "target": "Ours"}])

    F("f4-loop",
      [{"label": "A", "xy": (140, 110, 260, 190)},
       {"label": "B", "xy": (600, 110, 720, 190)},
       {"label": "C", "xy": (370, 400, 490, 480)}],
      [("A", "B"), ("B", "C"), ("C", "A")],
      overlays=[{"kind": "annotation", "target": "C"}])

    F("f5-flow",
      [{"label": "Data", "xy": (80, 250, 260, 330)},
       {"label": "Process", "xy": (360, 250, 560, 330)},
       {"label": "Result", "xy": (660, 250, 840, 330)}],
      [("Data", "Process"), ("Process", "Result")],
      circles=["Process"],
      overlays=[{"kind": "circle", "target": "Process"}])

    F("f6-decision",
      [{"label": "check x>0", "xy": (120, 240, 380, 330), "highlight": True},
       {"label": "yes path", "xy": (500, 90, 740, 170)},
       {"label": "no path", "xy": (500, 390, 740, 470)}],
      [("check x>0", "yes path"), ("check x>0", "no path")],
      overlays=[{"kind": "highlight", "target": "check x>0"}])

    for fig in figs:
        render(fig)
    (ROOT / "ground-truth.json").write_text(json.dumps(gt, indent=2), encoding="utf-8")
    print(f"wrote {len(figs)} figures + ground-truth.json")


if __name__ == "__main__":
    main()
