"""Build small privacy cases without `ingest` (S4-M1-T5).

Test code, not exported from `privacy`. One clause holds the sentences, and
the clause and sentence spans tile the text (T3, S2).
"""

import hashlib
from collections.abc import Sequence

from clause_tracer.core import (
    Clause,
    ClauseId,
    DefinedTerm,
    Document,
    FileKind,
    Party,
    PiiSource,
    PiiSuggestion,
    PlaceholderKind,
    Sentence,
    SentenceId,
    SourceFile,
    Span,
)
from clause_tracer.privacy import PrivacyInput


def make_case(
    sentences: Sequence[str],
    *,
    parties: Sequence[Party] = (),
    terms: Sequence[DefinedTerm] = (),
) -> PrivacyInput:
    """Build a pasted-text document with one clause over the sentences.

    Input:   the sentence texts, and optional parties and defined terms.
    Output:  the privacy input, with spans that tile the text.
    Raises:  ValueError for an empty sentence or one with a line break.
    Effects: none (T1).
    """

    for sentence in sentences:
        if sentence == "" or "\n" in sentence or "\r" in sentence:
            raise ValueError("a sentence must be non-empty and hold no line break")

    text = " ".join(sentences)
    document = Document(
        schema_version=1,
        source=SourceFile(
            name="case.txt",
            kind=FileKind.PASTED,
            sha256=hashlib.sha256(text.encode()).hexdigest(),
            size=len(text.encode()),
        ),
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
    if not sentences:
        return PrivacyInput(
            document=document,
            clauses=(),
            parties=tuple(parties),
            terms=tuple(terms),
        )

    built: list[Sentence] = []
    offset = 0
    last = len(sentences) - 1
    for index, sentence_text in enumerate(sentences):
        start = offset
        end = start + len(sentence_text) + (0 if index == last else 1)
        built.append(Sentence(id=SentenceId(f"1.s{index + 1}"), span=Span(start=start, end=end)))
        offset = end
    clause = Clause(
        id=ClauseId("1"),
        number="1",
        heading=None,
        level=1,
        parent_id=None,
        span=Span(start=0, end=len(text)),
        numbering_source="numbers",
        sentences=tuple(built),
    )
    return PrivacyInput(
        document=document,
        clauses=(clause,),
        parties=tuple(parties),
        terms=tuple(terms),
    )


def span_of(text: str, needle: str, nth: int = 1) -> Span:
    """Return the span of the nth occurrence of `needle` in `text`."""

    if nth < 1:
        raise AssertionError("nth must be 1 or more")
    start = -1
    for _ in range(nth):
        start = text.find(needle, start + 1)
        if start == -1:
            raise AssertionError(f"{needle!r} occurs fewer than {nth} times")
    return Span(start=start, end=start + len(needle))


def suggestion(
    text: str,
    needle: str,
    kind: PlaceholderKind,
    source: PiiSource,
    nth: int = 1,
) -> PiiSuggestion:
    """Build a suggestion over the nth occurrence of `needle` in `text`."""

    return PiiSuggestion(span=span_of(text, needle, nth), kind=kind, source=source)
