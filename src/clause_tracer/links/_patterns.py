"""The patterns that `links` reads (stage 3).

Every pattern that a task gives as a string constant lives here. It is
compiled once, next to the constant. Offsets are half-open and point into
the canonical text.
"""

import re
from typing import Final

ITEM_NUMBER: Final[str] = r"[0-9]{1,3}(?:\.[0-9]{1,3}){0,4}(?:\([0-9A-Za-z]{1,4}\)){0,3}"
WRITTEN_NUMBER_RE: Final[re.Pattern[str]] = re.compile(ITEM_NUMBER)
ROMAN_RE: Final[re.Pattern[str]] = re.compile(
    r"M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})"
)
