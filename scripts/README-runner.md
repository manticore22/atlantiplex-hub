Runnable scripts for branding asset hygiene

- Tools
  - tools/cleanup-assets.sh
    * Purpose: prune branding/assets keeping the top N newest files per directory
    * Usage:
      - Dry run: bash tools/cleanup-assets.sh -n
      - Real run: bash tools/cleanup-assets.sh -D
      - Keep per directory: bash tools/cleanup-assets.sh --keep-per-dir 1
    * Notes:
      - Default KEEP_PER_DIR is 1; you can override with --keep-per-dir
      - Ensure branding/assets exists before running

- Branding assets folder
  - branding/assets

Quick tip: mark executable if not already
  - chmod +x tools/cleanup-assets.sh
