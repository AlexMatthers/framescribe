"""Smoke tests for the FrameScribe scaffold."""

from __future__ import annotations

import framescribe
from framescribe.contract import CausalOverlay, SegmentNotes


def test_version_present() -> None:
    assert framescribe.__version__


def test_segment_renders_markdown() -> None:
    notes = SegmentNotes(
        segment_id="seg-001",
        start_s=60.0,
        end_s=75.0,
        final_state="A pipeline diagram: A -> B -> C.",
        build_order=["A and C appear", "B is inserted between them"],
        overlays=[CausalOverlay("arrow", "A -> B is highlighted")],
        transcript="and then we insert the encoder",
    )
    md = notes.to_markdown()
    assert md.startswith("### seg-001 — 01:00")
    assert "1. A and C appear" in md
    assert "**arrow**" in md
    assert "> and then we insert the encoder" in md


def test_segment_rejects_bad_input() -> None:
    import pytest

    with pytest.raises(ValueError):
        SegmentNotes(segment_id="", start_s=0, end_s=1, final_state="x")
    with pytest.raises(ValueError):
        SegmentNotes(segment_id="s", start_s=2, end_s=1, final_state="x")
