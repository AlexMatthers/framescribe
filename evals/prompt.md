# FrameScribe vision eval — task prompt

You are being evaluated on a **vision** task. For **each** image in `evals/figures/`
(read all six PNGs with your file-read tool so they are attached), produce one JSON object
describing the diagram under the FrameScribe contract.

Return **ONLY** a JSON array of six objects, no prose:

```json
[
  {
    "figure_id": "f1-pipeline",
    "final_state": "<one sentence: the fully-drawn diagram>",
    "build_order": ["<ordered step>"],
    "overlays": [{"kind": "<highlight|circle|callout|annotation|arrow|underline>", "description": "<what is emphasised>"}],
    "diagram": {
      "labels": ["<exact text in each box, in reading order>"],
      "connections": [["<from label>", "<to label>"]],
      "overlays": [{"kind": "<kind>", "target": "<label or none>"}]
    }
  }
]
```

Rules:
- Transcribe box labels **exactly** as shown.
- `connections` are **directed arrows**, from → to, using the exact labels.
- `overlays` are any red/emphasis marks: a highlighted box (kind `highlight`), a red circle
  (`circle`), or red text (`callout`/`annotation`). `target` is the label it applies to.
- If a figure shows no build-up, `build_order` is `[]`.
- Keep `final_state` to one sentence. Do not add commentary outside the JSON.
