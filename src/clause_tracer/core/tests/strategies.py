"""Hypothesis strategies for the core tests. Not exported from core."""

from hypothesis import strategies as st
from hypothesis.strategies import SearchStrategy

from clause_tracer.core import Span


def spans() -> SearchStrategy[Span]:
    """Spans over the canonical text: a start and a length."""

    return st.builds(
        lambda start, length: Span(start=start, end=start + length),
        start=st.integers(0, 200),
        length=st.integers(0, 50),
    )
