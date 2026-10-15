#!/usr/bin/env bash
# build_and_sign.sh — Build, post-process, sign, and install LV-Gen.app
#
# Usage (from repo root, venv active):
#   bash scripts/build_and_sign.sh
#
# Requires:
#   - venv active (source venv/bin/activate)
#   - Developer ID Application certificate in Keychain
#   - SIGN_CERT env var set to the SHA-1 hash of that certificate.
#     List the candidates:
#       security find-identity -v -p codesigning | grep 'Developer ID Application'
#     then pin the one you want, e.g.:
#       export SIGN_CERT=840DD6427C5D50491AC2244E0B79DA67A0264163
#     Pin the hash rather than deriving it. Across a certificate rollover the
#     Keychain holds both the old and the new cert under the same common name,
#     so anything that greps by name is ambiguous.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CERT="${SIGN_CERT:?Error: SIGN_CERT env var not set. Export your Developer ID certificate hash before running.}"

# A rollover leaves two identities sharing one common name, so the hash has to
# name exactly one of them -- codesign gives a cryptic error otherwise.
if ! [[ "$CERT" =~ ^[0-9A-Fa-f]{40}$ ]]; then
  echo "Error: SIGN_CERT must be a single 40-character SHA-1 hash, got: $CERT" >&2
  echo "Candidates:" >&2
  security find-identity -v -p codesigning | grep 'Developer ID Application' >&2
  exit 1
fi
if ! security find-identity -v -p codesigning | grep -qi "$CERT"; then
  echo "Error: no codesigning identity in the Keychain matches $CERT" >&2
  exit 1
fi

ENT="$REPO_ROOT/entitlements.plist"
DIST="$REPO_ROOT/dist/LV-Gen.app"
INSTALL="/Applications/LV-Gen.app"

echo "=== 1. Build py2app bundle ==="
cd "$REPO_ROOT"
python setup_py2app.py py2app

echo "=== 2. Post-process bundle ==="

# Remove dist-info dirs (confuse codesign)
find "$DIST" -name "*.dist-info" -type d -exec rm -rf {} + 2>/dev/null || true

# Remove Tcl/Tk data (app doesn't use tkinter)
for d in _tcl_data _tk_data tcl8; do
  rm -rf "$DIST/Contents/Frameworks/$d" "$DIST/Contents/Resources/$d" 2>/dev/null || true
done

# Remove hidden .dylibs from Frameworks (codesign rejects them)
find "$DIST/Contents/Frameworks" -name ".dylibs" -type d -exec rm -rf {} + 2>/dev/null || true

# Rename PIL's .dylibs → _dylibs (hidden dirs excluded from codesign seal)
PYVER=$(ls "$DIST/Contents/Resources/lib/" | head -1)  # e.g. python3.13
PILDIR="$DIST/Contents/Resources/lib/$PYVER/PIL"
if [ -d "$PILDIR/.dylibs" ]; then
  mv "$PILDIR/.dylibs" "$PILDIR/_dylibs"
  echo "  Renamed PIL/.dylibs -> PIL/_dylibs"

  # Update @loader_path/.dylibs/ references in .so files to @loader_path/_dylibs/
  for f in "$PILDIR"/*.so; do
    for lib in "$PILDIR/_dylibs"/*.dylib; do
      libname=$(basename "$lib")
      install_name_tool -change \
        "@loader_path/.dylibs/$libname" \
        "@loader_path/_dylibs/$libname" \
        "$f" 2>/dev/null || true
    done
  done
  echo "  Updated .so @loader_path references"
fi

# Symlink base_library.zip: move to Resources, symlink from Frameworks
if [ -f "$DIST/Contents/Frameworks/base_library.zip" ]; then
  mv "$DIST/Contents/Frameworks/base_library.zip" "$DIST/Contents/Resources/base_library.zip"
  ln -s "../Resources/base_library.zip" "$DIST/Contents/Frameworks/base_library.zip"
  echo "  Symlinked base_library.zip"
fi

echo "=== 3. Sign all binaries ==="

# Sign one file, aborting the build if codesign rejects it. A silent failure
# here produces a bundle that looks signed but fails notarization later.
sign() {
  codesign --force --sign "$CERT" --options runtime --entitlements "$ENT" "$1"
}

# -print0 / read -d '' so paths with spaces survive, and process substitution
# so the loop runs in this shell and `set -e` can actually abort the build.

# Sign dylibs (including _dylibs)
while IFS= read -r -d '' f; do
  sign "$f"
done < <(find "$DIST" -name "*.dylib" -print0)
echo "  Dylibs signed"

# Sign .so extension modules
while IFS= read -r -d '' f; do
  sign "$f"
done < <(find "$DIST" -name "*.so" -print0)
echo "  .so files signed"

# Sign extension-less Mach-O files in Frameworks (Qt dylibs without .dylib extension)
while IFS= read -r -d '' f; do
  if file "$f" 2>/dev/null | grep -q "Mach-O"; then
    sign "$f"
  fi
done < <(find "$DIST/Contents/Frameworks" -maxdepth 1 -type f -print0)
echo "  Extension-less Mach-O files signed"

echo "=== 4. Sign bundle ==="
sign "$DIST"
echo "  Bundle signed"

# Verify
codesign -dv "$DIST" 2>&1 | grep -E "TeamIdentifier|Sealed Resources"

echo "=== 5. Install to /Applications ==="
rm -rf "$INSTALL"
cp -r "$DIST" "$INSTALL"
echo "  Installed: $INSTALL"

echo ""
echo "Done. Launch /Applications/LV-Gen.app from Finder to test."
