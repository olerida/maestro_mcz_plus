"""Recipe switches."""
from homeassistant.components.switch import SwitchEntity
from .recipe_entity import RecipeEntity
from .recipes import discover_controls, read_value


async def async_setup_entry(hass, entry, async_add_entities):
    entities = []
    for coordinator, stove, lock in entry.runtime_data.sources:
        commands = discover_controls(stove)
        for key in ("adaptive", "active_enabled"):
            if key in commands:
                entities.append(RecipeSwitch(coordinator, stove, lock, commands, key))
    async_add_entities(entities)


class RecipeSwitch(RecipeEntity, SwitchEntity):
    _attr_icon = "mdi:toggle-switch"

    @property
    def is_on(self):
        return read_value(self._stove, self.key)

    async def async_turn_on(self, **kwargs):
        await self.send(True)

    async def async_turn_off(self, **kwargs):
        await self.send(False)
