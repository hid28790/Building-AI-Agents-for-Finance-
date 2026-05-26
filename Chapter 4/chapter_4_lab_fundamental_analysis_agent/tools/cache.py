"""
cache.py
--------
Simple in-memory cache for tool results within a single pipeline run.

Each entry is keyed by a tuple (tool_name, *args) and stores the JSON
string that the tool would otherwise return from yfinance. The cache is
populated on the first call and reused on all subsequent calls within the
same run, eliminating redundant API requests when multiple agents call the
same tool with the same inputs.

Call clear() at the start of each analyze_ticker() call to ensure a fresh
fetch for every new ticker analysis.
"""

_cache: dict[tuple, str] = {}


def get(key: tuple) -> str | None:
    return _cache.get(key)


def store(key: tuple, value: str) -> None:
    _cache[key] = value


def clear() -> None:
    _cache.clear()
