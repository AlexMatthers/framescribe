#!/usr/bin/env python3
"""Generate the FrameScribe vision-model eval **video-snippet** fixtures.

Each clip is a short *build-up* rendered as an ordered frame sequence (the models are
video-capable; the eval delivers video as frames so build-order is scored). Ground truth is
exact: final labels, directed connections, overlays, and the build order.

    uv run --with pillow python evals/make_clips.py
"""

from __future__ import annotations

import json
from pathlib import Path

from make_figures import SMALL, W, _arrow, _box, _circle
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
CLIPS = ROOT / "clips"
CLIPS.mkdir(exist_ok=True)


def render_frame(path: Path, boxes, arrows, callout=None, circles=None):
    img = Image.new("RGB", (W, 620), (255, 255, 255))
    d = ImageDraw.Draw(img)
    by = {b["label"]: b["xy"] for b in boxes}
    for b in boxes:
        _box(d, tuple(b["xy"]), b["label"], b.get("highlight", False))
    for a in arrows:
        _arrow(d, tuple(by[a[0]]), tuple(by[a[1]]))
    for lbl in (circles or []):
        _circle(d, tuple(by[lbl]))
    if callout:
        d.text(tuple(callout["xy"]), callout["text"], fill=(205, 30, 30), font=SMALL)
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)


# Boxes reused across frames.
IN = {"label": "Input", "xy": (70, 250, 260, 330)}
EN = {"label": "Encoder", "xy": (330, 250, 520, 330)}
LA = {"label": "Latent", "xy": (330, 250, 520, 330), "highlight": True}
DE = {"label": "Decoder", "xy": (590, 250, 780, 330)}
OU = {"label": "Output", "xy": (850, 250, 1040, 330)}
DA = {"label": "Data", "xy": (60, 240, 240, 320)}
BA = {"label": "Baseline", "xy": (380, 90, 580, 170)}
OO = {"label": "Ours", "xy": (380, 390, 580, 470)}
# c2-specific boxes with DISTINCT positions (Encoder and Latent must not overlap).
IN2 = {"label": "Input", "xy": (20, 250, 150, 330)}
EN2 = {"label": "Encoder", "xy": (180, 250, 320, 330)}
LA2 = {"label": "Latent", "xy": (350, 250, 490, 330)}
LA2H = {"label": "Latent", "xy": (350, 250, 490, 330), "highlight": True}
DE2 = {"label": "Decoder", "xy": (520, 250, 660, 330)}
OU2 = {"label": "Output", "xy": (690, 250, 830, 330)}

CLIPS_DEF = [
    {
        "id": "c1-pipeline-build",
        "frames": [
            ([IN], []),
            ([IN, EN], []),
            ([IN, EN], [("Input", "Encoder")]),
            ([IN, EN, OU], [("Input", "Encoder")]),
            ([IN, EN, OU], [("Input", "Encoder"), ("Encoder", "Output")]),
        ],
        "gt": {
            "labels": ["Input", "Encoder", "Output"],
            "connections": [["Input", "Encoder"], ["Encoder", "Output"]],
            "overlays": [],
            "build_order": ["Input box appears", "Encoder box appears",
                            "arrow Input to Encoder", "Output box appears",
                            "arrow Encoder to Output"],
        },
    },
    {
        "id": "c2-bottleneck-highlight",
        "frames": [
            ([IN2], []),
            ([IN2, EN2], []),
            ([IN2, EN2, LA2], [("Input", "Encoder")]),
            ([IN2, EN2, LA2, DE2], [("Input", "Encoder"), ("Encoder", "Latent")]),
            ([IN2, EN2, LA2H, DE2, OU2],
             [("Input", "Encoder"), ("Encoder", "Latent"), ("Latent", "Decoder"),
              ("Decoder", "Output")]),
        ],
        "gt": {
            "labels": ["Input", "Encoder", "Latent", "Decoder", "Output"],
            "connections": [["Input", "Encoder"], ["Encoder", "Latent"],
                            ["Latent", "Decoder"], ["Decoder", "Output"]],
            "overlays": [{"kind": "highlight", "target": "Latent"}],
            "build_order": ["Input box appears", "Encoder box appears", "Latent box appears",
                            "Decoder box appears", "Output box appears",
                            "highlight drawn around Latent"],
        },
    },
    {
        "id": "c3-compare-callout",
        "frames": [
            ([DA], []),
            ([DA, BA], []),
            ([DA, BA, OO], [("Data", "Baseline")]),
            ([DA, BA, OO], [("Data", "Baseline"), ("Data", "Ours")]),
            ([DA, BA, OO], [("Data", "Baseline"), ("Data", "Ours")]),
        ],
        "callout_frames": {4: {"text": "2x faster", "xy": (660, 415)}},
        "gt": {
            "labels": ["Data", "Baseline", "Ours"],
            "connections": [["Data", "Baseline"], ["Data", "Ours"]],
            "overlays": [{"kind": "callout", "target": "Ours"}],
            "build_order": ["Data box appears", "Baseline box appears", "Ours box appears",
                            "arrow Data to Baseline", "arrow Data to Ours",
                            "callout '2x faster' appears"],
        },
    },
]


def main() -> None:
    gt = []
    for clip in CLIPS_DEF:
        out = CLIPS / clip["id"]
        for i, (boxes, arrows) in enumerate(clip["frames"]):
            callout = (clip.get("callout_frames") or {}).get(i)
            render_frame(out / f"frame_{i:02d}.png", boxes, arrows, callout=callout)
        gt.append({"id": clip["id"], "n_frames": len(clip["frames"]), **clip["gt"]})
    (ROOT / "clips-ground-truth.json").write_text(json.dumps(gt, indent=2), encoding="utf-8")
    total = sum(len(c["frames"]) for c in CLIPS_DEF)
    print(f"wrote {len(CLIPS_DEF)} clips ({total} frames) + clips-ground-truth.json")


if __name__ == "__main__":
    main()
