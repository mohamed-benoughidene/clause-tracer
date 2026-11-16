"""Tests for reading positions, playbooks and label inputs from the sample format."""

import tomllib
from decimal import Decimal

import pytest

from clause_tracer.core.enums import Direction, Level, PositionType, Unit
from clause_tracer.core.playbook import NumberRule, WordsRule
from clause_tracer.core.sample_input import parse_playbook, parse_position

WHERE = "position 0"


def _data(text: str) -> dict[str, object]:
    return tomllib.loads(text)


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
