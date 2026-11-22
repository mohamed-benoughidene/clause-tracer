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

EMAIL: Final[str] = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+"
EMAIL_RE: Final[re.Pattern[str]] = re.compile(EMAIL)
PHONE: Final[str] = (
    r"(?<![\w+])(?:\+\d{1,3}[ -]?(?:\(0\))?\d[\d -]{6,14}\d"
    r"|0\d{2,4}[ -]\d{3,4}[ -]?\d{3,4}"
    r"|\(0\d{2,4}\)[ -]?\d{3,4}[ -]?\d{3,4}"
    r"|0\d{10})(?!\w)"
)
PHONE_RE: Final[re.Pattern[str]] = re.compile(PHONE)
ID_KEYWORD: Final[str] = (
    r"(?i:company (?:registration )?(?:number|no\.?)|registered (?:number|no\.?)"
    r"|registration (?:number|no\.?)"
    r"|vat (?:registration )?(?:number|no\.?)|tax id)[ \t]*(?:is|:|of)?[ \t]*"
    r"(?P<v>(?:GB[ ]?)?[A-Z]{0,2}\d[\d ]{3,12}\d)"
)
ID_KEYWORD_RE: Final[re.Pattern[str]] = re.compile(ID_KEYWORD)
SORT_CODE: Final[str] = r"(?i:sort[ ]code)[ \t]*:?[ \t]*(?P<v>\d{2}-?\d{2}-?\d{2})(?!\d)"
SORT_CODE_RE: Final[re.Pattern[str]] = re.compile(SORT_CODE)
ACCOUNT_NUMBER: Final[str] = r"(?i:account[ ](?:number|no\.?))[ \t]*:?[ \t]*(?P<v>\d{8})(?!\d)"
ACCOUNT_NUMBER_RE: Final[re.Pattern[str]] = re.compile(ACCOUNT_NUMBER)
IBAN: Final[str] = (
    r"(?<![A-Za-z0-9])[A-Z]{2}\d{2}(?:[ ]?[A-Z0-9]{4}){2,7}(?:[ ]?[A-Z0-9]{1,3})?(?![A-Za-z0-9])"
)
IBAN_RE: Final[re.Pattern[str]] = re.compile(IBAN)
H: Final[str] = r"[ \t]"
WORD: Final[str] = r"[A-Z][A-Za-z0-9'’&-]*"
SUFFIX_WORDS: Final[str] = (
    r"(?:Ltd|Plc|PLC|LLC|LLP|LP|Inc|Corp|Corporation|Incorporated|GmbH|AG|SARL|SAS|BV|NV"
    r"|Pty|SRL|SpA|Oy|KG|UG|Pte|Co)"
)
SUFFIX: Final[str] = (
    r"(?:S\.A\.R\.L\.|L\.L\.C\.|L\.L\.P\.|P\.L\.C\.|S\.A\.|N\.V\.|B\.V\."
    rf"|Co\.?{H}+KG(?![-\w])|Pte{H}+Ltd(?![-\w])"
    rf"|Limited(?![-\w])(?!{H}+(?:Liability|Warranty|Partnership|Licen[cs]e))"
    rf"|{SUFFIX_WORDS}(?![-\w]))"
)
CONNECTOR: Final[str] = (
    rf"(?:GmbH(?={H}+&{H}+Co\b)|(?!(?:{SUFFIX_WORDS}|Limited)(?![-\w])){WORD}|&|of|and)"
)
COMPANY: Final[str] = rf"(?<![\w]){WORD}(?:{H}+{CONNECTOR}){{0,5}}{H}+{SUFFIX}"
COMPANY_RE: Final[re.Pattern[str]] = re.compile(COMPANY)
