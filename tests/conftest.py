"""Shared pytest configuration: GPU tests are opt-in via --run-gpu."""

from __future__ import annotations

import pytest

pytest_plugins = ["pytester"]


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--run-gpu",
        action="store_true",
        default=False,
        help="run tests marked @pytest.mark.gpu (needs a CUDA GPU)",
    )


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    if config.getoption("--run-gpu"):
        return
    skip_gpu = pytest.mark.skip(reason="GPU test: pass --run-gpu to run")
    for item in items:
        if "gpu" in item.keywords:
            item.add_marker(skip_gpu)
