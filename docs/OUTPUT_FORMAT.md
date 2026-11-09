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
- No blank lines at the start of the page. A page with no text is the empty
  string (no newline).
- No variation selectors (U+FE0E, U+FE0F) after a chess glyph: `♔`, never
  `♔` + U+FE0F (the emoji form).

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
| Pawn   | ♙     | U+2659 (prose only) |

- Pawns have no figurine in move text (`e4`, `exd5`). The pawn glyph ♙ is
  used only where the page prints a pawn figurine in prose.
- The filled glyphs U+265A–U+265F (♚♛♜♝♞♟) must never appear in output.
  Post-processing maps each one to its outline glyph (♚→♔, …, ♟→♙).
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

## Text normalization

Post-processing (`chess_ocr.text.normalize`) applies exactly these rules, in
this order. They depend on the text alone and never change chess content.
Layout rules (reading order, de-hyphenation, dropping headers) are not part of
it; they belong to label extraction.

1. NFC normalization (not NFKC, which would turn `…` into `...`).
2. `\r\n` and `\r` become `\n`.
3. Filled figurines U+265A–U+265F become outline figurines U+2654–U+2659.
4. Variation selectors U+FE0E / U+FE0F directly after a figurine are removed.
5. Trailing whitespace is removed from every line.
6. Blank lines at the start and end of the page are removed, and runs of blank
   lines become exactly one blank line.
7. A non-empty page ends with exactly one `\n`. An empty page is `""`.

Everything else is left as is. For example, `+-` is not turned into `+−`,
`...` is not turned into `…`, and `0-0` is not turned into `O-O`.

## Example

Synthetic (invented for this spec, not taken from a book):

```
Instead 11…♘d7 12 ♕d2 ♘f8 13 ♖ad1 leaves the knight badly placed ⩲. The ♗ pair will tell in the long run.

11 … ♗d7
12 ♗e3 ♖e8
```
