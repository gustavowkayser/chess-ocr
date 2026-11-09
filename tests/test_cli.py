from __future__ import annotations

import subprocess
import sys

import pytest

from chess_ocr import __version__
from chess_ocr.cli import SUBCOMMANDS, main


def test_help_lists_all_subcommands(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        main(["--help"])
    assert exc.value.code == 0
    out = capsys.readouterr().out
    for name in ("ocr", "eval", "train", "data"):
        assert name in out


def test_version(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit):
        main(["--version"])
    assert __version__ in capsys.readouterr().out


@pytest.mark.parametrize("command", sorted(SUBCOMMANDS))
def test_stub_subcommands_exit_nonzero(command: str, capsys: pytest.CaptureFixture[str]) -> None:
    assert main([command]) != 0
    assert "not implemented" in capsys.readouterr().err


def test_no_subcommand_is_an_error() -> None:
    with pytest.raises(SystemExit) as exc:
        main([])
    assert exc.value.code != 0


def test_console_entry_point_runs() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "chess_ocr.cli", "--help"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert "train" in result.stdout
