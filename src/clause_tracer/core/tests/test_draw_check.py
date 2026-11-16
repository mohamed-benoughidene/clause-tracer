"""The last check before drawing (S1-M5-T11 to T13, system design 4.2)."""

from hypothesis import assume, example, given
from hypothesis import strategies as st

from clause_tracer.core import (
    Clause,
    ClauseId,
    Document,
    DrawAllowed,
    DrawFailure,
    DrawRefused,
    Evidence,
    FileKind,
    Glyph,
    Page,
    PageBox,
    Sentence,
    SentenceId,
    SourceFile,
    Span,
    check_before_drawing,
    fold_for_quote_check,
)
from clause_tracer.core.tests.strategies import documents_with_quote

FULL_TEXT = (
    "1. Payment. The Client pays within 60 days. Late fees apply. The Client pays within 60 days."
)
PIECES = (
    "1. Payment. ",
    "The Client pays within 60 days. ",
    "Late fees apply. ",
    "The Client pays within 60 days.",
)
SENTENCE_IDS = tuple(SentenceId(f"c1.s{n}") for n in range(1, 5))

# The same text with the "fees" quote written with curly quotes and two
# spaces, so the fold has to map it back.
CURLY_TEXT = (
    "1. Payment. The Client pays within 60 days. Late “fees”  apply."
    " The Client pays within 60 days."
)
A_SOURCE = SourceFile(name="sample.pdf", kind=FileKind.PDF, sha256="0" * 64, size=1)


def _sentence_spans(text: str) -> tuple[Span, ...]:
    pieces = PIECES if text == FULL_TEXT else _curly_pieces()
    spans: list[Span] = []
    start = 0
    for piece in pieces:
        spans.append(Span(start=start, end=start + len(piece)))
        start += len(piece)
    return tuple(spans)


def _curly_pieces() -> tuple[str, ...]:
    return (
        "1. Payment. ",
        "The Client pays within 60 days. ",
        "Late “fees”  apply. ",
        "The Client pays within 60 days.",
    )


def _clause(text: str = FULL_TEXT) -> Clause:
    spans = _sentence_spans(text)
    return Clause(
        id=ClauseId("c1"),
        number="1",
        heading=None,
        level=1,
        parent_id=None,
        span=Span(start=0, end=len(text)),
        numbering_source="test",
        sentences=tuple(
            Sentence(id=sentence_id, span=span)
            for sentence_id, span in zip(SENTENCE_IDS, spans, strict=True)
        ),
    )


def _document(text: str = FULL_TEXT) -> Document:
    return Document(
        schema_version=1,
        source=A_SOURCE,
        text=text,
        char_map=(),
        glyphs=(),
        pages=(),
        furniture=(),
        hidden=(),
        undecodable=(),
        tracked_changes=(),
        warnings=(),
    )


def _evidence(sentence: int, quote: Span) -> Evidence:
    return Evidence(
        clause_id=ClauseId("c1"),
        sentence_ids=(SentenceId(f"c1.s{sentence}"),),
        quote=quote,
        placed=True,
    )


def test_exact_quote_passes() -> None:
    evidence = _evidence(3, Span(start=44, end=60))
    result = check_before_drawing(_document(), _clause(), evidence, "Late fees apply.")
    assert result == DrawAllowed(evidence=evidence)


def test_curly_quotes_and_spaces_pass() -> None:
    document = _document(CURLY_TEXT)
    clause = _clause(CURLY_TEXT)
    region = Span(start=44, end=64)
    fold = fold_for_quote_check(document.text[region.start : region.end])
    needle = fold_for_quote_check('Late "fees" apply.').text
    start_index = fold.text.index(needle)
    quote = Span(
        start=region.start + fold.to_original[start_index],
        end=region.start + fold.to_original[start_index + len(needle) - 1] + 1,
    )
    evidence = Evidence(
        clause_id=ClauseId("c1"),
        sentence_ids=(SentenceId("c1.s3"),),
        quote=quote,
        placed=True,
    )
    result = check_before_drawing(document, clause, evidence, 'Late "fees" apply.')
    assert result == DrawAllowed(evidence=evidence)


def test_quote_twice_in_cited_sentences_fails() -> None:
    evidence = Evidence(
        clause_id=ClauseId("c1"),
        sentence_ids=(SentenceId("c1.s2"), SentenceId("c1.s3"), SentenceId("c1.s4")),
        quote=Span(start=12, end=43),
        placed=True,
    )
    result = check_before_drawing(
        _document(), _clause(), evidence, "The Client pays within 60 days."
    )
    assert result == DrawRefused(failure=DrawFailure.QUOTE_NOT_UNIQUE)


def test_quote_outside_cited_sentences_fails() -> None:
    evidence = _evidence(2, Span(start=12, end=30))
    result = check_before_drawing(_document(), _clause(), evidence, "Late fees apply.")
    assert result == DrawRefused(failure=DrawFailure.QUOTE_NOT_FOUND)


def test_one_changed_character_fails() -> None:
    # Promise test: no made-up quote reaches the screen (Spec 11, unit part).
    evidence = _evidence(3, Span(start=44, end=60))
    result = check_before_drawing(_document(), _clause(), evidence, "Late fees apply!")
    assert isinstance(result, DrawRefused)


def test_wrong_span_fails() -> None:
    evidence = _evidence(3, Span(start=45, end=61))
    result = check_before_drawing(_document(), _clause(), evidence, "Late fees apply.")
    assert result == DrawRefused(failure=DrawFailure.SPAN_MISMATCH)


def test_unknown_sentence_fails() -> None:
    wrong_id = Evidence(
        clause_id=ClauseId("c1"),
        sentence_ids=(SentenceId("c1.s9"),),
        quote=Span(start=44, end=60),
        placed=True,
    )
    no_sentences = Evidence(
        clause_id=ClauseId("c1"), sentence_ids=(), quote=Span(start=44, end=60), placed=True
    )
    for evidence in (wrong_id, no_sentences):
        result = check_before_drawing(_document(), _clause(), evidence, "Late fees apply.")
        assert result == DrawRefused(failure=DrawFailure.SENTENCE_UNKNOWN), evidence


def test_other_clause_fails() -> None:
    evidence = Evidence(
        clause_id=ClauseId("c2"),
        sentence_ids=(SentenceId("c1.s3"),),
        quote=Span(start=44, end=60),
        placed=True,
    )
    result = check_before_drawing(_document(), _clause(), evidence, "Late fees apply.")
    assert result == DrawRefused(failure=DrawFailure.CLAUSE_MISMATCH)


def test_empty_quote_fails() -> None:
    evidence = _evidence(3, Span(start=44, end=60))
    result = check_before_drawing(_document(), _clause(), evidence, "  ")
    assert result == DrawRefused(failure=DrawFailure.EMPTY_QUOTE)


def test_offsets_count_code_points() -> None:
    text = "\U0001f600 The Client pays within 60 days."
    document = _document(text)
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
    start = text.index("The Client")
    evidence = Evidence(
        clause_id=ClauseId("c1"),
        sentence_ids=(SentenceId("c1.s1"),),
        quote=Span(start=start, end=start + len("The Client pays within 60 days.")),
        placed=True,
    )
    result = check_before_drawing(document, clause, evidence, "The Client pays within 60 days.")
    assert result == DrawAllowed(evidence=evidence)


def _glyphed_document(
    text: str = FULL_TEXT,
    *,
    box: PageBox | None = None,
    char_map: tuple[int | None, ...] | None = None,
    glyphs: tuple[Glyph, ...] | None = None,
    pages: tuple[Page, ...] | None = None,
) -> Document:
    default_box = box if box is not None else PageBox(page=1, x0=0, top=0, x1=5, bottom=10)
    default_glyphs = (
        glyphs if glyphs is not None else tuple(Glyph(page=1, box=default_box) for _ in text)
    )
    default_char_map = char_map if char_map is not None else tuple(range(len(text)))
    default_pages = pages if pages is not None else (Page(number=1, width=600.0, height=800.0),)
    return Document(
        schema_version=1,
        source=A_SOURCE,
        text=text,
        char_map=default_char_map,
        glyphs=default_glyphs,
        pages=default_pages,
        furniture=(),
        hidden=(),
        undecodable=(),
        tracked_changes=(),
        warnings=(),
    )


def test_box_inside_page_passes() -> None:
    evidence = _evidence(3, Span(start=44, end=60))
    result = check_before_drawing(_glyphed_document(), _clause(), evidence, "Late fees apply.")
    assert result == DrawAllowed(evidence=evidence)


def test_box_past_page_edge_fails() -> None:
    document = _glyphed_document(box=PageBox(page=1, x0=0, top=0, x1=601, bottom=10))
    evidence = _evidence(3, Span(start=44, end=60))
    result = check_before_drawing(document, _clause(), evidence, "Late fees apply.")
    assert result == DrawRefused(failure=DrawFailure.BOX_OUTSIDE_PAGE)


def test_character_without_glyph_fails() -> None:
    char_map = tuple(range(44)) + (999,) + tuple(range(45, len(FULL_TEXT)))
    document = _glyphed_document(char_map=char_map)
    evidence = _evidence(3, Span(start=44, end=60))
    result = check_before_drawing(document, _clause(), evidence, "Late fees apply.")
    assert result == DrawRefused(failure=DrawFailure.GLYPH_MISSING)


def test_inserted_characters_need_no_box() -> None:
    char_map = tuple(range(44)) + (None,) + tuple(range(45, len(FULL_TEXT)))
    document = _glyphed_document(char_map=char_map)
    evidence = _evidence(3, Span(start=44, end=60))
    result = check_before_drawing(document, _clause(), evidence, "Late fees apply.")
    assert result == DrawAllowed(evidence=evidence)


def test_ligature_passes() -> None:
    # Two characters pointing at one glyph, as a ligature does.
    glyph_count = len(FULL_TEXT) - 1
    char_map = tuple(range(45)) + (44,) + tuple(range(45, glyph_count))
    document = _glyphed_document(
        char_map=char_map,
        glyphs=tuple(
            Glyph(page=1, box=PageBox(page=1, x0=0, top=0, x1=5, bottom=10))
            for _ in range(glyph_count)
        ),
    )
    evidence = _evidence(3, Span(start=44, end=60))
    result = check_before_drawing(document, _clause(), evidence, "Late fees apply.")
    assert result == DrawAllowed(evidence=evidence)


def test_unknown_page_fails() -> None:
    document = _glyphed_document(
        box=PageBox(page=2, x0=0, top=0, x1=5, bottom=10),
        glyphs=tuple(
            Glyph(page=2, box=PageBox(page=2, x0=0, top=0, x1=5, bottom=10)) for _ in FULL_TEXT
        ),
    )
    evidence = _evidence(3, Span(start=44, end=60))
    result = check_before_drawing(document, _clause(), evidence, "Late fees apply.")
    assert result == DrawRefused(failure=DrawFailure.PAGE_UNKNOWN)


def test_page_mismatch_fails() -> None:
    document = _glyphed_document(
        glyphs=tuple(
            Glyph(page=1, box=PageBox(page=2, x0=0, top=0, x1=5, bottom=10)) for _ in FULL_TEXT
        )
    )
    evidence = _evidence(3, Span(start=44, end=60))
    result = check_before_drawing(document, _clause(), evidence, "Late fees apply.")
    assert result == DrawRefused(failure=DrawFailure.PAGE_MISMATCH)


def test_char_map_length_fails() -> None:
    document = _glyphed_document(char_map=tuple(range(len(FULL_TEXT) - 1)))
    evidence = _evidence(3, Span(start=44, end=60))
    result = check_before_drawing(document, _clause(), evidence, "Late fees apply.")
    assert result == DrawRefused(failure=DrawFailure.CHAR_MAP_LENGTH)


def test_document_without_glyphs_skips_boxes() -> None:
    evidence = _evidence(3, Span(start=44, end=60))
    result = check_before_drawing(_document(), _clause(), evidence, "Late fees apply.")
    assert result == DrawAllowed(evidence=evidence)


@given(documents_with_quote())
def test_invariant_7_last_check_agrees(
    built: tuple[Document, Clause, Evidence, str],
) -> None:
    # Promise test: every evidence link scrolls to the right place
    # (Spec 11, unit part): invariant 7, the last check agrees.
    document, clause, evidence, quote_text = built
    result = check_before_drawing(document, clause, evidence, quote_text)
    assert result == DrawAllowed(evidence=evidence)


_UNPAIRED_QUOTES = "'\"‘’“”"


@given(built=documents_with_quote(), choice=st.integers(0, 79))
@example(
    built=(
        _document(),
        _clause(),
        _evidence(3, Span(start=44, end=60)),
        "Late fees apply.",
    ),
    choice=0,
)
def test_invariant_7_changed_character_fails(
    built: tuple[Document, Clause, Evidence, str], choice: int
) -> None:
    # Promise test: every evidence link scrolls to the right place
    # (Spec 11, unit part): changing one character of the quote fails.
    document, clause, evidence, quote_text = built
    pickable = [
        index
        for index, character in enumerate(quote_text)
        if not character.isspace() and character not in _UNPAIRED_QUOTES
    ]
    assume(len(pickable) > 0)
    picked = pickable[choice % len(pickable)]
    original_character = quote_text[picked]
    replacement = "Y" if original_character == "X" else "X"
    changed = quote_text[:picked] + replacement + quote_text[picked + 1 :]
    result = check_before_drawing(document, clause, evidence, changed)
    assert isinstance(result, DrawRefused)
