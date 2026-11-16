"""The opaque ids of the app. Ids are strings made at the edge (system design 3.4)."""

from typing import NewType

ReviewId = NewType("ReviewId", str)
PlaybookId = NewType("PlaybookId", str)
CustomerId = NewType("CustomerId", str)
PositionId = NewType("PositionId", str)
ClauseId = NewType("ClauseId", str)
SentenceId = NewType("SentenceId", str)
RecordId = NewType("RecordId", str)
