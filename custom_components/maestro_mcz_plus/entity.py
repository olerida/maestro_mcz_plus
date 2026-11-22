"""Discover new values from the existing integration's updates."""
from homeassistant.core import callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import SOURCE_DOMAIN
from .fields import CONFIRMED_FIELDS, ICONS, LABELS, connection_state, snapshot


async def setup_sensors(hass, entry, async_add_entities, entity_class, boolean):
    registry = er.async_get(hass)
    for coordinator, stove, _ in entry.runtime_data.sources:
        known = set()
        prefix = f"{stove.UniqueCode}-"

        @callback
        def discover(coordinator=coordinator, stove=stove, known=known, prefix=prefix):
            existing = {item.unique_id[len(prefix):] for item in registry.entities.values()
                        if item.platform == SOURCE_DOMAIN and item.unique_id.startswith(prefix)}
            new = []
            for key, value in snapshot(stove).items():
                if key in known or key in existing or isinstance(value, bool) != boolean:
                    continue
                known.add(key)
                new.append(entity_class(coordinator, stove, key))
            if new:
                async_add_entities(new)

        discover()
        entry.async_on_unload(coordinator.async_add_listener(discover))


class MaestroStoveEntity(CoordinatorEntity):
    """Share the upstream device and connection status."""

    _attr_has_entity_name = True

    def __init__(self, coordinator, stove):
        super().__init__(coordinator)
        self._stove = stove
        device_info = getattr(stove, "get_device_info", None)
        if not callable(device_info):
            device_info = getattr(coordinator, "get_device_info", None)
        self._attr_device_info = (
            device_info() if callable(device_info)
            else {"identifiers": {(SOURCE_DOMAIN, stove.UniqueCode)}}
        )

    @property
    def connected(self):
        return connection_state(self._stove)


class ExtraEntity(MaestroStoveEntity):
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator, stove, key):
        super().__init__(coordinator, stove)
        self._key = key
        self._attr_unique_id = f"{stove.UniqueCode}-{key}"
        self._attr_icon = ICONS.get(key, "mdi:help-circle-outline")
        self._attr_entity_registry_enabled_default = key in CONFIRMED_FIELDS
        if key in LABELS:
            self._attr_translation_key = key
        else:
            self._attr_name = key

    @property
    def available(self):
        return (
            super().available
            and (self.connected is not False or self._key == "is_connected")
            and self._key in snapshot(self._stove)
        )
