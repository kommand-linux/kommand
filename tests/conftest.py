"""Shared fixtures for all Kommand tests."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_context():
    """A fully mocked KommandContext for domain and adapter tests."""
    ctx = MagicMock()
    ctx.logger = MagicMock()
    ctx.config.get = MagicMock(return_value=75)
    ctx.privilege.has_sudo = True
    ctx.privilege.is_root = False
    ctx.privilege.current_password = None
    ctx.event_bus = MagicMock()
    ctx.domains = {}
    return ctx
