"""The FrameScribe output contract.

A figure in a technical talk is often *built up* on screen, so a single frame is not a
faithful description. Each figure segment is described by three things:

1. ``final_state`` — the transcription of the stable, final frame(s); what the diagram
   *is* once fully drawn.
2. ``build_order`` — the ordered steps shown while the figure was assembled (empty when the
   figure appeared fully formed).
3. ``overlays`` — an inventory of causal/emphasis marks (arrows, highlights, annotations)
   added over the figure.

These three fields are what a reader needs to reconstruct the argument; a bare caption is
not machine-consumable and a verbatim frame description is not useful. This module is the
single source of truth for that shape.
"""

from __future__ import annotations

from dataclasses import dataclass, field

__all__ = ["OVERLAY_KINDS", "CausalOverlay", "SegmentNotes"]

#: Recognised overlay kinds; unknown kinds are allowed but discouraged so downstream
#: consumers can rely on a small vocabulary.
OVERLAY_KINDS = ("arrow", "highlight", "annotation", "callout", "underline", "circle")


@dataclass(frozen=True)
class CausalOverlay:
    """An emphasis/causal mark drawn over a figure."""

    kind: str
    description: str

    def __post_init__(self) -> None:
        if not self.kind:
            raise ValueError("overlay kind must be non-empty")
        if not self.description:
            raise ValueError("overlay description must be non-empty")

    def to_markdown(self) -> str:
        return f"- **{self.kind}** — {self.description}"


@dataclass
class SegmentNotes:
    """Structured notes for one figure-bearing segment of a talk."""

    segment_id: str
    start_s: float
    end_s: float
    final_state: str
    build_order: list[str] = field(default_factory=list)
    overlays: list[CausalOverlay] = field(default_factory=list)
    transcript: str = ""

    def __post_init__(self) -> None:
        if not self.segment_id:
            raise ValueError("segment_id must be non-empty")
        if self.end_s < self.start_s:
            raise ValueError("end_s must be >= start_s")
        if not self.final_state:
            raise ValueError("final_state must be non-empty")

    def to_markdown(self) -> str:
        """Render this segment as one Markdown block."""
        hhmmss = f"{int(self.start_s // 60):02d}:{int(self.start_s % 60):02d}"
        lines = [f"### {self.segment_id} — {hhmmss}", "", self.final_state.strip()]
        if self.build_order:
            lines += ["", "**Build:**", *[f"{i}. {step}" for i, step in enumerate(self.build_order, 1)]]
        if self.overlays:
            lines += ["", "**Overlays:**", *[o.to_markdown() for o in self.overlays]]
        if self.transcript:
            lines += ["", f"> {self.transcript.strip()}"]
        return "\n".join(lines)
