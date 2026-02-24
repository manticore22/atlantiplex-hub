#!/bin/bash
set -euo pipefail
echo "Packing Stage 2 bundle..."
ZIP_NAME="seraphonix-stage2-bundle.zip"
rm -f "$ZIP_NAME"
if command -v zip >/dev/null 2>&1; then
  zip -r "$ZIP_NAME" docker-compose.stage2.yml nginx-stage2.conf verilysovereign-backend verilysovereign Stage2Bundle -x \\*.git* >/dev/null
  echo "Created $ZIP_NAME (zip)"
else
  TAR_NAME="seraphonix-stage2-bundle.tar.gz"
  tar -czf "$TAR_NAME" docker-compose.stage2.yml nginx-stage2.conf verilysovereign-backend verilysovereign Stage2Bundle
  echo "Created $TAR_NAME (tar.gz)"
  ZIP_NAME="$TAR_NAME"
fi
