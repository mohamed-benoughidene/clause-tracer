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
    return DrawAllowed(evidence=evidence)
