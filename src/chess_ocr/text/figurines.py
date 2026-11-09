"""Chess glyph constants from docs/OUTPUT_FORMAT.md. That document is the source of truth."""

from __future__ import annotations

from types import MappingProxyType

KING = "♔"  # U+2654
QUEEN = "♕"  # U+2655
ROOK = "♖"  # U+2656
BISHOP = "♗"  # U+2657
KNIGHT = "♘"  # U+2658
PAWN = "♙"  # U+2659, prose only; move text has no pawn figurine

# SAN piece letter -> outline figurine (pawns have no SAN letter).
SAN_TO_FIGURINE = MappingProxyType({"K": KING, "Q": QUEEN, "R": ROOK, "B": BISHOP, "N": KNIGHT})
FIGURINE_TO_SAN = MappingProxyType({glyph: san for san, glyph in SAN_TO_FIGURINE.items()})

# Every glyph allowed in output: the five piece figurines plus the prose-only pawn.
OUTLINE_FIGURINES = frozenset((*SAN_TO_FIGURINE.values(), PAWN))

# Filled ("black") glyphs U+265A..U+265F -> outline glyphs U+2654..U+2659.
FILLED_TO_OUTLINE = MappingProxyType({chr(0x265A + i): chr(0x2654 + i) for i in range(6)})

# All twelve chess glyphs, outline and filled.
CHESS_GLYPHS = OUTLINE_FIGURINES | frozenset(FILLED_TO_OUTLINE)

# Evaluation symbols (the spec's "Evaluation symbols" table).
EVAL_SYMBOLS = MappingProxyType(
    {
        "white_slightly_better": "⩲",  # U+2A72
        "black_slightly_better": "⩱",  # U+2A71
        "white_clearly_better": "±",  # U+00B1
        "black_clearly_better": "∓",  # U+2213
        "white_winning": "+\u2212",  # plus, MINUS SIGN (not hyphen)
        "black_winning": "\u2212+",  # MINUS SIGN, plus
        "equal": "=",
        "unclear": "∞",  # U+221E
        "compensation": "=∞",  # equals, U+221E
    }
)

# Move-annotation glyphs, always ASCII.
MOVE_ANNOTATIONS = ("!", "?", "!!", "??", "!?", "?!")

DIAGRAM_TOKEN = "[DIAGRAM]"
