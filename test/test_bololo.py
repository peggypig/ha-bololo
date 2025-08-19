import asyncio
import logging
import sys

from pytest_homeassistant_custom_component.common import MockConfigEntry
import pytest

_LOGGER = logging.getLogger(__name__)

if sys.platform == "win32":
    _LOGGER.info("set WindowsSelectorEventLoopPolicy for sys.platform : %s", sys.platform)
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


@pytest.fixture(scope="session")
@pytest.mark.asyncio
async def test_setup(hass):
    """Test setup."""
    _LOGGER.info("test_setup , hass : %s", hass)
    entry = MockConfigEntry(domain="bololo")
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
