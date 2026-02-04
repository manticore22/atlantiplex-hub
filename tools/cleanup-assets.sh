#!/usr/bin/env bash
set -euo pipefail

# Non-destructive, safe cleanup scaffold for assets
# Keeps the 3 most recently modified files in branding/assets,
# and deletes older ones only if they are older than 30 days.

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
ASSETS_DIR="$ROOT_DIR/branding/assets"
KEEP_N=${KEEP_N:-3}
DRY_RUN=true

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run|-n) DRY_RUN=true; shift ;;
    --no-dry-run|-D) DRY_RUN=false; shift ;;
    --keep|-k) KEEP_N="$2"; shift 2 ;;
    --help|-h) echo "Usage: $0 [--dry-run] [--no-dry-run] [--keep N]"; exit 0 ;;
    *) break ;;
  esac
done

if [[ ! -d "$ASSETS_DIR" ]]; then
  echo "No assets directory found at $ASSETS_DIR" >&2
  exit 0
fi

declare -a files
while IFS= read -r line; do
  files+=("$line")
done < <(find "$ASSETS_DIR" -type f -printf "%T@ %p\n" | sort -nr | awk '{print $2}')

if (( ${#files[@]} <= KEEP_N )); then
  echo "Nothing to prune; only ${#files[@]} asset(s) found, keep $KEEP_N by default."
  exit 0
fi

to_delete=()
for ((i=KEEP_N; i<${#files[@]}; i++)); do
  to_delete+=("${files[i]}")
done

echo "Found ${#files[@]} assets; will prune to ${KEEP_N} latest."

now=$(date +%s)
for f in "${to_delete[@]}"; do
  # get mtime in seconds
  mtime=$(stat -c %Y "$f" 2>/dev/null || stat -f %m "$f" 2>/dev/null || echo 0)
  (( mtime )) || continue
  age=$(( now - mtime ))
  # 30 days = 2592000 seconds
  if (( age >= 2592000 )); then
    if $DRY_RUN; then
      echo "[dry-run] would delete: $f (age: ${age}s)"
    else
      rm -f "$f" && echo "Deleted: $f"
    fi
  else
    echo "Skipping recent asset: $f (age: ${age}s)"
  fi
done
