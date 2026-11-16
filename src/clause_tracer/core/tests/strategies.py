"""Hypothesis strategies for the core tests. Not exported from core."""

from hypothesis import assume
from hypothesis import strategies as st
from hypothesis.strategies import SearchStrategy, composite

from clause_tracer.core import (
    UNSURE_REASONS,
    Clause,
    ClauseId,
    Direction,
    Document,
    Evidence,
    FileKind,
    Glyph,
    Level,
    NumberRule,
    Page,
    PageBox,
    Position,
    PositionId,
    PositionType,
    ReasonCode,
    Sentence,
    SentenceId,
    SourceFile,
    Span,
    Unit,
    ValueVerdict,
    WordsRule,
    YesNoRule,
    fold_for_quote_check,
)


def spans() -> SearchStrategy[Span]:
    """Spans over the canonical text: a start and a length."""

    return st.builds(
        lambda start, length: Span(start=start, end=start + length),
        start=st.integers(0, 200),
        length=st.integers(0, 50),
    )


@composite
def value_verdicts(draw: st.DrawFn) -> ValueVerdict:
    """Value verdicts for Rule 4: unsure ones with unsure reasons, and
    readable ones with note reasons and a readable value."""

    clause_id = draw(st.sampled_from(["c1", "c2", "c3"]))
    level = draw(st.sampled_from(Level))
    if level is Level.UNSURE:
        reasons: list[ReasonCode] = draw(
            st.lists(st.sampled_from(sorted(UNSURE_REASONS)), min_size=1, max_size=3)
        )
        readable: str | None = None
    else:
        reasons = draw(
            st.lists(
                st.sampled_from([ReasonCode.RANGE, ReasonCode.CLAUSES_DISAGREE]),
                min_size=0,
                max_size=2,
            )
        )
        readable = draw(st.sampled_from(["5", "10", "30"]))
    return ValueVerdict(
        clause_id=ClauseId(clause_id),
        level=level,
        reasons=tuple(reasons),
        evidence=None,
        readable_value=readable,
    )


@composite
def positions(draw: st.DrawFn) -> Position:
    """Playbook positions of any type, with limits ordered so the
    preferred limit is the stricter one."""

    number = draw(st.integers(0, 99))
    position_type = draw(st.sampled_from(PositionType))
    unit = draw(st.sampled_from(Unit))
    direction = draw(st.sampled_from(Direction))
    first = draw(st.decimals(0, 100, places=0))
    second = draw(st.decimals(0, 100, places=0))
    if direction is Direction.LOWER_IS_BETTER:
        rule: NumberRule | YesNoRule | WordsRule = NumberRule(
            unit=unit,
            direction=direction,
            preferred_limit=min(first, second),
            acceptable_limit=max(first, second),
        )
    else:
        rule = NumberRule(
            unit=unit,
            direction=direction,
            preferred_limit=max(first, second),
            acceptable_limit=min(first, second),
        )
    if position_type is PositionType.YES_NO:
        rule = YesNoRule(
            question="q",
            yes_level=draw(st.sampled_from([Level.PREFERRED, Level.ACCEPTABLE, Level.WALK_AWAY])),
            no_level=draw(st.sampled_from([Level.PREFERRED, Level.ACCEPTABLE, Level.WALK_AWAY])),
        )
    elif position_type is PositionType.WORDS:
        rule = WordsRule(preferred="a", acceptable="b", walk_away="c")
    return Position(
        id=PositionId(f"p{number}"),
        topic="t",
        type=position_type,
        rule=rule,
        missing_level=draw(st.sampled_from(Level)),
        why_note=None,
    )


# The characters that break PDF offsets and folds: ligatures, soft
# hyphens, curly quotes, zero-width characters, bidi controls, the
# "⟦" escape, and astral characters, whose offsets count code points
# (testing strategy 5).
HAZARD_ALPHABET: tuple[str, ...] = (
    *"abcXYZ019",
    " ",
    "\n",
    "\u00a0",
    "\ufb01",
    "\ufb02",
    "\u00ad",
    "'",
    '"',
    "‘",
    "’",
    "“",
    "”",
    "\u200b",
    "\u200c",
    "\u200d",
    "\ufeff",
    "\u202a",
    "\u202b",
    "\u202c",
    "\u202d",
    "\u202e",
    "\u2066",
    "\u2067",
    "\u2068",
    "\u2069",
    "ß",
    "\U0001f600",
    "\U0001d400",
    "⟦",
    "⟧",
)

_UNPAIRED_QUOTES = "'\"‘’“”"


def hazard_text() -> SearchStrategy[str]:
    """A short text over the hazard alphabet."""

    return st.text(alphabet=st.sampled_from(HAZARD_ALPHABET), min_size=1, max_size=80)


def _overlapping_places(haystack: str, needle: str) -> int:
    """How many places the needle starts in the haystack, overlapping
    places included — the same count the last check before drawing uses."""

    return sum(
        1
        for index in range(len(haystack) - len(needle) + 1)
        if haystack[index : index + len(needle)] == needle
    )


@composite
def documents_with_quote(
    draw: st.DrawFn,
) -> tuple[Document, Clause, Evidence, str]:
    """One document with one clause and one sentence over the whole text,
    and a quote the last check before drawing must approve."""

    text = draw(hazard_text())
    with_glyphs = draw(st.booleans())
    start = draw(st.integers(0, len(text) - 1))
    end = draw(st.integers(start + 1, len(text)))
    while start < len(text) and text[start].isspace():
        start += 1
    while end > start and text[end - 1].isspace():
        end -= 1
    assume(start < end)
    quote = text[start:end]
    folded_text = fold_for_quote_check(text).text
    folded_quote = fold_for_quote_check(quote).text
    assume(_overlapping_places(folded_text, folded_quote) == 1)
    source = SourceFile(name="sample.pdf", kind=FileKind.PDF, sha256="0" * 64, size=1)
    if with_glyphs:
        box = PageBox(page=1, x0=0, top=0, x1=1, bottom=1)
        glyphs: tuple[Glyph, ...] = tuple(Glyph(page=1, box=box) for _ in text)
        char_map: tuple[int | None, ...] = tuple(range(len(text)))
        pages: tuple[Page, ...] = (Page(number=1, width=600.0, height=800.0),)
    else:
        glyphs = ()
        char_map = ()
        pages = ()
    document = Document(
        schema_version=1,
        source=source,
        text=text,
        char_map=char_map,
        glyphs=glyphs,
        pages=pages,
        furniture=(),
        hidden=(),
        undecodable=(),
        tracked_changes=(),
        warnings=(),
    )
    clause = Clause(
        id=ClauseId("c1"),
        number=None,
        heading=None,
        level=1,
        parent_id=None,
        span=Span(start=0, end=len(text)),
        numbering_source="test",
        sentences=(Sentence(id=SentenceId("c1.s1"), span=Span(start=0, end=len(text))),),
    )
    evidence = Evidence(
        clause_id=ClauseId("c1"),
        sentence_ids=(SentenceId("c1.s1"),),
        quote=Span(start=start, end=end),
        placed=True,
    )
    return (document, clause, evidence, quote)
