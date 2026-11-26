"""Shared fixtures for TUI tests that run without the backend."""

from unittest.mock import Mock

import pytest


@pytest.fixture
def scripted_input(monkeypatch):
    """Provide scripted input without reading from the real terminal."""
    def configure(answers):
        reader = Mock(side_effect=list(answers))
        monkeypatch.setattr("builtins.input", reader)
        return reader

    return configure


@pytest.fixture
def sample_dish():
    """Local sample data, independent of the HTTP serialization contract."""
    return {
        "name": "Tomato pasta",
        "category": "PRIMO",
        "price_in_cents": 850,
        "available": True,
    }
