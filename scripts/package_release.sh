#!/usr/bin/env bash
set -euo pipefail

# Package a copy of the full working product for distribution.
# - Creates an archive in dist/ with a version label.
# - Excludes packaging tooling to keep the product clean for end users.

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DIST_DIR="$ROOT_DIR/dist"
ROOT_NAME="full-work-product-v"

VERSION="0.1.0"
LABEL=""
TYPE="zip" # or tar.gz
while [[ $# -gt 0 ]]; do
  case "$1" in
    -v|--version)
      VERSION="$2"; shift 2 ;;
    -l|--label)
      LABEL="$2"; shift 2 ;;
    -t|--type)
      TYPE="$2"; shift 2 ;;
    -h|--help)
      echo "Usage: $0 -v <version> [-l <label>] [-t zip|tar.gz]"; exit 0 ;;
    *)
      shift ;;
  esac
done

ARCHIVE_BASENAME="${ROOT_NAME}${VERSION}"
if [[ -n "$LABEL" ]]; then
  ARCHIVE_BASENAME+="-${LABEL}"
fi

mkdir -p "$DIST_DIR"

ARCHIVE_PATH_ZIP="$DIST_DIR/${ARCHIVE_BASENAME}.zip"
ARCHIVE_PATH_TAR="$DIST_DIR/${ARCHIVE_BASENAME}.tar.gz"

echo "Packaging version ${VERSION}${LABEL:+ (label: $LABEL)} as ${TYPE}..."

if [[ "$TYPE" == "zip" ]]; then
  if command -v zip >/dev/null 2>&1; then
    (cd "$ROOT_DIR" && zip -r "$ARCHIVE_PATH_ZIP" . \
      -x "dist/*" "scripts/*" "tools/*" "RUN_ME.txt" "scripts/README-runner.md" ".git/*" )
    echo "Created: $ARCHIVE_PATH_ZIP"
  else
    echo "Warning: zip not found, falling back to tar.gz" >&2
    TYPE="tar.gz"
  fi
fi

if [[ "$TYPE" == "tar.gz" ]]; then
  (cd "$ROOT_DIR" && tar czf "$ARCHIVE_PATH_TAR" \
    --exclude dist --exclude scripts --exclude tools --exclude RUN_ME.txt --exclude 'scripts/README-runner.md' --exclude .git .)
  echo "Created: $ARCHIVE_PATH_TAR"
fi

MANIFEST="$DIST_DIR/${ARCHIVE_BASENAME}.txt"
cat > "$MANIFEST" <<EOF
Product Release Manifest
Version: ${VERSION}
Label: ${LABEL:-none}
Date: $(date -u +"%Y-%m-%d %H:%M UTC")
Source: $ROOT_DIR
Archive: ${ARCHIVE_PATH_ZIP} or ${ARCHIVE_PATH_TAR}
EOF

echo "Manifest created: $MANIFEST"
