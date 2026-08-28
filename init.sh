#!/bin/bash
# init.sh - cutz2 verification entrypoint
# Runs the four checks the harness requires before any feature is marked done.
# Exits non-zero on the first failure (set -e + explicit checks).

set -e

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$REPO_ROOT"

# cutz2/bin/python is the venv interpreter; allow override via $PYTHON.
if [ -x "$REPO_ROOT/cutz2/bin/python" ]; then
  PYTHON="${PYTHON:-$REPO_ROOT/cutz2/bin/python}"
else
  PYTHON="${PYTHON:-python}"
fi
MANAGE="$PYTHON cuts/manage.py"

echo "=== cutz2 harness initialization ==="
echo "Using Python: $PYTHON"

# 1. Postgres reachable (infrastructure prerequisite)
echo "[1/4] Infrastructure check: Postgres at localhost:5432 ..."
if ! pg_isready -h localhost -p 5432 >/dev/null 2>&1; then
  echo "FAIL: Postgres not reachable at localhost:5432." >&2
  echo "      Start it (brew services start postgresql, docker compose up, etc.) and retry." >&2
  exit 1
fi
echo "      OK"

# 2. Django system check (static configuration check)
echo "[2/4] Static check: 'manage.py check' ..."
if ! $MANAGE check >/dev/null; then
  echo "FAIL: 'manage.py check' reported errors." >&2
  $MANAGE check >&2
  exit 1
fi
echo "      OK"

# 3. Migration drift check (build/schema check)
echo "[3/4] Build check: 'manage.py migrate --check' ..."
if ! $MANAGE migrate --check >/dev/null 2>&1; then
  echo "FAIL: unapplied migrations exist." >&2
  echo "      Run: python cuts/manage.py makemigrations --dry-run --check" >&2
  echo "      to see what's missing, then ask before generating." >&2
  $MANAGE migrate --check >&2 || true
  exit 1
fi
echo "      OK"

# 4. Tests (test suite execution)
echo "[4/4] Test check: running tests ..."
if [ -f pytest.ini ] || [ -f pyproject.toml ] && grep -q "pytest" pyproject.toml 2>/dev/null; then
  if ! $PYTHON -m pytest; then
    echo "FAIL: pytest exited non-zero." >&2
    exit 1
  fi
else
  if ! $MANAGE test; then
    echo "FAIL: 'manage.py test' exited non-zero." >&2
    exit 1
  fi
fi
echo "      OK"

echo ""
echo "=== Verification complete: all four checks passed ==="
echo "Next: read feature_list.json, pick the one not-started feature, work only on that."
