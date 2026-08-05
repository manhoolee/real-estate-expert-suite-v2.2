#!/bin/sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
PYTHON=${PYTHON:-python3}

$PYTHON -m py_compile "$ROOT"/*/scripts/*.py
if $PYTHON "$ROOT/real-estate-research/scripts/scope_check.py" "$ROOT/tests/fixtures/machang-scope-invalid.json" >/dev/null 2>&1; then
  echo "expected invalid scope fixture to fail" >&2
  exit 1
fi
$PYTHON "$ROOT/real-estate-research/scripts/scope_check.py" "$ROOT/tests/fixtures/machang-scope-valid.json" >/dev/null

TMP_DIR=$(mktemp -d)
trap 'rm -rf "$TMP_DIR"' EXIT
$PYTHON "$ROOT/comprehensive-real-estate-expert/scripts/init_case.py" "$TMP_DIR/case" --project "Smoke Test" --scope-id "smoke-phase-1" >/dev/null
$PYTHON "$ROOT/comprehensive-real-estate-expert/scripts/validate_case.py" "$TMP_DIR/case" >/dev/null
$PYTHON "$ROOT/real-estate-product-strategy/scripts/product_model.py" "$ROOT/tests/fixtures/machang-product-hypothesis.json" --out-json "$TMP_DIR/model.json" --out-csv "$TMP_DIR/model.csv"
printf '# Test\n\n## Table\n\n| A | B |\n|---|---|\n| 1 | FACT-A |\n' > "$TMP_DIR/test.md"
$PYTHON "$ROOT/comprehensive-real-estate-expert/scripts/render_report.py" "$TMP_DIR/test.md" "$TMP_DIR/test.html" >/dev/null
test -s "$TMP_DIR/test.html"
for skill in real-estate-report-editorial real-estate-report-design real-estate-delivery-qa; do
  test -s "$ROOT/$skill/SKILL.md"
  test -s "$ROOT/$skill/_meta.json"
  test -s "$ROOT/$skill/agents/openai.yaml"
done
test "$(python3 -c 'import json; print(json.load(open("'"$ROOT"'/manifest.json"))["version"])')" = "2.2.0"
echo "v2.2 smoke tests passed"
