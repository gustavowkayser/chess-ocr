from __future__ import annotations

import re
from pathlib import Path

import pytest

from chess_ocr.text import figurines as f

SPEC = (Path(__file__).resolve().parents[1] / "docs" / "OUTPUT_FORMAT.md").read_text(
    encoding="utf-8"
)


@pytest.mark.parametrize(
    ("san", "glyph", "codepoint"),
    [("K", f.KING, 0x2654), ("Q", f.QUEEN, 0x2655), ("R", f.ROOK, 0x2656),
     ("B", f.BISHOP, 0x2657), ("N", f.KNIGHT, 0x2658)],
)  # fmt: skip
def test_piece_figurines(san: str, glyph: str, codepoint: int) -> None:
    assert ord(glyph) == codepoint
    assert f.SAN_TO_FIGURINE[san] == glyph
    assert f.FIGURINE_TO_SAN[glyph] == san


def test_pawn_is_prose_only() -> None:
    assert ord(f.PAWN) == 0x2659
    assert f.PAWN in f.OUTLINE_FIGURINES
    assert f.PAWN not in f.FIGURINE_TO_SAN


def test_outline_set() -> None:
    assert {ord(g) for g in f.OUTLINE_FIGURINES} == set(range(0x2654, 0x265A))


def test_filled_to_outline() -> None:
    assert {ord(k): ord(v) for k, v in f.FILLED_TO_OUTLINE.items()} == {
        0x265A: 0x2654, 0x265B: 0x2655, 0x265C: 0x2656,
        0x265D: 0x2657, 0x265E: 0x2658, 0x265F: 0x2659,
    }  # fmt: skip
    assert {chr(c) for c in range(0x2654, 0x2660)} == f.CHESS_GLYPHS


@pytest.mark.parametrize(
    ("key", "codepoints"),
    [
        ("white_slightly_better", [0x2A72]),
        ("black_slightly_better", [0x2A71]),
        ("white_clearly_better", [0x00B1]),
        ("black_clearly_better", [0x2213]),
        ("white_winning", [0x2B, 0x2212]),
        ("black_winning", [0x2212, 0x2B]),
        ("equal", [0x3D]),
        ("unclear", [0x221E]),
        ("compensation", [0x3D, 0x221E]),
    ],
)
def test_eval_symbols(key: str, codepoints: list[int]) -> None:
    assert [ord(c) for c in f.EVAL_SYMBOLS[key]] == codepoints


# --- the constants must match docs/OUTPUT_FORMAT.md -------------------------


def test_figurine_table_matches_spec() -> None:
    rows = re.findall(r"^\| (\w+)\s+\| (\S)\s+\| U\+([0-9A-F]{4})", SPEC, re.MULTILINE)
    table = {glyph: int(cp, 16) for _, glyph, cp in rows}
    assert table == {g: ord(g) for g in f.OUTLINE_FIGURINES}


def test_filled_range_in_spec() -> None:
    assert "U+265A\u2013U+265F" in SPEC
    for filled in f.FILLED_TO_OUTLINE:
        assert filled in SPEC


@pytest.mark.parametrize("symbol", sorted(f.EVAL_SYMBOLS.values()))
def test_eval_symbol_in_spec(symbol: str) -> None:
    assert f"`{symbol}`" in SPEC


@pytest.mark.parametrize("glyph", f.MOVE_ANNOTATIONS)
def test_move_annotation_in_spec(glyph: str) -> None:
    assert f"`{glyph}`" in SPEC


def test_diagram_token_in_spec() -> None:
    assert f"`{f.DIAGRAM_TOKEN}`" in SPEC
