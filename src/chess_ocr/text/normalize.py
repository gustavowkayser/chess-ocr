"""Deterministic text normalization (docs/OUTPUT_FORMAT.md, "Text normalization").

Only rules that can be decided from the text alone live here. Layout rules
(reading order, de-hyphenation, dropping headers) belong to label extraction.
"""

from __future__ import annotations

import re
import unicodedata

from chess_ocr.text.figurines import CHESS_GLYPHS, FILLED_TO_OUTLINE

_FILLED_TABLE = str.maketrans(dict(FILLED_TO_OUTLINE))
_VARIATION_SELECTORS = re.compile(f"([{''.join(sorted(CHESS_GLYPHS))}])[\ufe0e\ufe0f]+")


def normalize(text: str) -> str:
    """Apply the spec's normalization rules, in order. Idempotent."""
    text = unicodedata.normalize("NFC", text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = text.translate(_FILLED_TABLE)
    text = _VARIATION_SELECTORS.sub(r"\1", text)

    lines: list[str] = []
    for line in text.split("\n"):
        line = line.rstrip()
        if line or (lines and lines[-1]):  # drop leading blanks, collapse runs
            lines.append(line)
    while lines and not lines[-1]:
        lines.pop()
    return "\n".join(lines) + "\n" if lines else ""
