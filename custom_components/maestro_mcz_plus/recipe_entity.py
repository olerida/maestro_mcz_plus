"""Serialize recipe changes and verify them through the source coordinator."""

from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity import EntityCategory

from .entity import MaestroStoveEntity
from .recipes import ACTIVE_RECIPES, read_value


class RecipeEntity(MaestroStoveEntity):
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, coordinator, stove, lock, commands, key):
        super().__init__(coordinator, stove)
        self.lock = lock
        self.commands = commands
        self.key = key
        self._attr_unique_id = f"{stove.UniqueCode}-recipe-{key}"
        self._attr_translation_key = key

    @property
    def available(self):
        if not super().available or self.connected is not True:
            return False
        keys = ACTIVE_RECIPES if self.key in ACTIVE_RECIPES else (self.key,)
        return all(read_value(self._stove, key) is not None for key in keys)

    async def send(self, value):
        async with self.lock:
            if not self.available:
                raise HomeAssistantError("Stove or current recipe state is unavailable")
            values = {self.key: value}
            if self.key in ACTIVE_RECIPES:
                await self.coordinator.async_refresh()
                if not self.available:
                    raise HomeAssistantError("Could not refresh current Active settings")
                values = {
                    "active_value": value if self.key == "active_value" else read_value(self._stove, "active_value"),
                    "active_enabled": value if self.key == "active_enabled" else read_value(self._stove, "active_enabled"),
                }
                bounds = self.commands["active_value"]
                if not bounds.minimum <= values["active_value"] <= bounds.maximum:
                    raise HomeAssistantError("Current Active value is outside model limits")
            await self._send_commands(values)
            refresh = getattr(self.coordinator, "update_data_after_set", None)
            await (refresh or self.coordinator.async_refresh)()
            if not self.available or any(
                read_value(self._stove, key) != expected for key, expected in values.items()
            ):
                raise HomeAssistantError("The stove has not confirmed the updated recipe values")

    async def _send_commands(self, values):
        if callable(getattr(self._stove, "activateProgramMultipleCommands", None)):
            from custom_components.maestro_mcz.maestro.controller.requests.activate_program import ProgramCommand

            send_commands = self._stove.activateProgramMultipleCommands
        elif callable(getattr(self._stove, "ActivateProgramMultipleCommands", None)):
            from custom_components.maestro_mcz.maestro.http.request import MczProgramCommand as ProgramCommand

            send_commands = self._stove.ActivateProgramMultipleCommands
        else:
            raise HomeAssistantError("Maestro MCZ does not support recipe commands")

        config_id = self.commands[self.key].config_id
        commands = [ProgramCommand(self.commands[key].sensor_id, value) for key, value in values.items()]
        accepted = False

        def success():
            nonlocal accepted
            accepted = True

        await send_commands(config_id, commands, success)
        if not accepted:
            raise HomeAssistantError("Maestro MCZ did not confirm the request")
