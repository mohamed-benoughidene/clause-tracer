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
CAP: Final[str] = r"(?:[A-Z][a-z'’-]+|UK|USA|UAE)"
STREET_PLAIN: Final[str] = r"(?:Street|St|Road|Rd|Avenue|Ave|Lane|Terrace|Gardens|Boulevard)"
STREET_AMBIG: Final[str] = r"(?:Way|Place|Court|Row|Hill|Close|Drive|Square)"
LEAD_WORD: Final[str] = r"(?:Rue|Avenue|Boulevard|Via|Calle|Strasse|Chemin|Allée)"
POST: Final[str] = r"(?:[A-Z]{1,2}\d[A-Z\d]?[ ]?\d[A-Z]{2}|\d{4,6})"
PART: Final[str] = rf",{H}*{CAP}(?:{H}+{CAP}){{0,2}}(?:{H}+{POST})?"
ADDRESS: Final[str] = (
    rf"\b\d+[A-Za-z]?{H}+(?:{CAP}{H}+){{0,3}}{STREET_PLAIN}\b(?:{PART}){{0,3}}"
    rf"|\b\d+[A-Za-z]?{H}+(?:{CAP}{H}+){{1,3}}{STREET_AMBIG}\b(?:{PART}){{0,3}}"
    rf"|\b\d+[A-Za-z]?{H}+{LEAD_WORD}{H}+{CAP}(?:{H}+{CAP}){{0,3}}(?:{PART}){{0,3}}"
)
ADDRESS_RE: Final[re.Pattern[str]] = re.compile(ADDRESS)
UK_POSTCODE: Final[str] = (
    r"\b(?:GIR ?0AA|[A-PR-UWYZ](?:[0-9]{1,2}|[A-HK-Y][0-9]{1,2}"
    r"|[0-9][A-HJKPSTUW]|[A-HK-Y][0-9][ABEHMNPRV-Y])[ ]?[0-9][ABD-HJLNP-UW-Z]{2})\b"
)
UK_POSTCODE_RE: Final[re.Pattern[str]] = re.compile(UK_POSTCODE)
US_ZIP: Final[str] = (
    r"\b(?:A[LKZR]|C[AOT]|DE|FL|GA|HI|I[DLNA]|K[SY]|LA|M[EDAINSOT]|N[EVHJMYCD]"
    r"|O[HKR]|PA|RI|S[CD]|T[NX]|UT|V[AT]|W[AIVY])"
    r"[ ]\d{5}(?:-\d{4})?\b"
)
US_ZIP_RE: Final[re.Pattern[str]] = re.compile(US_ZIP)
CA_POSTCODE: Final[str] = r"\b[A-Z]\d[A-Z][ ]?\d[A-Z]\d\b"
CA_POSTCODE_RE: Final[re.Pattern[str]] = re.compile(CA_POSTCODE)
MONTHS: Final[str] = (
    r"(?:January|February|March|April|May|June"
    r"|July|August|September|October|November|December)"
)
START_TOKEN: Final[str] = (
    r"(?:Flat|Unit|Suite|Floor|Room|Building)[ ]+\w+|PO Box[ ]+\d+"
    rf"|\d+[A-Za-z]?(?:-\d+)?(?=[ ]+(?!{MONTHS}\b)[A-Z][a-z])"
)
START_TOKEN_RE: Final[re.Pattern[str]] = re.compile(START_TOKEN)
CUE: Final[str] = (
    r"(?i:registered office (?:is )?at|registered address (?:is )?at"
    r"|address is|located at|whose address is|whose address)[ \t]+"
)
CUE_RE: Final[re.Pattern[str]] = re.compile(CUE)
TAIL: Final[str] = (
    rf",?{H}*(?:United Kingdom|UK|England|Scotland|Wales|Northern Ireland"
    r"|USA|United States|Canada)\b"
)
TAIL_RE: Final[re.Pattern[str]] = re.compile(TAIL)
HARD_STOP: Final[str] = r"[;:()\[\]\"“”\n]|[.!?](?=\s+[A-Z0-9])"
HARD_STOP_RE: Final[re.Pattern[str]] = re.compile(HARD_STOP)
ABBREVIATION_END: Final[str] = r"\b(?:St|Rd|Ave|Dr|Ln|Ct|Sq|Mt)$"
ABBREVIATION_END_RE: Final[re.Pattern[str]] = re.compile(ABBREVIATION_END)
