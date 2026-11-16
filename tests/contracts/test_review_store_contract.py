"""The ReviewStore behaviour suite (S1-M4-T7, T3, ADR 0006).

Run against the in-memory fake now, and against the real encrypted
adapter from stage 6 (ADR 0005, 14 Nov amendment).
"""

from datetime import UTC, datetime, timedelta

import pytest

from clause_tracer.core import DuplicateRecordError, InMemoryReviewStore, ReviewStore
from clause_tracer.core.ids import ReviewId
from clause_tracer.core.tests.shapes_for_tests import make_record

NOW = datetime(2026, 11, 16, 9, 0, 0, tzinfo=UTC)


@pytest.fixture(params=["in_memory"])
def review_store(request: pytest.FixtureRequest) -> ReviewStore:
    if request.param == "in_memory":
        return InMemoryReviewStore()
    raise AssertionError(f"unknown review store param {request.param}")


def test_saved_record_loads_back_equal(review_store: ReviewStore) -> None:
    record = make_record("rec-1", "review-1", NOW)
    review_store.save_record(record)
    assert review_store.load_records(ReviewId("review-1")) == (record,)


def test_records_load_in_save_order(review_store: ReviewStore) -> None:
    first = make_record("rec-1", "review-1", NOW)
    second = make_record("rec-2", "review-1", NOW + timedelta(minutes=1))
    review_store.save_record(second)
    review_store.save_record(first)
    assert review_store.load_records(ReviewId("review-1")) == (second, first)


def test_duplicate_record_id_raises(review_store: ReviewStore) -> None:
    # Append-only (D1): the id is taken across every review.
    review_store.save_record(make_record("rec-1", "review-1", NOW))
    with pytest.raises(DuplicateRecordError) as raised:
        review_store.save_record(make_record("rec-1", "review-2", NOW))
    assert raised.value.context["record_id"] == "rec-1"


def test_unknown_review_has_no_records(review_store: ReviewStore) -> None:
    assert review_store.load_records(ReviewId("no-such-review")) == ()


def test_list_reviews_is_sorted(review_store: ReviewStore) -> None:
    review_store.save_record(make_record("rec-1", "review-2", NOW))
    review_store.save_record(make_record("rec-2", "review-10", NOW))
    review_store.save_record(make_record("rec-3", "review-1", NOW))
    expected = (ReviewId("review-1"), ReviewId("review-10"), ReviewId("review-2"))
    assert review_store.list_reviews() == expected


def test_delete_review_twice_succeeds(review_store: ReviewStore) -> None:
    review_store.save_record(make_record("rec-1", "review-1", NOW))
    review_store.delete_review(ReviewId("review-1"))
    review_store.delete_review(ReviewId("review-1"))
    assert review_store.list_reviews() == ()


def test_delete_removes_the_records(review_store: ReviewStore) -> None:
    review_store.save_record(make_record("rec-1", "review-1", NOW))
    review_store.delete_review(ReviewId("review-1"))
    assert review_store.load_records(ReviewId("review-1")) == ()


def test_purge_removes_only_due_reviews(review_store: ReviewStore) -> None:
    # A review's last change is the latest finished_at of its records
    # (the stage 1 stand-in, system design 3.4).
    late = make_record("rec-1", "review-late", NOW - timedelta(days=31))
    early = make_record("rec-2", "review-early", NOW - timedelta(days=29))
    review_store.save_record(late)
    review_store.save_record(early)
    assert review_store.purge_expired(NOW, 30) == (ReviewId("review-late"),)
    assert review_store.list_reviews() == (ReviewId("review-early"),)


def test_purge_with_nothing_due_returns_empty(review_store: ReviewStore) -> None:
    review_store.save_record(make_record("rec-1", "review-1", NOW - timedelta(days=29)))
    assert review_store.purge_expired(NOW, 30) == ()
    assert review_store.list_reviews() == (ReviewId("review-1"),)


def test_purge_with_clock_behind_removes_nothing(review_store: ReviewStore) -> None:
    # Spec 9: a clock behind the last change deletes nothing.
    review_store.save_record(make_record("rec-1", "review-1", NOW))
    before = NOW - timedelta(days=365)
    assert review_store.purge_expired(before, 7) == ()
    assert review_store.list_reviews() == (ReviewId("review-1"),)
