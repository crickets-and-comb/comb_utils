"""Tests conftest."""

import os

import pytest


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Mark test types."""
    unit_tests_dir = os.path.join(config.rootdir, "tests/unit")
    integration_tests_dir = os.path.join(config.rootdir, "tests/integration")
    e2e_tests_dir = os.path.join(config.rootdir, "tests/e2e")

    for item in items:
        test_path = str(item.fspath)
        if test_path.startswith(unit_tests_dir):
            item.add_marker("unit")
        elif test_path.startswith(integration_tests_dir):
            item.add_marker("integration")
        elif test_path.startswith(e2e_tests_dir):
            item.add_marker("e2e")
