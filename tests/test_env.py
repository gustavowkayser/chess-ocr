from __future__ import annotations

import sys

import pytest

from chess_ocr import env
from chess_ocr.cli import main


def test_env_without_torch_prints_hint(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setitem(sys.modules, "torch", None)  # makes `import torch` raise ImportError
    assert main(["env"]) == 1
    assert "uv sync --group gpu" in capsys.readouterr().err


def test_help_lists_env(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit):
        main(["--help"])
    assert "env" in capsys.readouterr().out


def test_report_ok_requires_all_checks() -> None:
    assert not env.EnvReport().ok
    assert env.EnvReport(checks=[env.Check("a", True), env.Check("b", True)]).ok
    assert not env.EnvReport(checks=[env.Check("a", True), env.Check("b", False)]).ok


def test_format_report() -> None:
    report = env.EnvReport(
        info={"torch": "9.9", "GPU": "Fake"},
        checks=[env.Check("CUDA available", True), env.Check("bf16", False, "nope")],
    )
    text = env.format_report(report)
    assert "torch  9.9" in text
    assert "[PASS] CUDA available" in text
    assert "[FAIL] bf16: nope" in text
    assert text.endswith("Environment check FAILED")


@pytest.mark.gpu
def test_gpu_environment() -> None:
    report = env.collect()
    print(env.format_report(report))
    failed = [f"{c.name}: {c.detail}" for c in report.checks if not c.ok]
    assert report.ok, failed
