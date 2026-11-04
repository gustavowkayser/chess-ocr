# Dataset

> **Copyright.** The source books are copyrighted. The PDFs in `assets/`, and
> everything derived from them (page images, labels, manifests), stay on the
> local machine. They are never committed, uploaded, attached to issues or PRs,
> or pasted into issue text. `assets/` and `data/` are gitignored. Keep it that
> way. Short quotes of a few words in a bug report are fine. Whole pages are not.

Every label follows [OUTPUT_FORMAT.md](OUTPUT_FORMAT.md).

## Sources and roles

| Source | Pages | Kind | Role |
|---|---|---|---|
| *My 60 Memorable Games*, Bobby Fischer (`assets/My 60 Memorable Games.pdf`) | 468 | Digital (calibre ebook conversion) | **Train / val / test.** Labels extracted exactly from the PDF |
| Synthetic pages (generated) | configurable | Rendered from CC0 / public-domain PGNs | **Train.** Adds variety in typefaces and layouts |
| *Chess Structures*, Mauricio Flores Rios (`assets/Chess Structures.pdf`) | 464 | Scanned (1-bit JBIG2) with a broken OCR text layer | **Held-out eval only.** About 25 hand-corrected pages |

### Why this split

The Fischer book uses one typeface and one layout. A model trained only on it
could learn that one book and not figurines in general. Chess Structures comes
from a different publisher, uses a different typeface and is a real scan, so it
shows whether the model generalizes. Synthetic data adds variety at training
time, and the generated pages carry no copyright.

## My 60 Memorable Games: label extraction

This PDF has a clean text layer in CharisSIL, **but the figurines are not
text**. Each one is a small inline JPEG image placed between the characters.
Plain text extraction drops them, which gives `On 5...h5 6 c4 h7 7 d4` where the
page shows `On 5…h5 6 ♗c4 ♖h7 7 d4`.

Observations from `pdfimages -list`:

- **5 distinct figurine images** (about 13–17 px), one per piece type (K, Q, R,
  B, N). They are reused about 12.8k times across the book. pdfimages reports
  object IDs 37, 38, 41, 43 and 46. Check these against PyMuPDF xrefs before
  relying on them.
- **About 255 large images**: board diagrams (about 430×187 px and similar),
  plus the cover and front-matter art.
- The main line is set as a move table (number / White / Black columns). The
  notes are flowing prose with inline figurines.

Extraction pipeline (milestone M2):

1. **Render** each page to PNG at a fixed DPI (default 200) with PyMuPDF.
2. **Map figurines.** A small, committed mapping file goes from image xref (or
   a content hash) to a glyph. Five entries, verified by eye once.
3. **Splice.** Merge the text spans and the figurine image boxes into lines by
   their y position, then order them by x. Each figurine glyph goes at the
   position of its image.
4. **Diagrams.** Large images inside the page body become `[DIAGRAM]`.
   Cover and front-matter images are excluded.
5. **Normalize** to the output spec: paragraph joining, de-hyphenation, move
   table rows, and dropping running headers and page numbers.
6. **Validate:**
   - Each page's figurine count must equal the number of figurine images on
     that page.
   - Main-line moves are replayed with `python-chess`. An illegal move points
     to a mapping or ordering bug.
   - Spot-check a random sample of pages by eye and record the results in the
     PR.

## Synthetic pages (milestone M3)

- **Games:** CC0 or public-domain PGNs, such as the Lichess open database (CC0)
  and classical master games.
- **Fonts:** only fonts whose license allows this use, recorded in
  `data/synthetic/FONTS.md` along with the license text. Examples to evaluate:
  DejaVu, FreeSerif, Noto Sans Symbols 2.
- **Layouts:** single and two-column pages, move tables, inline notes,
  diagrams (rendered with python-chess and labelled `[DIAGRAM]`) and
  Informator symbols.
- **Degradations:** binarization, blur, noise, JPEG artefacts, small rotations,
  and DPI between 150 and 300. These make clean renders look like scans.
- The generator writes the image and the label together, so the labels are
  correct by construction.

## Chess Structures: eval set (milestone M3)

- About 25 pages, stratified across prose-heavy pages, analysis-heavy pages
  (dense figurines), two-column pages with diagrams, and chapter openings.
- **Pre-fill, then correct.** Start from the PDF's own text layer. Apply
  junk-repair rules (for example `lt:J`→`♘`, `E!:`→`♖`, `t`→`±` where it
  appears as an evaluation symbol), then correct each page by hand against the
  image.
- Never used for training, hyperparameter tuning or checkpoint selection.
  Those decisions use the Fischer validation split.

## Splits

- Fischer pages are split **by game**, not by page, so the analysis of one
  game never appears in both train and test. Default split: 48 / 6 / 6 games
  (train / val / test). Front-matter and index pages go to train.
- The split assignment is a committed file (game ids only, no content), so it
  is reproducible.

## On-disk layout (gitignored)

```
data/
  pages/<source>/<page_id>.png        # rendered page images
  labels/<source>/<page_id>.txt       # target text (OUTPUT_FORMAT.md)
  manifests/<source>.jsonl            # one row per page (see below)
  synthetic/                          # generated pages + FONTS.md
```

Manifest row:

```json
{"page_id": "m60-0150", "source": "m60", "image": "data/pages/m60/m60-0150.png",
 "label": "data/labels/m60/m60-0150.txt", "split": "train", "game": 12}
```
