"""The regular expressions that the finders share (S4-M1-T6)."""

import re
from typing import Final

HONORIFIC_BEFORE: Final[str] = r"\b(?:Mr|Mrs|Ms|Miss|Mx|Dr)\.?[ \t]+$"
HONORIFIC_BEFORE_RE: Final[re.Pattern[str]] = re.compile(HONORIFIC_BEFORE)
CLAUSE_NUMBER: Final[str] = r"^[ \t]*(?:\(?[0-9A-Za-z]{1,3}[.)]|\d+(?:\.\d+)*\.?)[ \t]+$"
CLAUSE_NUMBER_RE: Final[re.Pattern[str]] = re.compile(CLAUSE_NUMBER)
SENTENCE_MARK: Final[str] = r"[.!?]"
SENTENCE_MARK_RE: Final[re.Pattern[str]] = re.compile(SENTENCE_MARK)
HEADING_WORD: Final[str] = r"[^\W\d_][\w'’-]*"
HEADING_WORD_RE: Final[re.Pattern[str]] = re.compile(HEADING_WORD)
