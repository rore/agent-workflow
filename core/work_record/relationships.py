"""Strict validator for the optional Work Record Relationships field."""

from __future__ import annotations

import json
import math
import re
import unicodedata
from urllib.parse import urlsplit


def _object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate key")
        result[key] = value
    return result


def _control(value: str) -> bool:
    return any(unicodedata.category(char) == "Cc" for char in value)


def _url_parts(value: str):
    if _control(value) or _has_surrogate(value) or "\\" in value or " " in value:
        return None
    try:
        parts = urlsplit(value)
        host = parts.hostname
        _ = parts.port
    except ValueError:
        return None
    if parts.scheme.lower() != "https" or not host or parts.username is not None or parts.password is not None:
        return None
    if any(char.isspace() for char in parts.netloc):
        return None
    return parts


def _strip_surrounding_hints(raw: str) -> str:
    raw = raw.strip()
    while raw.startswith("<!--"):
        end = raw.find("-->", 4)
        if end < 0:
            break
        raw = raw[end + 3:].strip()
    while raw.endswith("-->"):
        start = raw.rfind("<!--", 0, len(raw) - 3)
        if start < 0:
            break
        raw = raw[:start].strip()
    return raw


def decode_relationships(raw: str | None) -> dict[str, object]:
    """Return ``status`` plus a validated v1 object or a stable failure reason."""
    if raw is None:
        return {"status": "legacy"}
    try:
        text = _strip_surrounding_hints(raw)
        if len(text.encode("utf-8", errors="strict")) > 65536:
            return {"status": "invalid", "reason": "relationships_too_large"}
        value = json.loads(
            text,
            object_pairs_hook=_object,
            parse_constant=lambda _: (_ for _ in ()).throw(ValueError("invalid constant")),
        )
    except (TypeError, ValueError, RecursionError, UnicodeError):
        return {"status": "invalid", "reason": "invalid_json"}

    if not isinstance(value, dict) or set(value) != {"schema_version", "sources", "pull_requests"}:
        return {"status": "invalid", "reason": "invalid_relationships"}
    version = value["schema_version"]
    if isinstance(version, bool) or not isinstance(version, (int, float)):
        return {"status": "invalid", "reason": "invalid_relationships"}
    if isinstance(version, float) and (not math.isfinite(version) or not version.is_integer()):
        return {"status": "invalid", "reason": "invalid_relationships"}
    if version > 1:
        return {"status": "unsupported", "reason": "unsupported_relationship_version"}
    if version != 1:
        return {"status": "invalid", "reason": "invalid_relationships"}

    sources = value["sources"]
    if sources is not None and not isinstance(sources, list):
        return {"status": "invalid", "reason": "invalid_relationships"}
    source_ids: set[tuple[str, str, str]] = set()
    if sources is not None:
        for source in sources:
            if not isinstance(source, dict) or set(source) - {"provider", "scope_ref", "local_ref", "url"} or not {"provider", "scope_ref", "local_ref"} <= set(source):
                return {"status": "invalid", "reason": "invalid_relationships"}
            identity = tuple(source[key] for key in ("provider", "scope_ref", "local_ref"))
            if any(
                not isinstance(item, str)
                or not item.strip()
                or _control(item)
                or _has_surrogate(item)
                for item in identity
            ):
                return {"status": "invalid", "reason": "invalid_relationships"}
            if identity in source_ids:
                return {"status": "invalid", "reason": "invalid_relationships"}
            source_ids.add(identity)
            if "url" in source:
                url = source["url"]
                if not isinstance(url, str) or _url_parts(url) is None or _has_surrogate(url):
                    return {"status": "invalid", "reason": "invalid_relationships"}

    pull_requests = value["pull_requests"]
    if not isinstance(pull_requests, list):
        return {"status": "invalid", "reason": "invalid_relationships"}
    pr_ids: set[tuple[str, str, str]] = set()
    unsupported_pr = False
    for url in pull_requests:
        if not isinstance(url, str):
            return {"status": "invalid", "reason": "invalid_relationships"}
        parts = _url_parts(url)
        if parts is None:
            return {"status": "invalid", "reason": "invalid_relationships"}
        match = re.fullmatch(
            r"https://github\.com/([A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?)/"
            r"([A-Za-z0-9_.-]+)/pull/([1-9][0-9]*)",
            url,
            re.IGNORECASE,
        )
        if not match:
            if re.match(r"https://[^/]+:[0-9]+(?:/|$)", url, re.IGNORECASE) or (
                parts.hostname.lower() == "github.com"
                and (parts.query or parts.fragment or "%" in parts.path)
            ):
                return {"status": "invalid", "reason": "invalid_relationships"}
            unsupported_pr = True
            continue
        owner, repository, number = match.groups()
        if repository in {".", ".."}:
            return {"status": "invalid", "reason": "invalid_relationships"}
        identity = (owner.lower(), repository.lower(), number)
        if identity in pr_ids:
            return {"status": "invalid", "reason": "invalid_relationships"}
        pr_ids.add(identity)
    if unsupported_pr:
        return {"status": "unsupported", "reason": "unsupported_pr_url"}
    return {"status": "declared", "relationships": value}


def _has_surrogate(value: str) -> bool:
    return any(0xD800 <= ord(char) <= 0xDFFF for char in value)
