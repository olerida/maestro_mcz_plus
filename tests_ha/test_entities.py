"""Exercise sensor creation and updates in an isolated Home Assistant."""
import logging
from types import SimpleNamespace

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from pytest_homeassistant_custom_component.common import MockConfigEntry


async def test_entities_follow_source_updates(hass):
    source = MockConfigEntry(domain="maestro_mcz", entry_id="source1", data={})
    source.add_to_hass(hass)
    stove = SimpleNamespace(
        UniqueCode="test-stove", State={"potenza_att": 2, "adaptive_on": False, "unconfirmed_value": 41}, Status={"temp_fumi": 100},
        get_device_info=lambda: {"identifiers": {("maestro_mcz", "test-stove")}, "name": "Test stove"},
    )
    coordinator = DataUpdateCoordinator(hass, logging.getLogger(__name__), name="test", config_entry=source)
    coordinator.maestroapi = stove
    hass.data["maestro_mcz"] = {source.entry_id: [coordinator]}
    result = await hass.config_entries.flow.async_init("maestro_mcz_plus", context={"source": config_entries.SOURCE_USER})
    result = await hass.config_entries.flow.async_configure(result["flow_id"], {"source_entry_id": source.entry_id})
    assert result["type"] is FlowResultType.CREATE_ENTRY
    await hass.async_block_till_done()
    entry = result["result"]
    assert entry.state is config_entries.ConfigEntryState.LOADED
    registry = er.async_get(hass)
    power_id = registry.async_get_entity_id("sensor", "maestro_mcz_plus", "test-stove-potenza_att")
    adaptive_id = registry.async_get_entity_id("binary_sensor", "maestro_mcz_plus", "test-stove-adaptive_on")
    unknown_id = registry.async_get_entity_id("sensor", "maestro_mcz_plus", "test-stove-unconfirmed_value")
    assert hass.states.get(power_id).state == "2"
    assert hass.states.get(adaptive_id).state == "off"
    assert unknown_id is None
    stove.State["potenza_att"] = 4
    stove.State["adaptive_on"] = True
    coordinator.async_set_updated_data({})
    await hass.async_block_till_done()
    assert hass.states.get(power_id).state == "4"
    assert hass.states.get(adaptive_id).state == "on"

    stove.State["is_connected"] = True
    stove.Status.update(is_connected=False)
    coordinator.async_set_updated_data({})
    await hass.async_block_till_done()
    connection_id = registry.async_get_entity_id("binary_sensor", "maestro_mcz_plus", "test-stove-is_connected")
    assert hass.states.get(connection_id).state == "off"
    assert hass.states.get(power_id).state == "unavailable"

    stove.is_connected = True
    stove.State["temp_fumi"] = "invalid"
    coordinator.async_set_updated_data({})
    await hass.async_block_till_done()
    temperature_id = registry.async_get_entity_id("sensor", "maestro_mcz_plus", "test-stove-temp_fumi")
    assert hass.states.get(connection_id).state == "on"
    assert hass.states.get(power_id).state == "4"
    assert hass.states.get(temperature_id).state == "100"

    stove.Status.pop("temp_fumi")
    coordinator.async_set_updated_data({})
    await hass.async_block_till_done()
    assert hass.states.get(temperature_id).state == "unavailable"
    assert await hass.config_entries.async_unload(entry.entry_id)


def test_snapshot_uses_same_recipe_readings_as_controls():
    from custom_components.maestro_mcz_plus.fields import snapshot

    stove = SimpleNamespace(
        State={"pos_ric_pel": 2, "potenza_att": 3},
        Status={"pos_ric_pel": -1, "act": False, "temp_fumi": float("nan")},
    )
    assert snapshot(stove) == {"pos_ric_pel": -1, "potenza_att": 3, "act": False}
