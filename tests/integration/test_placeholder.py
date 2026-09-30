"""Temporary integration-test placeholder for CI discovery."""

import pytest


@pytest.mark.skip(reason="Integration tests are added with their corresponding features.")
def test_integration_placeholder() -> None:
    """Keep pytest successful while the integration suite is intentionally empty."""
