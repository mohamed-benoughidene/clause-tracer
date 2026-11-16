"""Tests for reading positions, playbooks and label inputs from the sample format."""

import tomllib
from decimal import Decimal

import pytest

from clause_tracer.core.enums import Direction, Level, PositionType, Unit
from clause_tracer.core.ids import PlaybookId, PositionId
from clause_tracer.core.playbook import NumberRule, Playbook, Position, WordsRule
from clause_tracer.core.results import (
    CallFailed,
    CheckedValue,
    Evidence,
    JudgedLevel,
    MatchFound,
    MatchUnconfirmed,
    NothingFound,
    UnreadableSpans,
)
from clause_tracer.core.sample_input import (
    Sample,
    parse_label_inputs,
    parse_playbook,
    parse_position,
    parse_sample,
)
from clause_tracer.core.wording import Span

WHERE = "position 0"


def _data(text: str) -> dict[str, object]:
    return tomllib.loads(text)


def _number_position(position_id: str) -> Position:
    return Position(
        id=PositionId(position_id),
        topic="t",
        type=PositionType.NUMBER,
        rule=NumberRule(
            unit=Unit.DAYS,
            direction=Direction.LOWER_IS_BETTER,
            preferred_limit=Decimal(15),
            acceptable_limit=Decimal(30),
        ),
        missing_level=Level.UNSURE,
        why_note=None,
    )


def _words_position(position_id: str) -> Position:
    return Position(
        id=PositionId(position_id),
        topic="t",
        type=PositionType.WORDS,
        rule=WordsRule(preferred="p", acceptable="a", walk_away="w"),
        missing_level=Level.WALK_AWAY,
        why_note=None,
    )


def _playbook(*positions: Position) -> Playbook:
    return Playbook(
        id=PlaybookId("test"),
        schema_version=1,
        name="Test",
        side="test",
        customer_id=None,
        positions=tuple(positions),
        starter=False,
    )


def test_number_position() -> None:
    position = parse_position(
        _data(
            """
            id = "1"
            topic = "Days until I'm paid, from invoice date"
            type = "number"
            unit = "days"
            direction = "lower_is_better"
            preferred_limit = "15"
            acceptable_limit = 30
            missing_level = "unsure"
            """
        ),
        WHERE,
    )
    assert position.id == "1"
    assert position.topic == "Days until I'm paid, from invoice date"
    assert position.type is PositionType.NUMBER
    rule = position.rule
    assert isinstance(rule, NumberRule)
    assert rule.unit is Unit.DAYS
    assert rule.direction is Direction.LOWER_IS_BETTER
    assert rule.preferred_limit == Decimal("15")
    assert isinstance(rule.preferred_limit, Decimal)
    assert rule.acceptable_limit == Decimal(30)
    assert position.missing_level is Level.UNSURE
    assert position.why_note is None


def test_yes_no_missing_level_defaults_to_no_level() -> None:
    position = parse_position(
        _data(
            """
            id = "3"
            topic = "Late payment fee exists"
            type = "yes_no"
            question = "Does the contract name a late payment fee?"
            yes_level = "preferred"
            no_level = "acceptable"
            """
        ),
        WHERE,
    )
    assert position.missing_level is Level.ACCEPTABLE


def test_yes_no_missing_level_given_is_kept() -> None:
    position = parse_position(
        _data(
            """
            id = "3"
            topic = "Late payment fee exists"
            type = "yes_no"
            question = "Does the contract name a late payment fee?"
            yes_level = "preferred"
            no_level = "acceptable"
            missing_level = "preferred"
            """
        ),
        WHERE,
    )
    assert position.missing_level is Level.PREFERRED


def test_words_position() -> None:
    position = parse_position(
        _data(
            """
            id = "10"
            topic = "My liability is capped"
            type = "words"
            preferred = "At most the fees paid"
            acceptable = "Above the fees, up to 2x fees"
            walk_away = "Above 2x fees, a fixed sum, or uncapped"
            missing_level = "walk_away"
            why_note = "A cap keeps the worst case known."
            """
        ),
        WHERE,
    )
    assert position.type is PositionType.WORDS
    words = position.rule
    assert isinstance(words, WordsRule)
    assert words.preferred == "At most the fees paid"
    assert words.acceptable == "Above the fees, up to 2x fees"
    assert words.walk_away == "Above 2x fees, a fixed sum, or uncapped"
    assert position.missing_level is Level.WALK_AWAY
    assert position.why_note == "A cap keeps the worst case known."


def test_unknown_key_raises() -> None:
    with pytest.raises(ValueError, match="junk"):
        parse_position(
            _data(
                """
                id = "1"
                topic = "t"
                type = "number"
                unit = "days"
                direction = "lower_is_better"
                preferred_limit = "15"
                acceptable_limit = "30"
                missing_level = "unsure"
                junk = "1"
                """
            ),
            WHERE,
        )


def test_float_limit_raises() -> None:
    with pytest.raises(ValueError, match="preferred_limit"):
        parse_position(
            _data(
                """
                id = "1"
                topic = "t"
                type = "number"
                unit = "days"
                direction = "lower_is_better"
                preferred_limit = 1.5
                acceptable_limit = "30"
                missing_level = "unsure"
                """
            ),
            WHERE,
        )


def test_playbook_fields() -> None:
    playbook = parse_playbook(
        _data(
            """
            id = "starter-freelancer"
            name = "Freelancer receiving a service agreement"
            side = "service provider"
            starter = true

            [[positions]]
            id = "1"
            topic = "Days until paid"
            type = "number"
            unit = "days"
            direction = "lower_is_better"
            preferred_limit = "15"
            acceptable_limit = "30"
            missing_level = "unsure"

            [[positions]]
            id = "3"
            topic = "Late payment fee exists"
            type = "yes_no"
            question = "Does the contract name a late payment fee?"
            yes_level = "preferred"
            no_level = "acceptable"
            """
        ),
        schema_version=1,
    )
    assert playbook.id == "starter-freelancer"
    assert playbook.name == "Freelancer receiving a service agreement"
    assert playbook.side == "service provider"
    assert playbook.starter is True
    assert [position.id for position in playbook.positions] == ["1", "3"]
    assert playbook.customer_id is None
    assert playbook.schema_version == 1


def _entry(**changes: object) -> dict[str, object]:
    entry: dict[str, object] = {"position": "1", "match": "found"}
    entry.update(changes)
    return entry


def test_found_value_builds_checked_value_and_evidence() -> None:
    inputs, unreadable = parse_label_inputs(
        [_entry(values=[{"clause": "c1", "number": "60", "unit": "days"}])],
        _playbook(_number_position("1")),
    )
    assert len(inputs) == 1
    assert unreadable.hidden == ()
    assert unreadable.undecodable == ()
    assert len(inputs[0].values) == 1
    value = inputs[0].values[0]
    assert isinstance(value, CheckedValue)
    assert value.position_id == "1"
    assert value.clause_id == "c1"
    assert value.number == Decimal("60")
    assert value.unit_as_written == "days"
    evidence = value.evidence
    assert isinstance(evidence, Evidence)
    assert evidence.clause_id == "c1"
    assert evidence.sentence_ids == ("c1.s1",)
    assert evidence.quote == Span(start=0, end=10)
    assert evidence.placed is True


def test_quote_none_has_no_evidence() -> None:
    inputs, unreadable = parse_label_inputs(
        [
            _entry(
                values=[{"clause": "c4", "answer": "no", "quote": "none"}],
            )
        ],
        _playbook(_number_position("1")),
    )
    assert inputs[0].values[0].evidence is None
    assert unreadable.hidden == ()
    assert unreadable.undecodable == ()


def test_unplaced_quote_has_placed_false() -> None:
    inputs, _ = parse_label_inputs(
        [_entry(values=[{"clause": "c1", "number": "60", "quote": "unplaced"}])],
        _playbook(_number_position("1")),
    )
    evidence = inputs[0].values[0].evidence
    assert isinstance(evidence, Evidence)
    assert evidence.placed is False


def test_spans_count_across_entries() -> None:
    inputs, _ = parse_label_inputs(
        [
            _entry(
                position="1",
                values=[{"clause": "c1", "number": "60"}, {"clause": "c2", "number": "60"}],
            ),
            _entry(position="2", values=[{"clause": "c3", "number": "60"}]),
        ],
        _playbook(_number_position("1"), _number_position("2")),
    )
    third = inputs[1].values[0].evidence
    assert isinstance(third, Evidence)
    assert third.quote == Span(start=200, end=210)


def test_hidden_and_undecodable_spans_collected() -> None:
    inputs, unreadable = parse_label_inputs(
        [
            _entry(
                position="1",
                values=[
                    {"clause": "c1", "number": "60", "on": "hidden"},
                    {"clause": "c2", "number": "60", "on": "undecodable"},
                ],
            )
        ],
        _playbook(_number_position("1")),
    )
    assert unreadable.hidden == (Span(start=0, end=10),)
    assert unreadable.undecodable == (Span(start=100, end=110),)
    first = inputs[0].values[0].evidence
    assert isinstance(first, Evidence)
    assert first.placed is True


def test_match_kinds() -> None:
    inputs, _ = parse_label_inputs(
        [
            _entry(position="1", match="found", values=[{"clause": "c1", "number": "60"}]),
            _entry(position="2", match="nothing"),
            _entry(position="3", match="unconfirmed", clauses_to_read=["c7", "c8"]),
            _entry(position="4", match="failed"),
        ],
        _playbook(
            _number_position("1"),
            _number_position("2"),
            _number_position("3"),
            _number_position("4"),
        ),
    )
    assert isinstance(inputs[0].match, MatchFound)
    assert inputs[0].match.clause_ids == ("c1",)
    assert isinstance(inputs[1].match, NothingFound)
    assert inputs[1].match.searches == ()
    assert isinstance(inputs[2].match, MatchUnconfirmed)
    assert inputs[2].match.clauses_to_read == ("c7", "c8")
    assert isinstance(inputs[3].match, CallFailed)
    assert inputs[3].match.code == "model_reply_invalid"


def test_unknown_position_raises() -> None:
    with pytest.raises(ValueError, match="unknown position"):
        parse_label_inputs([_entry(position="9")], _playbook(_number_position("1")))


def test_judged_level() -> None:
    inputs, _ = parse_label_inputs(
        [_entry(position="10", match="found", judged=[{"clause": "c10", "level": "acceptable"}])],
        _playbook(_words_position("10")),
    )
    assert len(inputs[0].judged) == 1
    judged = inputs[0].judged[0]
    assert isinstance(judged, JudgedLevel)
    assert judged.position_id == "10"
    assert judged.clause_id == "c10"
    assert judged.level is Level.ACCEPTABLE
    evidence = judged.evidence
    assert isinstance(evidence, Evidence)
    assert evidence.clause_id == "c10"


def test_parse_sample_top_level() -> None:
    sample = parse_sample(
        _data(
            """
            schema_version = 1

            [playbook]
            id = "starter-freelancer"
            name = "Freelancer"
            side = "service provider"
            starter = true

            [[playbook.positions]]
            id = "1"
            topic = "Days until paid"
            type = "number"
            unit = "days"
            direction = "lower_is_better"
            preferred_limit = "15"
            acceptable_limit = "30"
            missing_level = "unsure"

            [[input]]
            position = "1"
            match = "found"
            values = [{ clause = "c1", number = "60" }]
            """
        )
    )
    assert isinstance(sample, Sample)
    assert sample.playbook.id == "starter-freelancer"
    assert sample.playbook.schema_version == 1
    assert [str(input.position.id) for input in sample.inputs] == ["1"]
    assert sample.unreadable == UnreadableSpans(hidden=(), undecodable=())
