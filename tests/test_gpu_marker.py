"""The --run-gpu option gates @pytest.mark.gpu tests (logic in tests/conftest.py)."""

from __future__ import annotations

from pathlib import Path

import pytest

CONFTEST = Path(__file__).with_name("conftest.py")

SAMPLE = """
import pytest

@pytest.mark.gpu
def test_needs_gpu():
    pass

def test_cpu():
    pass
"""


@pytest.fixture
def gpu_project(pytester: pytest.Pytester) -> pytest.Pytester:
    pytester.makeconftest(
        CONFTEST.read_text(encoding="utf-8").replace('pytest_plugins = ["pytester"]', "")
    )
    pytester.makeini("[pytest]\nmarkers =\n    gpu: needs a CUDA GPU\n")
    pytester.makepyfile(SAMPLE)
    return pytester


def test_gpu_tests_skipped_by_default(gpu_project: pytest.Pytester) -> None:
    result = gpu_project.runpytest("-rs")
    result.assert_outcomes(passed=1, skipped=1)
    result.stdout.fnmatch_lines(["*pass --run-gpu to run*"])


def test_gpu_tests_run_with_flag(gpu_project: pytest.Pytester) -> None:
    result = gpu_project.runpytest("--run-gpu")
    result.assert_outcomes(passed=2)
