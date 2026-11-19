"""The input size limits of Spec 9, and the word count they use."""

from typing import Final

MAX_FILE_BYTES: Final[int] = 20 * 1024 * 1024
# [Assumption] Spec 9: tuned in testing.

MAX_WORDS: Final[int] = 50_000
# [Assumption] Spec 9: tuned in testing.


def count_words(text: str) -> int:
    """Count the runs of characters between spaces and line breaks."""

    return len(text.split())
