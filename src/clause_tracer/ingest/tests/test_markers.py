"""Tests for finding a clause marker at the start of a line (S2-M3-T3)."""

import pytest

from clause_tracer.ingest._markers import (
    Marker,
    MarkerKind,
    find_marker,
    is_heading_line,
)


def marker(
    kind: MarkerKind,
    parts: tuple[int, ...],
    token: str,
    written: str,
    id_part: str,
    body_start: int,
) -> Marker:
    return Marker(
        kind=kind,
        parts=parts,
        token=token,
        written=written,
        id_part=id_part,
        body_start=body_start,
    )


@pytest.mark.parametrize(
    ("line", "expected"),
    [
        ("5. Charges", marker(MarkerKind.DECIMAL, (5,), "", "5", "5", 3)),
        ("5.1 The Agency", marker(MarkerKind.DECIMAL, (5, 1), "", "5.1", "5.1", 4)),
        ("5.1. The Agency", marker(MarkerKind.DECIMAL, (5, 1), "", "5.1", "5.1", 5)),
        (
            "  12.3.4\tText",
            marker(MarkerKind.DECIMAL, (12, 3, 4), "", "12.3.4", "12.3.4", 9),
        ),
        ("05. Old style", marker(MarkerKind.DECIMAL, (5,), "", "05", "5", 4)),
        ("7.", marker(MarkerKind.DECIMAL, (7,), "", "7", "7", 2)),
        ("5 November 2026", None),
        ("12.11.2026 is the date", None),
        ("2026. A year", None),
        ("5.1The Agency", None),
        ("1.2.3.4.5.6 too deep", None),
        ("\ufeff1. First", marker(MarkerKind.DECIMAL, (1,), "", "1", "1", 4)),
        ("## 3. The Services", marker(MarkerKind.DECIMAL, (3,), "", "3", "3", 6)),
        ("**5.1** The Agency", marker(MarkerKind.DECIMAL, (5, 1), "", "5.1", "5.1", 8)),
        ("(a) first", marker(MarkerKind.PAREN, (), "a", "(a)", "(a)", 4)),
        ("(iv) fourth", marker(MarkerKind.PAREN, (), "iv", "(iv)", "(iv)", 5)),
        ("(A) The Agency", marker(MarkerKind.PAREN, (), "A", "(A)", "(A)", 4)),
        ("(12) twelve", marker(MarkerKind.PAREN, (), "12", "(12)", "(12)", 5)),
        ("(the Agency) will", None),
        ("(a)first", None),
        ("a) first", marker(MarkerKind.PAREN, (), "a", "a)", "(a)", 3)),
        ("ii) components", marker(MarkerKind.PAREN, (), "ii", "ii)", "(ii)", 4)),
        (
            "Schedule 1 · Services and Charges",
            marker(MarkerKind.SCHEDULE, (), "S1", "Schedule 1", "S1", 11),
        ),
        ("SCHEDULE 2", marker(MarkerKind.SCHEDULE, (), "S2", "SCHEDULE 2", "S2", 10)),
        ("Annex A: Rates", marker(MarkerKind.SCHEDULE, (), "AA", "Annex A", "AA", 7)),
        ("Schedule 1 conflict, this Agreement prevails.", None),
        ("Schedule 12a", None),
        ("The Schedule 1", None),
        (
            "Article IV Payment",
            marker(MarkerKind.KEYWORD, (4,), "", "Article IV", "4", 11),
        ),
        (
            "Article IV. Payment",
            marker(MarkerKind.KEYWORD, (4,), "", "Article IV", "4", 12),
        ),
        ("ARTICLE 4", marker(MarkerKind.KEYWORD, (4,), "", "ARTICLE 4", "4", 9)),
        ("Clause 5: Fees", marker(MarkerKind.KEYWORD, (5,), "", "Clause 5", "5", 10)),
        (
            "clause 12 – Notices",
            marker(MarkerKind.KEYWORD, (12,), "", "clause 12", "12", 12),
        ),
        ("Clause 5 applies to notices.", None),
        ("Article 4.1 Terms", None),
        ("Article IIII Bad", None),
        ("3 Payment", marker(MarkerKind.BARE, (3,), "", "3", "3", 2)),
        ("**3** Payment", marker(MarkerKind.BARE, (3,), "", "3", "3", 6)),
        ("30 days' notice", None),
        ("1 January 2027", None),
        ("3 Build\tWeek 6", None),
        ("1000 Things", None),
        ("2 Build Templates.", None),
        ("03 Old", None),
        ("", None),
    ],
)
def test_find_marker(line: str, expected: Marker | None) -> None:
    assert find_marker(line) == expected


@pytest.mark.parametrize(
    ("line", "expected"),
    [
        ("Background", True),
        ("## Parties", True),
        ("Signed by Karim Benali", True),
        ("the Developer", False),
        ("The work is done.", False),
        ("Milestone\tWork", False),
        ("", False),
        ("A" * 61, False),
        ("One two three four five six seven eight nine", False),
    ],
)
def test_is_heading_line(line: str, expected: bool) -> None:
    assert is_heading_line(line) is expected
