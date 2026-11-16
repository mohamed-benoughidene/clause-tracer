"""A pure hash of the exact AI request (system design 7, D8).

The hash keys the cache, the resume and the replay fake. It is computed
from the accepted form of the request itself, never from a rendered
provider payload, so two calls that mean the same thing share a key.
"""

import base64
import dataclasses
import hashlib
import json
from collections.abc import Mapping
from datetime import datetime
from decimal import Decimal
from enum import Enum

from clause_tracer.core.ai import AiRequest


def to_plain(value: object) -> object:
    """Turn a request's parts into JSON-serialisable plain data.

    Checked in this order: None, bool, int and float stay as they are; an
    Enum member becomes its value; a str stays; a Decimal becomes its str;
    a datetime becomes its isoformat; bytes become base64 ascii; a tuple or
    list becomes a list of plain items; a Mapping becomes a dict of plain
    values (a non-str key raises TypeError); a dataclass instance becomes a
    dict with its __type__ and its fields. Anything else raises TypeError.
    """

    if value is None or isinstance(value, bool | int | float):
        return value
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, str):
        return value
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, bytes):
        return base64.b64encode(value).decode("ascii")
    if isinstance(value, tuple | list):
        return [to_plain(item) for item in value]
    if isinstance(value, Mapping):
        plain: dict[str, object] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise TypeError(f"cannot hash {type(key).__name__} mapping key")
            plain[key] = to_plain(item)
        return plain
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        fields: dict[str, object] = {"__type__": type(value).__qualname__}
        for field in dataclasses.fields(value):
            fields[field.name] = to_plain(getattr(value, field.name))
        return fields
    raise TypeError(f"cannot hash {type(value).__name__}")


def request_sha256(request: AiRequest) -> str:
    """Hash the exact request: sha256 of the plain form, serialised deterministically.

    The plain form is serialised with sort_keys=True, separators (",", ":"),
    ensure_ascii=False and allow_nan=False, encoded UTF-8.
    """

    payload = json.dumps(
        to_plain(request),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
