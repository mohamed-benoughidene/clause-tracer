"""The pre-run cost estimate (system design 7, Spec 9).

The call count comes from the table in system design 7; the prices come
from the caller, so no price list enters core (ADR 0015). The range
runs from "the cache hits on every call" (low) to "the cache never
hits" (high). Every constant is an assumption until the first paid run.
"""

import math
from decimal import ROUND_HALF_UP, Decimal

from clause_tracer.core.checks import CallPrices, CostInputs, CostRange

TASK_TOKENS_PER_CALL = 1000
OUTPUT_TOKENS_PER_CALL = 400

_TOKENS_PER_MILLION = Decimal(1_000_000)
_COST_QUANTUM = Decimal("0.0001")
_REVERSE_MATCH_CLAUSES_PER_BATCH = 25
_PAIR_CHECK_POSITIONS_PER_CALL = 4


def _check_counts(positions: int, words_positions: int, clauses: int) -> None:
    a_count_is_negative = positions < 0 or words_positions < 0 or clauses < 0
    words_exceed_positions = words_positions > positions
    if a_count_is_negative or words_exceed_positions:
        raise ValueError("counts must be 0 or more, with words_positions <= positions")


def _check_prices(prices: CallPrices) -> None:
    a_price_is_negative = (
        prices.input_per_million < 0
        or prices.cached_input_per_million < 0
        or prices.output_per_million < 0
    )
    if a_price_is_negative:
        raise ValueError("prices must be 0 or more")


def estimate_calls(positions: int, words_positions: int, clauses: int) -> int:
    """The number of AI calls a review makes, from the table in system
    design 7: one forward match per position, reverse-match batches and
    sort-not-covered calls per 25 clauses, a pair check per 4 positions,
    an extraction per number or yes/no position, and a judge call and an
    explain call per words position."""

    _check_counts(positions, words_positions, clauses)
    reverse_match_batches = math.ceil(clauses / _REVERSE_MATCH_CLAUSES_PER_BATCH)
    pair_checks = math.ceil(positions / _PAIR_CHECK_POSITIONS_PER_CALL)
    extractions = positions - words_positions
    judges = words_positions
    explains = words_positions
    sorts = reverse_match_batches
    return positions + reverse_match_batches + pair_checks + extractions + judges + explains + sorts


def estimate_cost(inputs: CostInputs) -> CostRange:
    """The pre-run estimate: the call count, and the cost if the cache
    hits on every call (low) or never hits (high), rounded half up to
    $0.0001. Task tokens and output tokens are priced the same at both
    ends."""

    _check_counts(inputs.positions, inputs.words_positions, inputs.clauses)
    _check_prices(inputs.prices)
    calls = estimate_calls(inputs.positions, inputs.words_positions, inputs.clauses)
    tokens = Decimal(inputs.contract_tokens)
    task = Decimal(TASK_TOKENS_PER_CALL)
    output = Decimal(OUTPUT_TOKENS_PER_CALL)
    prices = inputs.prices
    low_per_call = (
        tokens * prices.cached_input_per_million
        + task * prices.input_per_million
        + output * prices.output_per_million
    )
    high_per_call = (tokens + task) * prices.input_per_million + output * prices.output_per_million
    low_usd = (Decimal(calls) * low_per_call / _TOKENS_PER_MILLION).quantize(
        _COST_QUANTUM, rounding=ROUND_HALF_UP
    )
    high_usd = (Decimal(calls) * high_per_call / _TOKENS_PER_MILLION).quantize(
        _COST_QUANTUM, rounding=ROUND_HALF_UP
    )
    return CostRange(calls=calls, low_usd=low_usd, high_usd=high_usd)
