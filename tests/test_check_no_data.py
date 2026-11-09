from __future__ import annotations

import importlib.util
import subprocess
from pathlib import Path
from types import ModuleType

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_no_data.py"


def _load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("check_no_data", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


cnd = _load()


def _touch(root: Path, rel: str, size: int = 10) -> str:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"\0" * size)
    return rel


@pytest.mark.parametrize("rel", ["assets/book.txt", "data/labels/p1.txt", "runs/a/adapter.bin"])
def test_blocked_dirs(tmp_path: Path, rel: str) -> None:
    assert cnd.find_violations([_touch(tmp_path, rel)], tmp_path)


def test_blocked_dirs_only_at_root(tmp_path: Path) -> None:
    rel = _touch(tmp_path, "src/chess_ocr/data/render.py")
    assert cnd.find_violations([rel], tmp_path) == []


@pytest.mark.parametrize("rel", ["book.pdf", "docs/x/Scan.PDF", "tests/fixtures/a.pdf"])
def test_pdf_anywhere(tmp_path: Path, rel: str) -> None:
    assert cnd.find_violations([_touch(tmp_path, rel)], tmp_path)


@pytest.mark.parametrize("rel", ["page.png", "src/chess_ocr/x.jpg", "tests/crop.tif"])
def test_image_outside_allowlist(tmp_path: Path, rel: str) -> None:
    problems = cnd.find_violations([_touch(tmp_path, rel)], tmp_path)
    assert any("only allowed under" in p for p in problems)


@pytest.mark.parametrize("rel", ["tests/fixtures/board.png", "docs/img/pipeline.jpg"])
def test_small_image_in_allowlist_ok(tmp_path: Path, rel: str) -> None:
    assert cnd.find_violations([_touch(tmp_path, rel, size=1024)], tmp_path) == []


def test_oversized_image_in_allowlist(tmp_path: Path) -> None:
    rel = _touch(tmp_path, "tests/fixtures/big.png", size=cnd.MAX_IMAGE_BYTES + 1)
    problems = cnd.find_violations([rel], tmp_path)
    assert len(problems) == 1 and "max 200 KB" in problems[0]


def test_image_at_limit_ok(tmp_path: Path) -> None:
    rel = _touch(tmp_path, "tests/fixtures/edge.png", size=cnd.MAX_IMAGE_BYTES)
    assert cnd.find_violations([rel], tmp_path) == []


def test_ordinary_files_ok(tmp_path: Path) -> None:
    rels = [_touch(tmp_path, p) for p in ("README.md", "src/chess_ocr/cli.py", "uv.lock")]
    assert cnd.find_violations(rels, tmp_path) == []


def test_windows_separators(tmp_path: Path) -> None:
    assert cnd.find_violations(["data\\labels\\p1.txt"], tmp_path)


def test_main_exit_codes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.chdir(tmp_path)
    assert cnd.main([_touch(tmp_path, "src/ok.py")]) == 0
    assert cnd.main([_touch(tmp_path, "data/leak.txt")]) == 1
    assert "data/leak.txt" in capsys.readouterr().err


def test_all_checks_force_added_files(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    def git(*args: str) -> None:
        subprocess.run(["git", *args], cwd=tmp_path, check=True, capture_output=True)

    git("init", "-q")
    (tmp_path / ".gitignore").write_text("/data/\n")
    git("add", _touch(tmp_path, "src/ok.py"), ".gitignore")
    monkeypatch.chdir(tmp_path)
    assert cnd.main(["--all"]) == 0

    git("add", "-f", _touch(tmp_path, "data/leak.txt"))
    assert cnd.main(["--all"]) == 1
    assert "data/leak.txt" in capsys.readouterr().err
