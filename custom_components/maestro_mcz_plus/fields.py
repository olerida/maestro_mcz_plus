"""Extract scalar fields without exposing credentials or identifiers."""
from dataclasses import fields, is_dataclass
from collections.abc import Mapping
import math
import re

from .recipes import FIELDS, field_value, read_value

# Network identifiers and account/device credentials are not telemetry.
PRIVATE = re.compile(r"password|passwd|pwd|secret|token|credential|ssid|mac_wifi|(?:^|_)serial|(?:^|_)sn$|unique.?code", re.I)
# Fields supported by app code, the existing integration, or observed device data.
# A label alone does not make an undocumented field confirmed.
CONFIRMED_FIELDS = frozenset({
    "pos_ric_flu", "pos_ric_pel", "mod_ada_on", "act", "pul_brac", "att_eco",
    "ingr_amb", "sens_liv_pellet", "adaptive_on", "potenza_att",
    "potenza_counter", "t_dur_pul", "t_int_pul", "set_pot_man", "pressione",
    "pressione_imp", "state", "state_duration", "mode", "is_connected",
    "is_in_error", "last_alarm", "crono_enabled", "silent_enabled",
    "sleep_enabled", "clean_in_prog", "clean_air_in_prog", "ore_prox_manut",
    "index_vel_v1", "index_vel_v2", "index_vel_v3", "set_amb1", "set_amb2",
    "set_amb3", "temp_fumi", "temp_scheda", "vel_real_ventola_fumi",
    "vel_imp_ventola_fumi", "vel_real_coclea", "vel_imp_coclea",
    "temp_caldaia", "temp_bollitore", "temp_puffer",
})
# Explicitly reviewed, non-private telemetry from the device inventory.
ALLOWED_FIELDS = CONFIRMED_FIELDS | frozenset({
    'absolute_battery_charge_level',
    'act',
    'act_acc',
    'adaptive_on',
    'am_pm',
    'anno',
    'att_eco',
    'auto_pellet',
    'battery_capacity',
    'clean_air_in_prog',
    'clean_in_prog',
    'com_es_car_coclea',
    'cont_fine_pul',
    'crono_enabled',
    'en_sav_m',
    'fase_op',
    'giorno',
    'giorno_sett',
    'has_battery',
    'index_vel_v1',
    'index_vel_v2',
    'index_vel_v3',
    'ing_term_amb1',
    'ingr_amb',
    'is_ble_connected',
    'is_connected',
    'is_crono_empty',
    'is_in_error',
    'is_live_only',
    'ist_eco_neg_amb',
    'ist_eco_pos_amb',
    'ist_neg_amb',
    'ist_pos_amb',
    'last_alarm',
    'last_stdt',
    'mc_vs_app',
    'mese',
    'minuti',
    'mod_ada_on',
    'mod_lav_att',
    'mode',
    'nome_banca_dati_sel',
    'ore',
    'ore_prox_manut',
    'pos_ric_asp',
    'pos_ric_flu',
    'pos_ric_pel',
    'potenza_att',
    'potenza_counter',
    'power_enabled',
    'pren_acc',
    'pres_pul',
    'pres_rete_ele',
    'pressione',
    'pressione_imp',
    'pressione_pascal',
    'pul_brac',
    'rit_ing_standby',
    'rit_usc_standby',
    'sav_m',
    'scheduled_turn_off_timestamp',
    'secondi',
    'sens_liv_pel',
    'sens_liv_pellet',
    'set_amb1',
    'set_amb2',
    'set_amb3',
    'set_pot_man',
    'set_vent_v1',
    'set_vent_v2',
    'set_vent_v3',
    'silent',
    'silent_enabled',
    'site_time_zone',
    'sleep_enabled',
    'sm_nome_app',
    'sm_vs_app',
    'state',
    'state_duration',
    'stato_stufa',
    'status',
    'status_timestamp',
    't_car_pel_man',
    't_dur_pul',
    't_int_pul',
    't_power',
    'temp_NTC3',
    'temp_amb_can1',
    'temp_amb_can2',
    'temp_amb_can3',
    'temp_amb_install',
    'temp_fumi',
    'temp_scheda',
    'toni_buzz',
    'turbo_activation_timestamp',
    'umid_rel',
    'v_ven1_v0',
    'v_ven2_v0',
    'v_ven3_v0',
    'vel_imp_coclea',
    'vel_imp_ventola_fumi',
    'vel_real_coclea',
    'vel_real_ventola_fumi',
    'wifi_status',
})

ICONS = {
    "pos_ric_flu": "mdi:tune-variant", "pos_ric_pel": "mdi:grain",
    "act": "mdi:toggle-switch",
    "mod_ada_on": "mdi:autorenew", "adaptive_on": "mdi:autorenew",
    "pul_brac": "mdi:broom", "att_eco": "mdi:leaf",
    "ingr_amb": "mdi:thermostat", "sens_liv_pellet": "mdi:grain",
    "potenza_att": "mdi:fire", "set_pot_man": "mdi:fire",
    "potenza_counter": "mdi:timer-outline", "state_duration": "mdi:timer-outline",
    "t_dur_pul": "mdi:timer-cog-outline", "t_int_pul": "mdi:timer-sand",
    "pressione": "mdi:gauge", "pressione_imp": "mdi:gauge",
    "state": "mdi:fireplace", "mode": "mdi:tune-variant",
    "is_connected": "mdi:connection", "is_in_error": "mdi:alert-circle-outline",
    "last_alarm": "mdi:alert-circle-outline", "crono_enabled": "mdi:calendar-clock",
    "silent_enabled": "mdi:volume-off", "sleep_enabled": "mdi:sleep",
    "clean_in_prog": "mdi:broom", "clean_air_in_prog": "mdi:air-filter",
    "ore_prox_manut": "mdi:wrench-clock",
    "index_vel_v1": "mdi:fan", "index_vel_v2": "mdi:fan", "index_vel_v3": "mdi:fan",
    "set_amb1": "mdi:thermometer", "set_amb2": "mdi:thermometer", "set_amb3": "mdi:thermometer",
    "temp_fumi": "mdi:thermometer", "temp_scheda": "mdi:thermometer",
    "temp_caldaia": "mdi:thermometer", "temp_bollitore": "mdi:thermometer", "temp_puffer": "mdi:thermometer",
    "vel_real_ventola_fumi": "mdi:fan", "vel_imp_ventola_fumi": "mdi:fan",
    "vel_real_coclea": "mdi:screw-lag", "vel_imp_coclea": "mdi:screw-lag",
}
LABELS = {
    "pos_ric_flu": ("Active recipe", None, None),
    "act": ("Active recipe enabled", None, None),
    "pos_ric_pel": ("Pellet recipe", None, None),
    "mod_ada_on": ("Adaptive mode recipe", None, None),
    "pul_brac": ("Matic", None, None),
    "att_eco": ("Start/Stop", None, None),
    "ingr_amb": ("T.EXT", None, None),
    "sens_liv_pellet": ("Pellet level sensor", None, None),
    "adaptive_on": ("Adaptive mode active", None, None),
    "potenza_att": ("Active power", None, None),
    "potenza_counter": ("Active power duration", None, None),
    "t_dur_pul": ("Expected brazier cleaning duration", "s", None),
    "set_pot_man": ("Selected manual power level", None, None),
    "pressione": ("Active actual", None, None),
    "pressione_imp": ("Active setpoint", None, None),
    "t_int_pul": ("Time until brazier cleaning", "s", None),
    "state": ("Stove state", None, None),
    "state_duration": ("State duration", None, None),
    "mode": ("Operating mode", None, None),
    "is_connected": ("Stove connected", None, None),
    "is_in_error": ("Stove error", None, None),
    "last_alarm": ("Last alarm", None, None),
    "crono_enabled": ("Timer enabled", None, None),
    "silent_enabled": ("Silent mode enabled", None, None),
    "sleep_enabled": ("Sleep mode enabled", None, None),
    "clean_in_prog": ("Cleaning in progress", None, None),
    "clean_air_in_prog": ("Air cleaning in progress", None, None),
    "ore_prox_manut": ("Hours until next maintenance", None, None),
    "index_vel_v1": ("Fan level 1", None, None),
    "index_vel_v2": ("Fan level 2", None, None),
    "index_vel_v3": ("Fan level 3", None, None),
    "set_amb1": ("Target room temperature 1", None, None),
    "set_amb2": ("Target room temperature 2", None, None),
    "set_amb3": ("Target room temperature 3", None, None),
    "temp_fumi": ("Exhaust temperature", "°C", "temperature"),
    "temp_scheda": ("Board temperature", "°C", "temperature"),
    "vel_real_ventola_fumi": ("Actual exhaust fan speed", "rpm", None),
    "vel_imp_ventola_fumi": ("Requested exhaust fan speed", "rpm", None),
    "vel_real_coclea": ("Actual auger speed", "rpm", None),
    "vel_imp_coclea": ("Requested auger speed", "rpm", None),
    "temp_caldaia": ("Boiler temperature", "°C", "temperature"),
    "temp_bollitore": ("Hot water tank temperature", "°C", "temperature"),
    "temp_puffer": ("Buffer tank temperature", "°C", "temperature"),
}
NUMERIC_TELEMETRY = frozenset(key for key, (_, unit, _) in LABELS.items() if unit)


def connection_state(stove):
    """Prefer the source's connectivity flag to the last polled readings."""
    reported = getattr(stove, "is_connected", None)
    if isinstance(reported, bool):
        return reported
    for source in ("Status", "State"):
        data = getattr(stove, source, None)
        reported = field_value(data, "is_connected")
        if isinstance(reported, bool):
            return reported
        reported = field_value(field_value(data, "unknown_fields"), "is_connected")
        if isinstance(reported, bool):
            return reported
    return None


def values(obj):
    if obj is None:
        return {}
    if isinstance(obj, Mapping):
        data = obj
    elif is_dataclass(obj):
        data = {field.name: getattr(obj, field.name, None) for field in fields(obj)}
    else:
        data = getattr(obj, "__dict__", {})
    result = {}
    for key, value in data.items():
        if key == "unknown_fields" and isinstance(value, Mapping):
            result.update(values(value))
        elif isinstance(key, str) and key in ALLOWED_FIELDS and not PRIVATE.search(key) and isinstance(value, (str, int, float, bool)):
            if key in NUMERIC_TELEMETRY and type(value) not in (int, float):
                continue
            # HA's state limit is 255 characters; containers and empty values are skipped.
            if isinstance(value, str) and (not value or len(value) > 255):
                continue
            if isinstance(value, float) and not math.isfinite(value):
                continue
            result[key] = value
    return result


def snapshot(stove):
    """Keep recipe sensors consistent with the values shown by the controls."""
    result = values(getattr(stove, "Status", None))
    result.update(values(getattr(stove, "State", None)))
    connected = connection_state(stove)
    if connected is None:
        result.pop("is_connected", None)
    else:
        result["is_connected"] = connected
    for key, field in FIELDS.items():
        value = read_value(stove, key)
        if value is None:
            result.pop(field, None)
        else:
            result[field] = value
    return result
