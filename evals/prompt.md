# FrameScribe vision eval — video-snippet task prompt

You are being evaluated on a **video** task. Each item in `evals/clips/` is a short clip
delivered as an **ordered frame sequence** (`frame_00.png`, `frame_01.png`, …) showing a
diagram being **built up**. Read every frame of every clip (attach them with your file-read
tool), in order.

For **each** clip, reconstruct what was drawn and in what order, under the FrameScribe
contract. Return ONLY a JSON array of three objects, no prose:

```json
[
  {
    "figure_id": "c1-pipeline-build",
    "final_state": "<one sentence: the fully-drawn diagram>",
    "build_order": ["<what appeared first>", "<next>", "..."],
    "overlays": [{"kind": "<highlight|circle|callout|annotation|arrow|underline>", "description": "<what is emphasised>"}],
    "diagram": {
      "labels": ["<exact text in each box>"],
      "connections": [["<from label>", "<to label>"]],
      "overlays": [{"kind": "<kind>", "target": "<label or none>"}]
    }
  }
]
```

Rules:
- `build_order` must reflect the **order things appeared across the frames** (boxes added,
  arrows drawn, highlights/callouts added).
- Transcribe box labels **exactly**; `connections` are **directed arrows** (from → to).
- `overlays` are red/emphasis marks: a highlighted box (`highlight`), a red circle
  (`circle`), or red text (`callout`/`annotation`).
- Keep `final_state` to one sentence; no commentary outside the JSON.
