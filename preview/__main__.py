"""Launch the local macOS preview from Craft Anything's Play button."""

import os
from pathlib import Path
import subprocess
import sys


def main():
    app = Path(__file__).resolve().parents[1]
    bundle = app / "dist/Maestro MCZ Plus Preview.app/Contents"
    executable = bundle / "MacOS/MaestroPreview"
    if needs_build(app, bundle, executable):
        subprocess.run([str(app / "build.sh")], check=True)
    os.execv(executable, [str(executable), *sys.argv[1:]])


def needs_build(app, bundle, executable):
    if not executable.is_file() or not (bundle / "Resources/sample.json").is_file():
        return True
    compiled_at = executable.stat().st_mtime_ns
    sources = [
        app / "build.sh",
        app / "preview/Info.plist",
        app / "preview/MaestroPreview.swift",
        app / "preview/sample.py",
    ]
    integration = app / "custom_components/maestro_mcz_plus"
    sources.extend(integration.glob("*.py"))
    sources.append(integration / "translations/es.json")
    return any(source.stat().st_mtime_ns > compiled_at for source in sources)


if __name__ == "__main__":
    main()
