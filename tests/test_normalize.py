from __future__ import annotations

import random
import re
import unicodedata
from pathlib import Path

import pytest

from chess_ocr.text.figurines import FILLED_TO_OUTLINE
from chess_ocr.text.normalize import normalize

SPEC = (Path(__file__).resolve().parents[1] / "docs" / "OUTPUT_FORMAT.md").read_text(
    encoding="utf-8"
)


def spec_example() -> str:
    match = re.search(r"## Example\n.*?```\n(.*?)```", SPEC, re.DOTALL)
    assert match, "Example block not found in OUTPUT_FORMAT.md"
    return match.group(1)


# --- one test per rule -------------------------------------------------------


def test_nfc() -> None:
    assert normalize("caf" + "e\u0301" + "\n") == "caf\u00e9\n"


def test_nfc_not_nfkc() -> None:
    assert normalize("23…♕h5 \ufb01le\n") == "23…♕h5 \ufb01le\n"  # ellipsis and ligature kept


@pytest.mark.parametrize("text", ["a\r\nb\r\n", "a\rb\r", "a\r\nb\rc\n"])
def test_line_endings(text: str) -> None:
    out = normalize(text)
    assert "\r" not in out
    assert out == text.replace("\r\n", "\n").replace("\r", "\n")


@pytest.mark.parametrize(("filled", "outline"), sorted(FILLED_TO_OUTLINE.items()))
def test_filled_to_outline(filled: str, outline: str) -> None:
    assert normalize(f"12 {filled}f3\n") == f"12 {outline}f3\n"


@pytest.mark.parametrize("selector", ["\ufe0e", "\ufe0f", "\ufe0f\ufe0e"])
def test_variation_selectors_after_glyph(selector: str) -> None:
    assert normalize(f"♔{selector}e2 ♟{selector}\n") == "♔e2 ♙\n"


def test_variation_selector_elsewhere_kept() -> None:
    assert normalize("a\ufe0f ♔ \ufe0f\n") == "a\ufe0f ♔ \ufe0f\n"


def test_trailing_whitespace() -> None:
    assert normalize("12 ♘f3  \t\n13 ♗c4\u00a0\n") == "12 ♘f3\n13 ♗c4\n"


def test_leading_whitespace_kept() -> None:
    assert normalize("  indented\n") == "  indented\n"


def test_leading_blank_lines_removed() -> None:
    assert normalize("\n \n\t\nfirst\n") == "first\n"


def test_blank_line_runs_collapsed() -> None:
    assert normalize("a\n\n\n \n\nb\n") == "a\n\nb\n"


@pytest.mark.parametrize("text", ["a", "a\n", "a\n\n\n", "a  \n \n"])
def test_single_trailing_newline(text: str) -> None:
    assert normalize(text) == "a\n"


@pytest.mark.parametrize("text", ["", "\n", " \n\t\r\n"])
def test_empty_page(text: str) -> None:
    assert normalize(text) == ""


# --- chess content is never changed -----------------------------------------


@pytest.mark.parametrize(
    "text",
    [
        "+-", "-+", "+\u2212", "\u2212+", "±", "∓", "⩲", "⩱", "=", "∞", "=∞",
        "...", "…", "0-0", "O-O", "0-0-0", "O-O-O",
        "!", "?", "!!", "??", "!?", "?!", "#", "+", "x",
        "23.♖e3", "23 ♖e3", "23...♕h5", "23…♕h5", "♗xf7+", "exd5", "e8=♕#",
        "[DIAGRAM]", '[DIAGRAM fen="8/8/8/8/8/8/8/8 w - - 0 1"]',
    ],
)  # fmt: skip
def test_chess_content_unchanged(text: str) -> None:
    assert normalize(text + "\n") == text + "\n"


def test_spec_example_is_normalized() -> None:
    example = spec_example()
    assert normalize(example) == example


def test_spec_example_idempotent() -> None:
    once = normalize(spec_example())
    assert normalize(once) == once


# --- property-style checks on generated inputs -------------------------------

ALPHABET = [
    "a", "Z", "1", " ", "\t", "\u00a0", "\n", "\r", "\r\n", ".", "…", "+", "\u2212", "-",
    "e\u0301", "\u00e9", "\ufb01", "\ufe0e", "\ufe0f", "\ufeff", "\u2028",
    *[chr(c) for c in range(0x2654, 0x2660)],
    "[DIAGRAM]", "♘f3", "±",
]  # fmt: skip


def random_texts(n: int = 2000, seed: int = 1234) -> list[str]:
    rng = random.Random(seed)
    return ["".join(rng.choices(ALPHABET, k=rng.randint(0, 40))) for _ in range(n)]


def _content(text: str) -> str:
    """What normalization must preserve: non-whitespace content after the
    character-level rules (NFC, filled->outline, selector removal)."""
    text = unicodedata.normalize("NFC", text).translate(str.maketrans(dict(FILLED_TO_OUTLINE)))
    text = re.sub("([♔-♟])[\ufe0e\ufe0f]+", r"\1", text)
    return "".join(text.split())


def test_idempotent_on_generated_inputs() -> None:
    for text in random_texts():
        once = normalize(text)
        assert normalize(once) == once, repr(text)


def test_output_invariants_on_generated_inputs() -> None:
    for text in random_texts():
        out = normalize(text)
        assert "\r" not in out, repr(text)
        assert not set(out) & set(FILLED_TO_OUTLINE), repr(text)
        assert "\n\n\n" not in out, repr(text)
        assert out == "" or (out.endswith("\n") and not out.endswith("\n\n")), repr(text)
        assert not out.startswith("\n"), repr(text)
        assert _content(out) == _content(text), repr(text)
