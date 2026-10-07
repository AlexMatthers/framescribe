# FrameScribe — design

## Problem

Technical talks carry their argument in **figures**, which are frequently *built up* on
screen across several seconds. Transcript-only notes lose this; fixed-interval frame
sampling either misses the fully-drawn state or floods the reader with mid-animation
frames. The useful signal is sparse and figure-shaped.

## Approach

1. **Figure activity detection.** Find windows where the visual content is figure-like and
   changing (scene detection / edge-density deltas), rather than sampling on a fixed grid.
2. **Boundary segmentation.** Cut on figure *boundaries*, not fixed slices: a segment is
   one figure build-up.
3. **Stability-aware sampling.** A mid-reveal frame is not a stable state. Sample a
   segment at a low rate (~2–5 fps, downscaled) and check stability against **±5 s
   neighbour frames** before describing; prefer the stable final frame.
4. **Contract description.** Describe each segment with a vision model under the fixed
   contract (`SegmentNotes`): final-state transcription, build order, causal overlays.
5. **Markdown assembly.** Emit one block per segment, interleaved with the aligned
   transcript.

## Non-goals

- Full-video OCR/transcription quality (use a dedicated ASR tool).
- Real-time operation.
- Non-Markdown outputs.

## Contract rationale

A caption ("a diagram of a transformer") is not machine-consumable; a verbatim frame
description is not useful to a reader reconstructing an argument. `SegmentNotes` encodes
exactly the three fields a reader needs: what it ended up being, how it was built, and
what was emphasised. Keeping this in `src/framescribe/contract.py` makes it the single
point of change and the interface downstream tooling binds to.
