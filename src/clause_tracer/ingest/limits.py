"""The input size limits of Spec 9, and the word count they use."""

from typing import Final

MAX_FILE_BYTES: Final[int] = 20 * 1024 * 1024
# [Assumption] Spec 9: tuned in testing.

MAX_WORDS: Final[int] = 50_000
# [Assumption] Spec 9: tuned in testing.


def count_words(text: str) -> int:
    """Count the runs of characters between spaces and line breaks."""

    return len(text.split())


MAX_ZIP_MEMBERS: Final[int] = 2_000
# [Assumption] ADR 0007 action item 3: tuned in testing.

MAX_XML_PART_BYTES: Final[int] = 32 * 1024 * 1024
# [Assumption] system design 8.4: tuned in testing.

MAX_PARSED_TOTAL_BYTES: Final[int] = 48 * 1024 * 1024
# [Assumption] system design 8.4: tuned in testing.

MAX_XML_DEPTH: Final[int] = 256
# The fixed depth of lxml without huge_tree (measured: 256 parses, 257 fails).

MAX_PDF_PAGES: Final[int] = 1_000
# [Assumption] ADR 0007 action item 3: tuned in testing.
