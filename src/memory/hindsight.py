"""Hindsight long-term memory integration for Microsoft Agent Framework."""

import logging
from typing import Optional
from hindsight_agent_framework import HindsightProvider
from src.config import settings

logger = logging.getLogger(__name__)

INCIDENTMIND_MISSION = (
    "IncidentMind AI operational memory bank. Retains and recalls technical incidents, "
    "failure modes, observable symptoms, affected services, root causes, executed runbooks, "
    "and successful resolution steps to assist incident responders."
)


def create_hindsight_provider(
    bank_id: Optional[str] = None,
    api_key: Optional[str] = None,
    api_url: Optional[str] = None,
    auto_recall: bool = True,
    auto_retain: bool = True,
) -> Optional[HindsightProvider]:
    """Create a HindsightProvider instance for Microsoft Agent Framework.

    Args:
        bank_id: Memory bank ID (defaults to settings.hindsight_bank_id).
        api_key: Hindsight API key (defaults to settings.hindsight_api_key).
        api_url: Hindsight API base URL (defaults to settings.hindsight_api_url).
        auto_recall: Automatically recall memories before agent run.
        auto_retain: Automatically retain conversation after agent run.

    Returns:
        HindsightProvider instance if configured, or None if no API key is provided.
    """
    key = api_key or settings.hindsight_api_key
    url = api_url or settings.hindsight_api_url
    bank = bank_id or settings.hindsight_bank_id

    if not key:
        logger.warning(
            "Hindsight API key not found. HindsightProvider cannot be initialized."
        )
        return None

    try:
        provider = HindsightProvider(
            bank_id=bank,
            api_key=key,
            hindsight_api_url=url,
            budget="mid",
            max_tokens=4096,
            context="incidentmind-agent",
            tags=["incident", "resolution", "root_cause"],
            recall_tags=None,
            recall_tags_match="any",
            mission=INCIDENTMIND_MISSION,
            auto_recall=auto_recall,
            auto_retain=auto_retain,
            source_id="hindsight",
        )
        logger.info("Initialized HindsightProvider for bank: %s", bank)
        return provider
    except Exception as e:
        logger.error("Failed to initialize HindsightProvider: %s", e)
        return None
