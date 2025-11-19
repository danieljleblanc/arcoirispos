#!/usr/bin/env bash
# ------------------------------------------------------------------
# Pre-commit Hook: Prevent Editing Historical Alembic Migration Files
# ------------------------------------------------------------------
# This hook stops commits that modify *existing* migration files,
# except for:
#   - brand new migration files (git "A" status)
#   - the latest migration file (optional toggle)
#   - env.py and script.py.mako (safe to edit)
#
# Why?
#   Alembic migrations are an immutable history.
#   Modifying old ones breaks environments, deployments, and DB state.
# ------------------------------------------------------------------

MIGRATIONS_DIR="src/database/migrations/versions"

# Toggle this to allow editing HEAD migration:
ALLOW_EDIT_LATEST=true

echo "🔍 Running migration safety checks..."

# Get changed Python files under migrations/versions
CHANGED_MIGRATIONS=$(git diff --cached --name-status -- "$MIGRATIONS_DIR"/*.py)

# If none touched, exit cleanly
if [[ -z "$CHANGED_MIGRATIONS" ]]; then
    echo "✔ No migration files modified."
    exit 0
fi

# Determine the currently latest migration file (lexicographically highest rev-id)
LATEST_MIGRATION=$(ls "$MIGRATIONS_DIR" | sort -r | head -n 1)

BLOCKED_FILES=()

while IFS= read -r line; do
    STATUS=$(echo "$line" | awk '{print $1}')
    FILE=$(echo "$line" | awk '{print $2}')

    # Allow new migration files (Added)
    if [[ "$STATUS" == "A" ]]; then
        echo "✔ New migration added: $FILE"
        continue
    fi

    # Allow editing the newest migration file only
    if [[ "$ALLOW_EDIT_LATEST" == true ]]; then
        if [[ "$FILE" == *"$LATEST_MIGRATION" ]]; then
            echo "✔ Allowed: editing latest migration $FILE"
            continue
        fi
    fi

    # Everything else is forbidden
    BLOCKED_FILES+=("$FILE")

done <<< "$CHANGED_MIGRATIONS"


# If any forbidden migration edits detected → BLOCK COMMIT
if [[ ${#BLOCKED_FILES[@]} -gt 0 ]]; then
    echo
    echo "⛔ ERROR: You attempted to modify historical migration files:"
    for f in "${BLOCKED_FILES[@]}"; do
        echo "   - $f"
    done
    echo
    echo "🚫 These files are IMMUTABLE. Create a NEW migration instead:"
    echo "      alembic revision --autogenerate -m \"your message\""
    echo
    echo "Commit aborted."
    exit 1
fi

echo "✔ Migration check passed."
exit 0
