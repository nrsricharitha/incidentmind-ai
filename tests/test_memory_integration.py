"""Integration tests for Hindsight memory connectivity and provider."""

import os
import pytest
from src.config import settings
from src.memory.memory_service import MemoryService
from src.memory.hindsight import create_hindsight_provider


def test_hindsight_provider_initialization() -> None:
    """Test HindsightProvider creation logic under missing and dummy keys."""
    # When no key is set, returns None cleanly
    if not settings.hindsight_api_key:
        provider = create_hindsight_provider(api_key=None)
        assert provider is None

    # When key is provided, returns HindsightProvider instance
    provider_with_key = create_hindsight_provider(
        api_key="test_dummy_key", bank_id="test-bank"
    )
    assert provider_with_key is not None
    assert provider_with_key.bank_id == "test-bank"


def test_live_hindsight_integration() -> None:
    """Live integration test against Hindsight Cloud.

    Skips cleanly if HINDSIGHT_API_KEY is not configured in the test environment.
    """
    key = os.getenv("HINDSIGHT_API_KEY")
    if not key:
        pytest.skip(
            "HINDSIGHT_API_KEY not configured. Set HINDSIGHT_API_KEY in .env to run live integration test."
        )

    service = MemoryService(api_key=key, bank_id="incidentmind-test-bank")
    connected, msg = service.check_connection()
    assert connected is True, f"Failed to connect to Hindsight: {msg}"
