"""Discover only recipe commands identified in the app and model metadata."""
from collections.abc import Mapping
from dataclasses import dataclass
import math

# Maestro+ 5.8.0 selects these IDs from its sensor-set tables (MECHANICS.md).
IDS = {
    "pellet": {"e50abf4a-6e52-487c-8637-1d00d8978359", "8c59dc5a-4e7d-4706-8ac3-e144ed8a9515"},
    "adaptive": {"f5ee03fd-7f71-48fb-8e71-46d5d4cf56d5", "b22fb6e1-d8d2-4857-b9bf-07bfcf10fe91"},
    "active_value": {"307ba615-e58f-4df0-944a-a1df97c73e06", "8056d063-f5e0-48c7-9960-90b48ca81798"},
    "active_enabled": {"2998639c-8240-4bc5-9331-2b9aa9ffc1a2", "9156d446-2062-40c7-bea7-4934c5e5d79a"},
}
# Pair each configuration with the corresponding sensor family. Never mix
# otherwise recognized IDs from different model families in one request.
FAMILY_IDS = {
    "f6538f6b-ef3d-4ed7-9ab6-4b3b97fc0e1f": {
        "e50abf4a-6e52-487c-8637-1d00d8978359", "f5ee03fd-7f71-48fb-8e71-46d5d4cf56d5",
        "307ba615-e58f-4df0-944a-a1df97c73e06", "2998639c-8240-4bc5-9331-2b9aa9ffc1a2",
    },
    "62bfda67-95b2-4372-804d-0f7013d857e0": {
        "8c59dc5a-4e7d-4706-8ac3-e144ed8a9515", "b22fb6e1-d8d2-4857-b9bf-07bfcf10fe91",
        "8056d063-f5e0-48c7-9960-90b48ca81798", "9156d446-2062-40c7-bea7-4934c5e5d79a",
    },
}
CONFIG_IDS = set(FAMILY_IDS)
FIELDS = {"pellet": "pos_ric_pel", "adaptive": "mod_ada_on", "active_value": "pos_ric_flu", "active_enabled": "act"}
NUMERIC_RECIPES = {"pellet", "active_value"}
ACTIVE_RECIPES = {"active_enabled", "active_value"}
COMMAND_METHODS = ("activateProgramMultipleCommands", "ActivateProgramMultipleCommands")


@dataclass(frozen=True)
class Command:
    config_id: str
    sensor_id: str
    minimum: int | None = None
    maximum: int | None = None


def discover(model):
    """Require unique known IDs and valid model-specific numeric bounds."""
    candidates = {key: [] for key in IDS}
    for group in getattr(model, "model_configurations", None) or []:
        config_id = str(getattr(group, "configuration_id", "")).lower()
        if config_id not in CONFIG_IDS:
            continue
        for item in getattr(group, "configurations", None) or []:
            sensor_id = str(getattr(item, "sensor_id", "")).lower()
            if sensor_id not in FAMILY_IDS[config_id] or getattr(item, "enabled", None) is not True:
                continue
            for key, ids in IDS.items():
                if sensor_id not in ids:
                    continue
                expected_type = "int" if key in NUMERIC_RECIPES else "boolean"
                if getattr(item, "type", None) != expected_type:
                    continue
                low = high = None
                if key in NUMERIC_RECIPES:
                    try:
                        lo, hi = float(item.min), float(item.max)
                        if not math.isfinite(lo) or not math.isfinite(hi):
                            continue
                        low, high = math.ceil(lo), math.floor(hi)
                        if low > high:
                            continue
                    except (TypeError, ValueError, AttributeError, OverflowError):
                        continue
                candidates[key].append(Command(config_id, sensor_id, low, high))
    commands = {key: values[0] for key, values in candidates.items() if len(values) == 1}
    active_configurations = {commands[key].config_id for key in ACTIVE_RECIPES if key in commands}
    if not ACTIVE_RECIPES <= commands.keys() or len(active_configurations) != 1:
        for key in ACTIVE_RECIPES:
            commands.pop(key, None)
    return commands


def discover_controls(stove):
    """Offer controls only when the source has a recipe command interface."""
    if any(callable(getattr(stove, name, None)) for name in COMMAND_METHODS):
        return discover(getattr(stove, "Model", None))
    return {}


def field_value(data, field, default=None):
    """Read fields from the models or plain mappings used by the source."""
    if isinstance(data, Mapping):
        return data.get(field, default)
    return getattr(data, field, default)


def read_value(stove, key):
    expected = int if key in NUMERIC_RECIPES else bool
    for data in (getattr(stove, "Status", None), getattr(stove, "State", None)):
        value = field_value(data, FIELDS[key])
        if value is None:
            value = field_value(field_value(data, "unknown_fields"), FIELDS[key])
        if value is not None:
            return value if type(value) is expected else None
    return None
