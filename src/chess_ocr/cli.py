"""`chess-ocr` command-line entry point."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from chess_ocr import __version__, env

# Subcommands that are still stubs.
SUBCOMMANDS: dict[str, str] = {
    "ocr": "Run OCR on page images or PDF pages.",
    "eval": "Evaluate a backend on a labelled dataset.",
    "train": "Fine-tune a backend with QLoRA.",
    "data": "Build and inspect datasets.",
}


def _not_implemented(args: argparse.Namespace) -> int:
    print(f"chess-ocr {args.command}: not implemented yet", file=sys.stderr)
    return 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="chess-ocr",
        description="OCR for chess books that reads piece figurines correctly.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command", metavar="<command>", required=True)
    for name, help_text in SUBCOMMANDS.items():
        sub = subparsers.add_parser(name, help=help_text, description=help_text)
        sub.set_defaults(func=_not_implemented)
    env_help = "Check the CUDA / bitsandbytes environment."
    subparsers.add_parser("env", help=env_help, description=env_help).set_defaults(func=env.run)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
