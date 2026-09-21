#!/usr/bin/env bash
# Genera la version web con pygbag 0.9.3 usando el template local (index.tmpl)
# y copia los binarios a build/web y a la raiz del repo (GitHub Pages).
#
# Uso:  bash build_web.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
STAGE="${TEMP:-/tmp}/pygbag_build/21_septiembre_game"
PYGBAG="$ROOT/venv312/Scripts/python.exe"

echo "==> Preparando staging en $STAGE"
rm -rf "$STAGE"
mkdir -p "$STAGE"
cp -r "$ROOT/main.py" "$ROOT/src" "$ROOT/assets" "$ROOT/index.tmpl" "$ROOT/pygbag.ini" "$ROOT/favicon.png" "$STAGE/"

echo "==> pygbag build (template index.tmpl)"
cd "$STAGE"
"$PYGBAG" -m pygbag --disable-sound-format-error --template index.tmpl --build .

echo "==> Copiando resultados a build/web y raiz del repo"
cp -f "$STAGE/build/web/index.html" "$STAGE/build/web/21_septiembre_game.apk" \
      "$STAGE/build/web/21_septiembre_game.tar.gz" "$STAGE/build/web/favicon.png" \
      "$ROOT/build/web/"
cp -f "$ROOT/build/web/index.html" "$ROOT/build/web/21_septiembre_game.apk" \
      "$ROOT/build/web/21_septiembre_game.tar.gz" "$ROOT/build/web/favicon.png" \
      "$ROOT/"

echo "==> Listo. Sube estos archivos a \"/\" en GitHub Pages:"
ls -la "$ROOT/index.html" "$ROOT/21_septiembre_game.apk" "$ROOT/21_septiembre_game.tar.gz" "$ROOT/favicon.png"

echo
echo "Preview local (opcional):"
echo "  cd build/web && \"$PYGBAG\" -m pygbag --disable-sound-format-error --template \"$ROOT/index.tmpl\" --build . && \"$PYGBAG\" -m pygbag ."