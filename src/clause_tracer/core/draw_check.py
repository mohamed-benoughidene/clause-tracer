"""The last check before drawing (system design 4.2).

The same rule runs again, by a different code path, right before a
highlight is drawn. It shares only the fold with the stage 8 quote
check (system design 15.8). If it refuses, nothing is drawn and the
app says "Check [clause] yourself." The text half always runs; the
page-box half runs only when the document has glyphs (S1-M5-T12).
"""

from clause_tracer.core.checks import DrawAllowed, DrawRefused
from clause_tracer.core.document import Clause, Document
from clause_tracer.core.enums import DrawFailure
from clause_tracer.core.quote_fold import fold_for_quote_check
from clause_tracer.core.results import Evidence
from clause_tracer.core.wording import Span


def check_before_drawing(
    document: Document, clause: Clause, evidence: Evidence, quote_text: str
) -> DrawAllowed | DrawRefused:
    """Agree, by a different code path, that this evidence places this
    quote inside this clause. Stops at the first failure and refuses."""

    if evidence.clause_id != clause.id:
        return DrawRefused(failure=DrawFailure.CLAUSE_MISMATCH)
    known_sentence_ids = {sentence.id for sentence in clause.sentences}
    sentence_ids_empty = len(evidence.sentence_ids) == 0
    sentence_unknown = any(
        sentence_id not in known_sentence_ids for sentence_id in evidence.sentence_ids
    )
    if sentence_ids_empty or sentence_unknown:
        return DrawRefused(failure=DrawFailure.SENTENCE_UNKNOWN)
    cited = [sentence for sentence in clause.sentences if sentence.id in set(evidence.sentence_ids)]
    region = Span(
        start=min(sentence.span.start for sentence in cited),
        end=max(sentence.span.end for sentence in cited),
    )
    quote_inside_region = region.start <= evidence.quote.start and evidence.quote.end <= region.end
    if not quote_inside_region:
        return DrawRefused(failure=DrawFailure.SPAN_OUTSIDE_SENTENCES)
    folded_quote = fold_for_quote_check(quote_text).text.strip(" ")
    if folded_quote == "":
        return DrawRefused(failure=DrawFailure.EMPTY_QUOTE)
    folded_region = fold_for_quote_check(document.text[region.start : region.end])
    quote_length = len(folded_quote)
    places = [
        index
        for index in range(len(folded_region.text) - quote_length + 1)
        if folded_region.text[index : index + quote_length] == folded_quote
    ]
    if len(places) == 0:
        return DrawRefused(failure=DrawFailure.QUOTE_NOT_FOUND)
    if len(places) > 1:
        return DrawRefused(failure=DrawFailure.QUOTE_NOT_UNIQUE)
    place = places[0]
    start = region.start + folded_region.to_original[place]
    end = region.start + folded_region.to_original[place + quote_length - 1] + 1
    if Span(start=start, end=end) != evidence.quote:
        return DrawRefused(failure=DrawFailure.SPAN_MISMATCH)
    has_glyphs = len(document.glyphs) > 0
    if has_glyphs:
        char_map_matches_text = len(document.char_map) == len(document.text)
        if not char_map_matches_text:
            return DrawRefused(failure=DrawFailure.CHAR_MAP_LENGTH)
        for index in range(evidence.quote.start, evidence.quote.end):
            glyph_index = document.char_map[index]
            if glyph_index is None:
                continue
            if glyph_index < 0 or glyph_index >= len(document.glyphs):
                return DrawRefused(failure=DrawFailure.GLYPH_MISSING)
            glyph = document.glyphs[glyph_index]
            if glyph.page != glyph.box.page:
                return DrawRefused(failure=DrawFailure.PAGE_MISMATCH)
            page = next(
                (candidate for candidate in document.pages if candidate.number == glyph.page),
                None,
            )
            if page is None:
                return DrawRefused(failure=DrawFailure.PAGE_UNKNOWN)
            box = glyph.box
            box_inside_page = (
                0 <= box.x0 <= box.x1 <= page.width and 0 <= box.top <= box.bottom <= page.height
            )
            if not box_inside_page:
                return DrawRefused(failure=DrawFailure.BOX_OUTSIDE_PAGE)
    return DrawAllowed(evidence=evidence)
