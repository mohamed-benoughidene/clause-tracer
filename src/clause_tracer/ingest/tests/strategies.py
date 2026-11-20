"""Hypothesis strategies for the ingest tests. Not exported from ingest."""

from hypothesis import assume
from hypothesis import strategies as st
from hypothesis.strategies import composite

from clause_tracer.core.tests.strategies import hazard_text
from clause_tracer.ingest._lines import is_blank_text


def is_usable_text(text: str) -> bool:
    """True when a generated text is not blank. A text of only a byte-order mark
    is blank, as `read_pasted_text` treats it."""

    return not is_blank_text(text)


MARKER_PREFIXES: tuple[str, ...] = (
    "",
    "",
    "1. ",
    "2. ",
    "3. ",
    "1.1 ",
    "1.2 ",
    "2.1 ",
    "(a) ",
    "(b) ",
    "(i) ",
    "(ii) ",
    "(A) ",
    "(1) ",
    "a) ",
    "ii) ",
    "Article II ",
    "Clause 3 ",
    "3 ",
    "Background\n",
    "Schedule 1 ",
    "## 1. ",
    "**1.1** ",
)


@composite
def contract_like_text(draw: st.DrawFn) -> str:
    """A short contract-like text over the marker prefixes and hazards."""

    lines = draw(
        st.lists(
            st.tuples(st.sampled_from(MARKER_PREFIXES), hazard_text()),
            min_size=1,
            max_size=12,
        )
    )
    separators = draw(
        st.lists(
            st.sampled_from(["\n", "\n\n", "\r\n"]),
            min_size=len(lines) - 1,
            max_size=len(lines) - 1,
        )
    )

    parts: list[str] = []
    for index, (prefix, body) in enumerate(lines):
        if index > 0:
            parts.append(separators[index - 1])
        parts.append(prefix + body)
    text = "".join(parts)
    assume(is_usable_text(text))
    return text
