"""Fail if copyrighted data (or anything that looks like it) is about to be committed.

Usage:
    check_no_data.py PATH...   check the given paths (pre-commit passes staged files)
    check_no_data.py --all     check every file tracked by git (CI)

Rules (paths are repo-relative, forward slashes):
    - nothing under assets/, data/ or runs/
    - no *.pdf anywhere
    - raster images only under an allowlisted directory
    - raster images at most MAX_IMAGE_BYTES, allowlist included
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from collections.abc import Iterable, Sequence
from pathlib import Path, PurePosixPath

BLOCKED_DIRS = ("assets", "data", "runs")
IMAGE_ALLOWLIST = ("tests/fixtures", "docs/img")
IMAGE_SUFFIXES = frozenset(
    {
        ".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".gif", ".webp",
        ".ppm", ".pgm", ".pbm", ".pnm", ".jp2", ".jpx", ".jxl", ".avif", ".heic",
    }
)  # fmt: skip
MAX_IMAGE_BYTES = 200 * 1024


def _under(path: PurePosixPath, directory: str) -> bool:
    return path.parts[: len(PurePosixPath(directory).parts)] == PurePosixPath(directory).parts


def check_path(rel: str, root: Path) -> list[str]:
    """Return the rule violations for one repo-relative path."""
    path = PurePosixPath(rel.replace("\\", "/"))
    problems: list[str] = []
    if path.parts and path.parts[0] in BLOCKED_DIRS:
        problems.append(f"{path}: files under {path.parts[0]}/ must never be committed")
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        problems.append(f"{path}: PDF files must never be committed")
    if suffix in IMAGE_SUFFIXES:
        if not any(_under(path, d) for d in IMAGE_ALLOWLIST):
            allowed = ", ".join(f"{d}/" for d in IMAGE_ALLOWLIST)
            problems.append(f"{path}: images are only allowed under {allowed}")
        file = root / path
        if file.is_file() and (size := file.stat().st_size) > MAX_IMAGE_BYTES:
            problems.append(
                f"{path}: image is {size // 1024} KB (max {MAX_IMAGE_BYTES // 1024} KB)"
            )
    return problems


def find_violations(paths: Iterable[str], root: Path) -> list[str]:
    return [problem for rel in paths for problem in check_path(rel, root)]


def tracked_files(root: Path) -> list[str]:
    out = subprocess.run(
        ["git", "ls-files", "-z"], cwd=root, capture_output=True, check=True
    ).stdout
    return [p for p in out.decode("utf-8").split("\0") if p]


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("paths", nargs="*", help="repo-relative paths to check")
    parser.add_argument("--all", action="store_true", help="check all git-tracked files")
    args = parser.parse_args(argv)

    root = Path.cwd()
    paths = tracked_files(root) if args.all else args.paths
    problems = find_violations(paths, root)
    for problem in problems:
        print(problem, file=sys.stderr)
    if problems:
        print(
            "\nCopyrighted books and derived data must stay out of git (docs/DATASET.md).",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
