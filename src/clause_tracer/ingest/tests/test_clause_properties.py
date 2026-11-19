"""Property tests for the clause splitter (S2-M3-T10)."""

from hypothesis import given

from clause_tracer.core import FileKind
from clause_tracer.ingest import read_pasted_text, read_text_file, split_clauses
from clause_tracer.ingest.tests.strategies import contract_like_text


@given(text=contract_like_text())
def test_clauses_cover_the_text(text: str) -> None:
    clauses = split_clauses(read_pasted_text(text))

    assert clauses
    assert clauses[0].span.start == 0
    assert clauses[-1].span.end == len(text)
    for earlier, later in zip(clauses, clauses[1:], strict=False):
        assert earlier.span.end == later.span.start
    for clause in clauses:
        assert clause.span.start < clause.span.end


# Promise test (Spec 11): every evidence link scrolls to the right place,
# because each sentence id names a span that lies inside one clause.
@given(text=contract_like_text())
def test_invariant_4_sentences_join_up_to_the_clause(text: str) -> None:
    clauses = split_clauses(read_pasted_text(text))

    for clause in clauses:
        sentences = clause.sentences
        assert sentences
        assert sentences[0].span.start == clause.span.start
        assert sentences[-1].span.end == clause.span.end
        for earlier, later in zip(sentences, sentences[1:], strict=False):
            assert earlier.span.end == later.span.start
        for index, sentence in enumerate(sentences, start=1):
            assert sentence.span.start < sentence.span.end
            assert str(sentence.id) == f"{clause.id}.s{index}"


@given(text=contract_like_text())
def test_invariant_4_ids_are_the_same_on_a_second_read(text: str) -> None:
    from_paste = split_clauses(read_pasted_text(text))
    from_file = split_clauses(read_text_file(text.encode(), kind=FileKind.TEXT, name="a.txt"))

    assert from_paste == from_file


@given(text=contract_like_text())
def test_ids_are_unique(text: str) -> None:
    clauses = split_clauses(read_pasted_text(text))

    clause_ids = [str(clause.id) for clause in clauses]
    sentence_ids = [str(sentence.id) for clause in clauses for sentence in clause.sentences]

    assert len(clause_ids) == len(set(clause_ids))
    assert len(sentence_ids) == len(set(sentence_ids))


@given(text=contract_like_text())
def test_parents_come_first(text: str) -> None:
    clauses = split_clauses(read_pasted_text(text))

    seen: set[str] = set()
    levels: dict[str, int] = {}
    for clause in clauses:
        clause_id = str(clause.id)
        if clause.parent_id is None:
            assert clause.level == 1
        else:
            parent_id = str(clause.parent_id)
            assert parent_id in seen
            assert clause.level == levels[parent_id] + 1
        seen.add(clause_id)
        levels[clause_id] = clause.level
