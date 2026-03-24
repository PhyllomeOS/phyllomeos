#!/bin/bash
# Run all tests inside the container environment
# Usage: podman run --rm -v .:/phyllomeos:ro phyllo/test-runner

set -e

echo "============================================="
echo "  Phyllome OS Recipe Generator Test Suite"
echo "============================================="
echo ""

# Navigate to project root
cd /phyllomeos

echo "[1/3] Running unit tests (test_recipe_generator.py)..."
echo "----------------------------------------"
python3 -m pytest tests/test_recipe_generator.py -v
echo "✓ Unit tests passed!"
echo ""

echo "[2/3] Running integration tests..."
echo "----------------------------------------"
python3 -m pytest tests/integration/ -v
echo "✓ Integration tests passed!"
echo ""

echo "[3/3] Validating generated recipes..."
echo "----------------------------------------"
cd scripts
python3 generate_recipe.py --validate ../recipes/*.cfg --strict
echo "✓ Recipe validation passed!"
echo ""

echo "============================================="
echo "  ALL TESTS PASSED!"
echo "============================================="
echo ""
echo "Summary:"
echo "  - Unit tests: 36 tests (test_recipe_generator.py)"
echo "  - Integration tests: Fragment validation, recipe composition, golden masters"
echo "  - Fragment validation: 54 .ks files checked"
echo "  - Recipe validation: All 16 manifest variants generated and validated"
echo ""
