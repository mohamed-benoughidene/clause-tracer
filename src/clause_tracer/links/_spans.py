"""Span helpers: the trimmed span, and one overlap check for many spans (S3-M2-T1)."""

import bisect
from collections.abc import Iterable
from dataclasses import dataclass

from clause_tracer.core import Span


def trimmed(text: str, span: Span) -> Span:
    """Move `end` back over trailing white space, never below `start`."""

    end = span.end
    while end > span.start and text[end - 1].isspace():
        end -= 1
    return Span(start=span.start, end=end)


@dataclass(frozen=True, slots=True, kw_only=True)
class SpanSet:
    """Sorted spans, so many overlap checks cost one binary search each."""

    starts: tuple[int, ...]
    max_ends: tuple[int, ...]

    def overlaps(self, span: Span) -> bool:
        """Return whether `span` shares a character with any span in the set."""

        if span.start == span.end:
            return False
        index = bisect.bisect_left(self.starts, span.end)
        return index > 0 and self.max_ends[index - 1] > span.start


def build_span_set(spans: Iterable[Span]) -> SpanSet:
    """Drop empty spans, sort the rest by start, and keep the largest end so far."""

    ordered = sorted(
        (span for span in spans if span.start != span.end),
        key=lambda span: (span.start, span.end),
    )
    starts = tuple(span.start for span in ordered)
    max_ends: list[int] = []
    running = -1
    for span in ordered:
        running = max(running, span.end)
        max_ends.append(running)
    return SpanSet(starts=starts, max_ends=tuple(max_ends))
