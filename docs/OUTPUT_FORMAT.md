# Output Format Specification

This is the contract for what the OCR produces. Training labels, evaluation
metrics and post-processing all depend on it. Change it only through an issue,
and regenerate the labels when you do.

## Goals

- **Faithful to the page.** Reproduce what is printed, in reading order. Do not
  translate notation or "fix" the author.
- **Chess-aware.** Piece figurines and annotation symbols are real Unicode
  characters, never look-alike junk (`lt:J`, `E!:`, `��`, ...).
- **Deterministic.** Two annotators labelling the same page should produce the
  same text byte for byte. Every rule below exists to remove an ambiguity.

## Encoding

- UTF-8, `\n` line endings, NFC normalization.
- A single trailing newline at the end of the page.

## Piece figurines

Books print one figurine style for both colours, so we always use the **outline
("white") glyphs**:

| Piece  | Glyph | Code point |
|--------|-------|------------|
| King   | ♔     | U+2654     |
| Queen  | ♕     | U+2655     |
| Rook   | ♖     | U+2656     |
| Bishop | ♗     | U+2657     |
| Knight | ♘     | U+2658     |

- Pawns have no figurine in move text (`e4`, `exd5`).
- The filled glyphs U+265A–U+265F must never appear in output.
  Post-processing maps them to the outline glyphs.
- Do not add a space between the figurine and the square: `♘f3`, `♗xf7+`.
- If a figurine appears in prose ("the ♗ pair"), output the glyph exactly as
  printed.

## Move text

- Move numbers are written as printed: `23.♖e3`, `23 ♖e3`, `23...♕h5`,
  `23…♕h5`. Keep the book's punctuation style. Do not normalize between
  books.
- Ellipsis: if the page shows a typographic ellipsis, use `…` (U+2026). If it
  shows separated dots, use `...`.
- Check `+`, mate `#`, captures `x`, castling `0-0` / `O-O` exactly as printed.
- Move-annotation glyphs are kept as ASCII: `!`, `?`, `!!`, `??`, `!?`, `?!`.

### Move tables (column layout)

Some books, such as *My 60 Memorable Games*, set the main line in columns
(move number, White, Black). Each row becomes **one line**, with the cells
separated by a single space:

```
6 d4 …
7 ♘d3 ♘xe4
9 … ♘xc3
```

## Evaluation symbols

| Meaning                   | Output |
|---------------------------|--------|
| White slightly better     | `⩲` (U+2A72) |
| Black slightly better     | `⩱` (U+2A71) |
| White clearly better      | `±` (U+00B1) |
| Black clearly better      | `∓` (U+2213) |
| White winning             | `+−` (plus, U+2212) |
| Black winning             | `−+` (U+2212, plus) |
| Equal                     | `=` |
| Unclear                   | `∞` (U+221E) |
| With compensation         | `=∞` or as printed |

Any other Informator symbol is kept as its closest Unicode character. It should
also be added to this table in the same PR.

## Layout and reading order

- **Reading order:** top to bottom. On multi-column pages, read the whole
  left column first, then the right column.
- **Paragraphs** are separated by exactly one blank line. Line breaks inside a
  paragraph are joined with a single space, and words hyphenated at the end of
  a line are rejoined.
- **Running headers, running footers and page numbers are dropped.**
- **Emphasis** (bold or italic) is not encoded. Output plain text only.

## Diagrams

- Each board diagram is replaced by the token `[DIAGRAM]` on its own line,
  with a blank line before and after it.
- Caption text printed next to or under the diagram (player names,
  "Position after 8…♗g7", side-to-move markers) is kept as normal lines
  right after the `[DIAGRAM]` line, in reading order.
- Converting diagrams to FEN is post-v1 work (see the backlog milestone). When
  that happens, the token will become `[DIAGRAM fen="..."]`.

## Example

Source: *My 60 Memorable Games*, page 150 (top):

```
On 5…h5 6 ♗c4 ♖h7 7 d4 d6 8 ♘d3 f3 9 gxf3 ♗e7 10 ♗e3 ♗xh4+ 11 ♔d2 ♗g5 12 f4 ♗h6 13 ♘c3 White has more than enough compensation for the Pawn. This is vintage analysis.

6 d4 …
```
