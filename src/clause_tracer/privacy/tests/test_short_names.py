"""Short names of found companies (S4-M2-T5)."""

import pytest

from clause_tracer.core import DefinedTerm, Party, PiiSource, PlaceholderKind
from clause_tracer.privacy.companies import find_companies
from clause_tracer.privacy.short_names import find_short_names
from clause_tracer.privacy.tests.case_builder import span_of


def found(
    text: str, parties: tuple[Party, ...] = (), terms: tuple[DefinedTerm, ...] = ()
) -> list[tuple[str, int, int]]:
    result = find_short_names(text, find_companies(text), parties, terms)
    for item in result:
        assert item.kind == PlaceholderKind.COMPANY
        assert item.source == PiiSource.RULE
    return [(text[s.span.start : s.span.end], s.span.start, s.span.end) for s in result]


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        pytest.param(
            "Beta Gadgets, Inc. signs. Beta Gadgets pays.",
            [("Beta Gadgets", 0, 12), ("Beta Gadgets", 26, 38)],
            id="several_words",
        ),
        pytest.param(
            "Gizmotron, Inc. signs. Gizmotron pays.",
            [("Gizmotron", 0, 9), ("Gizmotron", 23, 32)],
            id="one_word",
        ),
        pytest.param(
            "Mercury, Inc. signs. Mercury pays. No mercury here.", [], id="one_word_in_small"
        ),
        pytest.param(
            "Gizmotron, Inc. signs. Gizmotron pays. Mail a@gizmotron.com now.",
            [("Gizmotron", 0, 9), ("Gizmotron", 23, 32)],
            id="small_in_address",
        ),
        pytest.param(
            "Beta Gadgets Inc. sells beta gadgets.",
            [("Beta Gadgets", 0, 12)],
            id="small_copy_stays",
        ),
        pytest.param("Contractor, Inc. signs. Contractor pays.", [], id="role_word"),
        pytest.param("England Ltd signs. England pays.", [], id="listed_place"),
        pytest.param("Beta (Shanghai) Co, Ltd signs. Co pays.", [], id="only_an_ending"),
        pytest.param("Rose, Inc. signs. Rose pays.", [], id="common_word"),
    ],
)
def test_short_names(text: str, expected: list[tuple[str, int, int]]) -> None:
    assert find_companies(text)
    assert found(text) == expected


@pytest.mark.parametrize(
    ("text", "term", "sentence", "expected"),
    [
        pytest.param(
            'Beta Gadgets, Inc. ("Beta") signs. Beta pays.',
            "Beta",
            'Beta Gadgets, Inc. ("Beta") signs.',
            [("Beta", 0, 4), ("Beta Gadgets", 0, 12), ("Beta", 21, 25), ("Beta", 35, 39)],
            id="made_of_the_name",
        ),
        pytest.param(
            'Beta Gadgets, Inc. ("BetaG") signs. BetaG pays.',
            "BetaG",
            'Beta Gadgets, Inc. ("BetaG") signs.',
            [("Beta Gadgets", 0, 12)],
            id="other_word",
        ),
        pytest.param(
            'Beta Gadgets, Inc. signs. "Beta" pays.',
            "Beta",
            '"Beta" pays.',
            [("Beta Gadgets", 0, 12)],
            id="name_not_in_definition",
        ),
        pytest.param(
            'Mercury, Inc. ("Mercury") signs. Mercury pays. No mercury here.',
            "Mercury",
            'Mercury, Inc. ("Mercury") signs.',
            [("Mercury", 0, 7), ("Mercury", 16, 23), ("Mercury", 33, 40)],
            id="one_word_in_small",
        ),
        pytest.param(
            'Beta Services, Inc. ("Services") signs. Services start.',
            "Services",
            'Beta Services, Inc. ("Services") signs.',
            [("Beta Services", 0, 13)],
            id="a_legal_word",
        ),
    ],
)
def test_nicknames(
    text: str, term: str, sentence: str, expected: list[tuple[str, int, int]]
) -> None:
    defined = DefinedTerm(term=term, definition=span_of(text, sentence), uses=())

    assert found(text, terms=(defined,)) == expected


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        pytest.param("Beta Gadgets Corporation", [], id="read_as_a_person"),
        pytest.param(
            "Beta Gadgets Inc.",
            [("Beta Gadgets", 0, 12), ("Beta Gadgets", 25, 37)],
            id="read_as_a_company",
        ),
    ],
)
def test_typed_parties(name: str, expected: list[tuple[str, int, int]]) -> None:
    party = Party(name=name, address=None, yours=False)

    assert found("Beta Gadgets Inc. signs. Beta Gadgets pays.", parties=(party,)) == expected
