"""Export the integration's snapshot of a simulated stove for the macOS preview."""

import json
from pathlib import Path
from types import SimpleNamespace

from custom_components.maestro_mcz_plus.fields import LABELS, snapshot
from custom_components.maestro_mcz_plus.recipes import FIELDS


def main():
    stove = SimpleNamespace(
        State={
            "potenza_att": 2,
            "vel_real_ventola_fumi": 1340,
            "vel_real_coclea": 4.2,
            "t_dur_pul": 30,
            "t_int_pul": 1740,
        },
        Status={
            "temp_fumi": 126,
            "temp_scheda": 42,
            FIELDS["active_value"]: 1,
            FIELDS["active_enabled"]: True,
            FIELDS["pellet"]: -1,
            FIELDS["adaptive"]: False,
        },
    )
    source = Path(__file__).resolve().parents[1] / "custom_components" / "maestro_mcz_plus"
    translations = json.loads((source / "translations" / "es.json").read_text(encoding="utf-8"))
    sections = {"telemetry": [], "recipes": []}
    for key, value in snapshot(stove).items():
        platform = "binary_sensor" if isinstance(value, bool) else "sensor"
        label = translations["entity"][platform][key]["name"]
        unit = LABELS[key][1]
        display_value = ("Sí" if value else "No") if isinstance(value, bool) else str(value)
        section = "recipes" if key in FIELDS.values() else "telemetry"
        sections[section].append(
            {"id": key, "label": label, "value": f"{display_value} {unit}" if unit else display_value}
        )
    print(json.dumps(sections, ensure_ascii=False))


if __name__ == "__main__":
    main()
