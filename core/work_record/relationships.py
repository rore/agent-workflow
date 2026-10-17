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
    authority_match = re.match(r"^https://([^/?#]+)(?:[/?#]|$)", value, re.IGNORECASE)
    if not authority_match:
        return None
    authority = authority_match.group(1)
    if "@" in authority or "%" in authority:
        return None
    is_ipv6 = authority.startswith("[")
    if is_ipv6:
        closing = authority.find("]")
        if closing < 0:
            return None
        raw_host = authority[1:closing]
        try:
            from ipaddress import IPv6Address

            IPv6Address(raw_host)
        except ValueError:
            return None
    else:
        raw_host = authority.rsplit(":", 1)[0] if ":" in authority else authority
    try:
        parts = urlsplit(value)
        host = parts.hostname
        _ = parts.port
        ascii_host = host.encode("idna").decode("ascii") if host and not is_ipv6 else ""
    except ValueError:
        return None
    if parts.scheme.lower() != "https" or not host or parts.username is not None or parts.password is not None:
        return None
    if any(char.isspace() for char in parts.netloc):
        return None
    if not is_ipv6:
        labels = ascii_host.split(".")
        if labels[-1] == "":
            labels.pop()
        if not labels or any(not re.fullmatch(r"[A-Za-z0-9_-]+", label) for label in labels):
            return None
        if re.fullmatch(r"(?:[0-9]+|0[xX][0-9A-Fa-f]*)", labels[-1]):
            octets = raw_host.split(".")
            if len(octets) != 4 or any(
                not re.fullmatch(r"(?:0|[1-9][0-9]*)", octet) or int(octet) > 255
                for octet in octets
            ):
                return None
    return parts


def _source_url_status(value: str) -> str | None:
    """Validate the literal source-navigation authority without IDNA repair."""
    if _control(value) or _has_surrogate(value) or any(char.isspace() for char in value) or "\\" in value:
        return None
    match = re.match(r"^https://([^/?#]+)(?:[/?#]|$)", value, re.IGNORECASE)
    if not match:
        return None
    authority = match.group(1)
    if "@" in authority or "%" in authority:
        return None
    if authority.startswith("["):
        closing = authority.find("]")
        if closing < 0 or authority[closing + 1:] not in ("",) and not re.fullmatch(r":[0-9]+", authority[closing + 1:], re.ASCII):
            return None
        if authority[closing + 1:].startswith(":"):
            port = authority[closing + 2:].lstrip("0") or "0"
            if len(port) > 5 or (len(port) == 5 and port > "65535"):
                return None
        try:
            from ipaddress import IPv6Address

            IPv6Address(authority[1:closing])
        except ValueError:
            return None
        return "supported"

    if authority.count(":") > 1:
        return None
    host, separator, port = authority.partition(":")
    if separator:
        if not re.fullmatch(r"[0-9]+", port, re.ASCII):
            return None
        port = port.lstrip("0") or "0"
        if len(port) > 5 or (len(port) == 5 and port > "65535"):
            return None
    if not host:
        return None
    final_dot = host.endswith(".")
    host_without_dot = host[:-1] if final_dot else host
    labels = host_without_dot.split(".")
    if not host_without_dot or any(not label for label in labels):
        return None
    if any(ord(char) > 127 for char in host):
        if len(host_without_dot) > 253 or any(len(label) > 63 for label in labels):
            return None
        if any(not re.fullmatch(r"(?:[A-Za-z0-9_-]|[^\x00-\x7f])+", label) for label in labels):
            return None
        if re.fullmatch(r"(?:[0-9]+|0[xX][0-9A-Fa-f]*)", labels[-1], re.ASCII):
            return None
        return "unsupported"
    if len(host_without_dot) > 253 or any(len(label) > 63 for label in labels):
        return None
    if any(not re.fullmatch(r"[A-Za-z0-9_-]+", label, re.ASCII) for label in labels):
        return None
    if re.fullmatch(r"(?:[0-9]+|0[xX][0-9A-Fa-f]*)", labels[-1], re.ASCII):
        if final_dot or len(labels) != 4 or any(
            not re.fullmatch(r"(?:0|[1-9][0-9]*)", octet, re.ASCII) or int(octet) > 255
            for octet in labels
        ):
            return None
    return "supported"


def _strip_surrounding_hints(raw: str) -> str:
    raw = raw.strip(" \t\r\n")
    while raw.startswith("<!--"):
        end = raw.find("-->", 4)
        if end < 0:
            break
        raw = raw[end + 3:].strip(" \t\r\n")
    while raw.endswith("-->"):
        start = raw.rfind("<!--", 0, len(raw) - 3)
        if start < 0:
            break
        raw = raw[:start].strip(" \t\r\n")
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
    unsupported_source_url = False
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
                if not isinstance(url, str):
                    return {"status": "invalid", "reason": "invalid_relationships"}
                url_status = _source_url_status(url)
                if url_status is None:
                    return {"status": "invalid", "reason": "invalid_relationships"}
                unsupported_source_url |= url_status == "unsupported"

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
            re.IGNORECASE | re.ASCII,
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
    if unsupported_source_url:
        return {"status": "unsupported", "reason": "unsupported_source_url"}
    return {"status": "declared", "relationships": value}


def _has_surrogate(value: str) -> bool:
    return any(0xD800 <= ord(char) <= 0xDFFF for char in value)
