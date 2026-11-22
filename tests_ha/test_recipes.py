"""Verify recipe commands without any network or stove."""
import asyncio
from types import SimpleNamespace as NS
from unittest.mock import AsyncMock, MagicMock
import pytest
from homeassistant.exceptions import HomeAssistantError
from custom_components.maestro_mcz_plus.recipes import discover, read_value, IDS, CONFIG_IDS, Command
from custom_components.maestro_mcz_plus.number import RecipeNumber
from custom_components.maestro_mcz_plus.switch import RecipeSwitch


def fixture():
    cid = 'f6538f6b-ef3d-4ed7-9ab6-4b3b97fc0e1f'
    ids = ['e50abf4a-6e52-487c-8637-1d00d8978359', 'f5ee03fd-7f71-48fb-8e71-46d5d4cf56d5', '307ba615-e58f-4df0-944a-a1df97c73e06', '2998639c-8240-4bc5-9331-2b9aa9ffc1a2']
    model = NS(model_configurations=[NS(configuration_id=cid, configurations=[NS(sensor_id=i, enabled=True, type=('int' if n in (0, 2) else 'boolean'), min='-3', max='3') for n, i in enumerate(ids)])])
    return model, discover(model)


def test_discovery_requires_matching_enabled_configuration_and_bounds():
    model, commands = fixture()
    assert set(commands) == set(IDS)
    assert (commands['pellet'].minimum, commands['pellet'].maximum) == (-3, 3)
    item = model.model_configurations[0].configurations[0]
    item.enabled = False
    assert 'pellet' not in discover(model)
    item.enabled = True
    item.min, item.max = "-5.5", "4.5"
    pellet = discover(model)["pellet"]
    assert (pellet.minimum, pellet.maximum) == (-5, 4)
    item.min = None
    assert 'pellet' not in discover(model)
    model.model_configurations[0].configuration_id = 'unknown'
    assert not discover(model)


@pytest.mark.asyncio
async def test_active_write_preserves_other_setting_and_handles_failure(hass, monkeypatch):
    import sys
    from types import ModuleType
    module = ModuleType("custom_components.maestro_mcz.maestro.http.request")
    class MczProgramCommand:
        def __init__(self, sensor_id, value):
            self.SensorId, self.Value = sensor_id, value
    module.MczProgramCommand = MczProgramCommand
    monkeypatch.setitem(sys.modules, module.__name__, module)
    _, commands = fixture()
    coordinator = MagicMock(last_update_success=True)
    coordinator.get_device_info.return_value = {}
    coordinator.update_data_after_set = AsyncMock()
    stove = NS(UniqueCode='test', Status=NS(pos_ric_flu=0, act=False, is_connected=True), State=None)
    async def refresh():
        stove.Status.act = True
    coordinator.async_refresh = AsyncMock(side_effect=refresh)
    calls = []
    async def send(config, items, callback):
        calls.append((config, items))
        stove.Status.pos_ric_flu = next(c.Value for c in items if c.SensorId == commands['active_value'].sensor_id)
        stove.Status.act = next(c.Value for c in items if c.SensorId == commands['active_enabled'].sensor_id)
        callback()
    stove.ActivateProgramMultipleCommands = send
    entity = RecipeNumber(coordinator, stove, asyncio.Lock(), commands, 'active_value')
    await entity.async_set_native_value(2)
    assert [(c.SensorId, c.Value) for c in calls[0][1]] == [
        (commands['active_value'].sensor_id, 2),
        (commands['active_enabled'].sensor_id, True),
    ]
    coordinator.update_data_after_set.assert_awaited_once()
    coordinator.async_refresh.assert_awaited_once()
    with pytest.raises(HomeAssistantError):
        await entity.async_set_native_value(4)
    assert len(calls) == 1
    toggle = RecipeSwitch(coordinator, stove, entity.lock, commands, 'active_enabled')
    await toggle.async_turn_off()
    assert [(c.SensorId, c.Value) for c in calls[1][1]] == [
        (commands['active_value'].sensor_id, 2),
        (commands['active_enabled'].sensor_id, False),
    ]
    async def fail(*args): pass
    stove.ActivateProgramMultipleCommands = fail
    with pytest.raises(HomeAssistantError):
        await entity.async_set_native_value(1)

async def test_advanced_mode_adds_control_platforms(hass):
    from unittest.mock import patch
    from homeassistant.const import Platform
    from pytest_homeassistant_custom_component.common import MockConfigEntry
    from custom_components.maestro_mcz_plus import async_setup_entry
    source = MockConfigEntry(domain="maestro_mcz", entry_id="recipe-source")
    source.add_to_hass(hass)
    coordinator = NS(maestroapi=object(), last_update_success=True)
    hass.data['maestro_mcz'] = {source.entry_id: [coordinator]}
    for advanced, expected in [(False, {Platform.SENSOR, Platform.BINARY_SENSOR}), (True, {Platform.SENSOR, Platform.BINARY_SENSOR, Platform.NUMBER, Platform.SWITCH})]:
        entry = MockConfigEntry(domain="maestro_mcz_plus", data={"source_entry_id": source.entry_id, "advanced": advanced})
        entry.add_to_hass(hass)
        with patch.object(hass.config_entries, 'async_forward_entry_setups', new=AsyncMock()) as forward:
            await async_setup_entry(hass, entry)
            assert set(forward.await_args.args[1]) == expected

async def test_controls_only_for_recognized_and_compatible_metadata(hass):
    from custom_components.maestro_mcz_plus import number, switch
    model, _ = fixture()
    coordinator = MagicMock(last_update_success=True)
    coordinator.get_device_info.return_value = {}
    stove = NS(UniqueCode='test', Model=model, ActivateProgramMultipleCommands=AsyncMock(), Status=NS(pos_ric_pel=0, pos_ric_flu=0, act=True, mod_ada_on=False, is_connected=True), State=None)
    entry = NS(runtime_data=NS(sources=[(coordinator, stove, asyncio.Lock())]))
    entities = []
    await number.async_setup_entry(hass, entry, entities.extend)
    await switch.async_setup_entry(hass, entry, entities.extend)
    assert {entity.key for entity in entities} == {'pellet', 'active_value', 'active_enabled', 'adaptive'}
    assert {entity.key: (entity.native_value if isinstance(entity, RecipeNumber) else entity.is_on) for entity in entities} == {'pellet': 0, 'active_value': 0, 'active_enabled': True, 'adaptive': False}
    model.model_configurations[0].configurations[-1].enabled = False
    entities = []
    await number.async_setup_entry(hass, entry, entities.extend)
    await switch.async_setup_entry(hass, entry, entities.extend)
    assert {entity.key for entity in entities} == {'pellet', 'adaptive'}

async def test_adaptive_command_and_unavailable_stove(hass, monkeypatch):
    import sys
    from types import ModuleType
    module = ModuleType('custom_components.maestro_mcz.maestro.http.request')
    class CommandItem:
        def __init__(self, sensor_id, value):
            self.SensorId, self.Value = sensor_id, value
    module.MczProgramCommand = CommandItem
    monkeypatch.setitem(sys.modules, module.__name__, module)
    _, commands = fixture()
    coordinator = MagicMock(last_update_success=True)
    coordinator.get_device_info.return_value = {}
    coordinator.update_data_after_set = AsyncMock()
    stove = NS(UniqueCode='test', Status=NS(mod_ada_on=False, is_connected=True), State=None)
    sent = []
    async def send(config, items, callback):
        sent.append((config, items))
        if items[0].SensorId == commands['adaptive'].sensor_id:
            stove.Status.mod_ada_on = items[0].Value
        else:
            stove.Status.pos_ric_flu = items[0].Value
        callback()
    stove.ActivateProgramMultipleCommands = send
    entity = RecipeSwitch(coordinator, stove, asyncio.Lock(), commands, 'adaptive')
    await entity.async_turn_on()
    assert sent[0][0] == commands['adaptive'].config_id
    assert [(item.SensorId, item.Value) for item in sent[0][1]] == [(commands['adaptive'].sensor_id, True)]
    stove.Status.is_connected = False
    with pytest.raises(HomeAssistantError):
        await entity.async_turn_off()
    assert len(sent) == 1


async def test_accepted_command_without_matching_readback_is_reported(monkeypatch):
    import sys
    from types import ModuleType

    module = ModuleType("custom_components.maestro_mcz.maestro.http.request")
    module.MczProgramCommand = Command
    monkeypatch.setitem(sys.modules, module.__name__, module)
    _, commands = fixture()
    coordinator = NS(last_update_success=True, async_refresh=AsyncMock())
    stove = NS(
        UniqueCode="test",
        Status={"mod_ada_on": False, "is_connected": True},
        ActivateProgramMultipleCommands=AsyncMock(side_effect=lambda config, items, success: success()),
    )
    entity = RecipeSwitch(coordinator, stove, asyncio.Lock(), commands, "adaptive")

    with pytest.raises(HomeAssistantError, match="has not confirmed"):
        await entity.async_turn_on()
    stove.ActivateProgramMultipleCommands.assert_awaited_once()
    coordinator.async_refresh.assert_awaited_once()

def test_rejects_mixed_model_family_and_invalid_types():
    model, _ = fixture()
    items = model.model_configurations[0].configurations
    items[0].sensor_id = '8c59dc5a-4e7d-4706-8ac3-e144ed8a9515'
    items[1].type = 'int'
    commands = discover(model)
    assert 'pellet' not in commands
    assert 'adaptive' not in commands
    assert {'active_value', 'active_enabled'} <= commands.keys()

async def test_source_setup_retry_and_unload(hass):
    from unittest.mock import patch
    from homeassistant.exceptions import ConfigEntryNotReady
    from pytest_homeassistant_custom_component.common import MockConfigEntry
    from custom_components.maestro_mcz_plus import async_setup_entry, async_unload_entry
    source = MockConfigEntry(domain='maestro_mcz', entry_id='retry-source')
    source.add_to_hass(hass)
    entry = MockConfigEntry(domain='maestro_mcz_plus', data={'source_entry_id': source.entry_id})
    entry.add_to_hass(hass)
    coordinator = NS(maestroapi=object(), last_update_success=False)
    hass.data['maestro_mcz'] = {source.entry_id: [coordinator]}
    with pytest.raises(ConfigEntryNotReady):
        await async_setup_entry(hass, entry)
    coordinator.last_update_success = True
    with patch.object(hass.config_entries, 'async_forward_entry_setups', new=AsyncMock()):
        assert await async_setup_entry(hass, entry)
    with patch.object(hass.config_entries, 'async_unload_platforms', new=AsyncMock(return_value=True)) as unload:
        assert await async_unload_entry(hass, entry)
        unload.assert_awaited_once()


async def test_source_layouts_use_each_stove(hass):
    """Support the legacy, per-device and per-account source layouts."""
    from pytest_homeassistant_custom_component.common import MockConfigEntry
    from custom_components.maestro_mcz_plus import get_sources

    source = MockConfigEntry(domain="maestro_mcz", entry_id="source-layouts")
    source.add_to_hass(hass)
    one, two = object(), object()
    old = NS(maestroapi=one)
    hass.data["maestro_mcz"] = {source.entry_id: [old]}
    assert get_sources(hass, source.entry_id) == [(old, one)]
    first, second = NS(stove=one), NS(stove=two)
    source.runtime_data = {"one": first, "two": second}
    assert get_sources(hass, source.entry_id) == [(first, one), (second, two)]
    account = NS(stoves={"one": one, "two": two})
    source.runtime_data = account
    assert get_sources(hass, source.entry_id) == [(account, one), (account, two)]
    source.runtime_data = NS(account=object(), coordinator=account)
    assert get_sources(hass, source.entry_id) == [(account, one), (account, two)]
    source.runtime_data = NS(stoves=None)
    assert get_sources(hass, source.entry_id) == []


async def test_current_command_interface_and_device_info(hass, monkeypatch):
    """Send the paired values through the newer command interface."""
    import sys
    from types import ModuleType
    module = ModuleType("custom_components.maestro_mcz.maestro.controller.requests.activate_program")
    class ProgramCommand:
        def __init__(self, sensor_id, value):
            self.SensorId, self.Value = sensor_id, value
    module.ProgramCommand = ProgramCommand
    monkeypatch.setitem(sys.modules, module.__name__, module)
    _, commands = fixture()
    coordinator = MagicMock(spec=["last_update_success", "async_refresh", "update_data_after_set"])
    coordinator.last_update_success = True
    coordinator.async_refresh = AsyncMock()
    coordinator.update_data_after_set = AsyncMock()
    stove = NS(UniqueCode="test", Status=NS(pos_ric_flu=0, act=True), State=None,
               is_connected=True, get_device_info=lambda: {"identifiers": {("maestro_mcz", "test")}})
    sent = []
    async def send(config, items, callback):
        sent.append((config, items))
        if items[0].SensorId == commands['adaptive'].sensor_id:
            stove.Status.mod_ada_on = items[0].Value
        else:
            stove.Status.pos_ric_flu = items[0].Value
        callback()
    stove.activateProgramMultipleCommands = send
    entity = RecipeNumber(coordinator, stove, asyncio.Lock(), commands, "active_value")
    await entity.async_set_native_value(2)
    assert {(item.SensorId, item.Value) for item in sent[0][1]} == {
        (commands["active_value"].sensor_id, 2), (commands["active_enabled"].sensor_id, True)}
    assert entity.device_info["identifiers"] == {("maestro_mcz", "test")}
    coordinator.update_data_after_set.assert_awaited_once()
    stove.is_connected = False
    with pytest.raises(HomeAssistantError):
        await entity.async_set_native_value(1)
    assert len(sent) == 1

async def test_active_refresh_failure_prevents_write(hass):
    import sys
    from types import ModuleType
    from unittest.mock import patch
    module = ModuleType("custom_components.maestro_mcz.maestro.http.request")
    module.MczProgramCommand = object
    _, commands = fixture()
    coordinator = MagicMock(last_update_success=True)
    coordinator.get_device_info.return_value = {}
    async def fail_refresh():
        coordinator.last_update_success = False
    coordinator.async_refresh = AsyncMock(side_effect=fail_refresh)
    stove = NS(UniqueCode='test', Status=NS(pos_ric_flu=0, act=True, is_connected=True), State=None, ActivateProgramMultipleCommands=AsyncMock())
    entity = RecipeNumber(coordinator, stove, asyncio.Lock(), commands, 'active_value')
    with patch.dict(sys.modules, {module.__name__: module}):
        with pytest.raises(HomeAssistantError):
            await entity.async_set_native_value(1)
    stove.ActivateProgramMultipleCommands.assert_not_awaited()

async def test_options_reload_switches_modes_and_preserves_account(hass):
    """Changing options unloads the old platforms and retains legacy data."""
    import logging
    from homeassistant.components.number import DOMAIN as NUMBER_DOMAIN
    from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
    from homeassistant.data_entry_flow import FlowResultType
    from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
    from pytest_homeassistant_custom_component.common import MockConfigEntry

    source = MockConfigEntry(domain='maestro_mcz', entry_id='source-options')
    source.add_to_hass(hass)
    model, _ = fixture()
    stove = NS(UniqueCode='test-options', Model=model, ActivateProgramMultipleCommands=AsyncMock(),
               Status=NS(pos_ric_pel=0, pos_ric_flu=0, act=True, mod_ada_on=False, is_connected=True), State=None)
    coordinator = DataUpdateCoordinator(hass, logging.getLogger(__name__), name='test', config_entry=source)
    coordinator.maestroapi = stove
    coordinator.get_device_info = lambda: {'identifiers': {('maestro_mcz', 'test-options')}, 'name': 'Test stove'}
    hass.data['maestro_mcz'] = {source.entry_id: [coordinator]}
    entry = MockConfigEntry(domain='maestro_mcz_plus', data={'source_entry_id': source.entry_id, 'advanced': False})
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    assert len(hass.states.async_entity_ids(SENSOR_DOMAIN)) == 2
    assert all(hass.states.get(entity_id).state == 'unavailable' for entity_id in hass.states.async_entity_ids(NUMBER_DOMAIN))

    flow = await hass.config_entries.options.async_init(entry.entry_id)
    assert flow['type'] is FlowResultType.FORM
    result = await hass.config_entries.options.async_configure(flow['flow_id'], {'advanced': True})
    assert result['type'] is FlowResultType.CREATE_ENTRY
    await hass.async_block_till_done()
    assert entry.options['advanced'] is True
    assert entry.data['source_entry_id'] == source.entry_id
    assert len(hass.states.async_entity_ids(NUMBER_DOMAIN)) == 2
    assert {hass.states.get(entity_id).state for entity_id in hass.states.async_entity_ids(SENSOR_DOMAIN)} == {'0'}

    flow = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(flow['flow_id'], {'advanced': False})
    assert result['type'] is FlowResultType.CREATE_ENTRY
    await hass.async_block_till_done()
    assert entry.options['advanced'] is False
    assert len(hass.states.async_entity_ids(SENSOR_DOMAIN)) == 2
    assert all(hass.states.get(entity_id).state == 'unavailable' for entity_id in hass.states.async_entity_ids(NUMBER_DOMAIN))
