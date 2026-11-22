#!/bin/sh
set -eu
cd "$(dirname "$0")"

if [ -z "${PYTHON:-}" ]; then
    PYTHON=python3
    if [ -x .venv/bin/python ]; then
        PYTHON=.venv/bin/python
    fi
fi

mkdir -p dist
staging=$(mktemp -d dist/.build.XXXXXX)
trap 'rm -rf "$staging"' EXIT

"$PYTHON" -m compileall -q custom_components preview
version=$("$PYTHON" -c 'import json; from pathlib import Path; print(json.loads(Path("custom_components/maestro_mcz_plus/manifest.json").read_text())["version"])')
archive="maestro_mcz_plus-$version.zip"
zip -qr "$staging/$archive" hacs.json README.md MECHANICS.md LICENSE custom_components/maestro_mcz_plus \
    -x '*/__pycache__/*' '*.py[co]' '*/.DS_Store'
unzip -tq "$staging/$archive"

bundle="$staging/Maestro MCZ Plus Preview.app"
mkdir -p "$bundle/Contents/MacOS" "$bundle/Contents/Resources"
"$PYTHON" -m preview.sample > "$bundle/Contents/Resources/sample.json"
cp preview/Info.plist "$bundle/Contents/Info.plist"
swiftc -parse-as-library -module-cache-path "$staging/swift-cache" \
    preview/MaestroPreview.swift -o "$bundle/Contents/MacOS/MaestroPreview"

destination="dist/Maestro MCZ Plus Preview.app"
rm -rf "$destination"
mv "$bundle" "$destination"
mv "$staging/$archive" "dist/$archive"
printf 'Integration packaged in dist/%s\n' "$archive"
printf 'Preview built at %s\n' "$destination"
