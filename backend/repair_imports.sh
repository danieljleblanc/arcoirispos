#!/bin/bash

echo "=== FIXING ALL BAD IMPORT PATHS ==="

find src/app -type f -name "*.py" -print0 | xargs -0 sed -i '' \
  -e 's/from src.core/from src.app.core/g' \
  -e 's/from src.pos/from src.app.pos/g' \
  -e 's/from src.inventory/from src.app.inventory/g' \
  -e 's/from src.org/from src.app.org/g' \
  -e 's/from src.auth/from src.app.auth/g' \
  -e 's/from src\.app\.core\.core/from src.app.core/g'

echo "=== IMPORT REPAIR COMPLETE ==="
