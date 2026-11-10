"""Report display helpers: emoji stripping and compact-fund rendering."""
from __future__ import annotations

import re
from typing import Any

# Emoji / pictograph ranges. Kept explicit so plain arrows, punctuation and
# CJK text are never touched.
_EMOJI_PATTERN = re.compile(
    "["
    "\U0001F000-\U0001FAFF"  # emoji, symbols & pictographs
    "\U00002600-\U000027BF"  # misc symbols / dingbats
    "\U00002B00-\U00002BFF"  # arrows & misc symbols
    "\U0001F1E6-\U0001F1FF"  # regional indicators
    "\U0000FE0F"             # variation selector-16
    "\U0000200D"             # zero width joiner
    "\U000020E3"             # combining enclosing keycap
    "\U000E0020-\U000E007F"  # tag characters
    "]+"
)


def strip_emoji(text: str) -> str:
    """Remove emoji/pictographs from rendered report text."""
    if not text:
        return text or ""
    cleaned = _EMOJI_PATTERN.sub("", text)
    # Collapse whitespace left behind by removed emoji between tokens.
    cleaned = re.sub(r"[ \t]+\n", "\n", cleaned)
    cleaned = re.sub(r"(?<=\S) {2,}(?=\S)", " ", cleaned)
    # Emoji often sat inside bold markers or at line start; normalize those gaps
    # so "** 持有**" still renders as bold on mobile clients.
    cleaned = re.sub(r"\*\*[ \t]+", "**", cleaned)
    cleaned = re.sub(r"(?m)^[ \t]+(?=\*\*)", "", cleaned)
    return cleaned


_A_ETF_PREFIXES = ("51", "52", "56", "58", "15", "16", "18")
_ETF_NAME_HINTS = ("ETF", "FUND", "TRUST", "INDEX", "TRACKER", "UNIT", "指数")


def _is_etf_like(code: str, name: str) -> bool:
    raw_code = (code or "").strip().split(".")[0]
    upper_name = (name or "").upper()
    if raw_code.isdigit() and len(raw_code) == 6 and raw_code.startswith(_A_ETF_PREFIXES):
        return True
    return any(hint in upper_name for hint in _ETF_NAME_HINTS)


def is_etf_result(result: Any) -> bool:
    """Whether an analysis result targets an ETF or a market index.

    Prefer the canonical SearchService classifier; fall back to a local
    heuristic so report rendering never fails when optional search deps are
    missing (e.g. minimal test environments).
    """
    code = getattr(result, "code", "") or ""
    name = getattr(result, "name", "") or ""
    try:
        from src.search_service import SearchService

        return bool(SearchService.is_index_or_etf(code, name))
    except Exception:  # noqa: BLE001 - display helper must stay fail-open
        return _is_etf_like(code, name)


_ETF_SUFFIX_RE = re.compile(r"\s*ETF.*$", re.IGNORECASE)
_ETF_ACTION_PATTERNS = (
    ("加仓", ("加仓", "买入", "买进", "增持", "buy", "add")),
    ("减仓", ("减仓", "卖出", "清仓", "减持", "sell", "reduce", "avoid", "alert")),
    ("继续持有", ("持有", "继续持有", "观望", "watch", "hold", "wait")),
)


def etf_sector_label(name: str) -> str:
    """Derive the tracked sector/theme from an ETF display name."""
    raw = (name or "").strip()
    if not raw:
        return "N/A"
    base = _ETF_SUFFIX_RE.sub("", raw).strip()
    return base or raw


def etf_action_label(advice: str) -> str:
    """Map localized operation advice to fund action: 加仓/减仓/继续持有."""
    text = (advice or "").strip().lower()
    for label, patterns in _ETF_ACTION_PATTERNS:
        if any(p.lower() in text for p in patterns):
            return label
    return "继续持有"
