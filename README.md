# FrameScribe

**Turn talk videos into diagrammatic, figure-aware Markdown notes.**

FrameScribe takes a video (a lecture, conference talk, or screencast) and produces
structured Markdown that preserves the *diagrammatic* content — the figures, slides, and
on-screen build-ups — not just a verbatim transcript. It is designed for technical talks
where the slides carry the argument.

> **Status: alpha / scaffold.** The public interface and the output contract are being
> pinned; expect breaking changes before `0.1.0`.

## Why

Transcript-only notes lose the argument when the speaker builds a diagram incrementally:
you get "as you can see here" with no idea what was shown. Most of the information in a
technical talk lives in a small number of figure-heavy windows, and it changes *during*
those windows. FrameScribe treats figures as first-class and segments on **figure
boundaries** rather than on fixed time slices.

## How it works (planned)

1. **Detect figure activity** in the video (scene/edge-density change) to find
   figure-heavy windows.
2. **Segment on figure boundaries** and sample each figure window at a low rate
   (~2–5 fps, downscaled) — a mid-reveal frame is not a stable state, so stability is
   checked against ±5 s neighbour frames.
3. **Describe each segment** with a vision model under a fixed **contract**
   (`framescribe.contract`): the *final-state* transcription, the *build order* shown, and
   an inventory of *causal overlays* (arrows, highlights, annotations).
4. **Emit one Markdown block per segment**, interleaved with the aligned transcript.

The contract exists because a single-frame description is not enough for a build-up, and a
free-form description is not machine-consumable.

## Install

```bash
uv add framescribe     # not yet published
# or, from source:
git clone https://github.com/AlexMatthers/framescribe
cd framescribe && uv sync --dev
```

Requires Python 3.12+.

## Usage

> Planned API; not implemented yet.

```python
from framescribe.contract import SegmentNotes, CausalOverlay

notes = SegmentNotes(
    segment_id="seg-004",
    start_s=312.0, end_s=337.0,
    final_state="A block diagram: Input -> Encoder -> Latent -> Decoder -> Output.",
    build_order=[
        "Input and Output boxes appear",
        "Encoder is inserted between Input and Latent",
        "Decoder is inserted between Latent and Output",
    ],
    overlays=[CausalOverlay("arrow", "Latent -> Decoder is highlighted as the bottleneck")],
    transcript="as you can see, the latent is where the bottleneck lives",
)
print(notes.to_markdown())
```

## Development

```bash
uv sync --dev
uv run ruff check .
uv run pytest
```

**Note for agents/contributors:** this repository is a standalone project that may be
developed inside another repository's tree (a git worktree). Always run `uv` with
`--no-workspace` here so it is not adopted as a member of a parent uv workspace.

## License

Apache-2.0 — see [LICENSE](LICENSE).

## AI participation disclosure

Portions of this project are developed with LLM coding agents under human direction. This
is disclosed in line with the [research-methodology] policy of the originating lab; commit
history and PR descriptions record the provenance of substantive changes.

[research-methodology]: https://github.com/AlexMatthers/mnemosyne
