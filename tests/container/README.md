# Phyllome OS Recipe Generator Test Container

Minimal containerized testing environment for kickstart recipe validation.

## Build

```bash
cd /home/lukas/Code/virt/phyllomeos

podman build -t phyllo/test-runner tests/container/
# or: docker build -t phyllo/test-runner tests/container/
```

## Run Tests

```bash
# Run all tests (unit + integration + golden masters)
podman run --rm -v .:/phyllomeos:ro phyllo/test-runner

# Run specific test file
podman run --rm -v .:/phyllomeos:ro phyllo/test-runner pytest tests/integration/test_ingredients.py -v

# Interactive mode for debugging
podman run -it --rm -v .:/phyllomeos phyllo/test-runner bash
```

## Test Types

### Unit Tests
- **Location:** `tests/test_recipe_generator.py`
- **Count:** 36 tests
- **Description:** Tests for recipe generator functionality (template loading, validation, version extraction)

### Fragment Validation Tests
- **Location:** `tests/integration/test_ingredients.py`
- **Count:** ~15 tests
- **Description:** Validates all 54 ingredients with pykickstart, checks section structure

### Recipe Composition Tests
- **Location:** `tests/integration/test_recipe_composition.py`
- **Count:** ~10 tests
- **Description:** Tests recipe generation, validates all 16 manifest variants

### Semantic Validation Tests
- **Location:** `tests/integration/test_semantic_validation.py`
- **Count:** ~10 tests
- **Description:** pykickstart semantic validation, deprecated command detection

### Golden Master Tests
- **Location:** `tests/integration/test_golden_masters.py`
- **Count:** ~5 tests
- **Description:** Regression tests comparing generated recipes against expected outputs

## Test Structure

```
tests/
├── test_recipe_generator.py          # Unit tests (36 tests)
├── integration/
│   ├── test_ingredients.py             # Fragment validation (~15 tests)
│   ├── test_recipe_composition.py    # Recipe generation (~10 tests)
│   ├── test_semantic_validation.py   # pykickstart semantic (~10 tests)
│   ├── test_golden_masters.py        # Regression tests (~5 tests)
│   └── conftest.py                   # Pytest fixtures
├── fixtures/
│   ├── expected_recipes/             # 5 golden master files
│   └── sample_ingredients/             # Test fragment samples
└── container/
    ├── Containerfile                 # Test runner container definition
    ├── run-tests.sh                  # Test entrypoint script
    └── README.md                     # This file
```

## Container Contents

The test runner container includes:

- **OS:** Fedora 43
- **Python packages:**
  - `pykickstart` - Kickstart parsing and validation
  - `pytest` - Test framework
  - `PyYAML` - YAML parsing
- **System tools:**
  - `make` - Build automation
  - `git` - Version control
  - `coreutils` - Basic utilities

## Adding New Tests

1. Add test file to `tests/integration/`
2. Follow naming convention: `test_*.py`
3. Use pytest fixtures from `conftest.py`
4. Run tests in container to verify

## Troubleshooting

### Container won't start
```bash
# Check if container builds
podman build tests/container/

# Run with verbose output
podman run --rm -v .:/phyllomeos:ro -e PYTEST_VERBOSITY=2 phyllo/test-runner
```

### Tests failing inside container
```bash
# Get interactive shell
podman run -it --rm -v .:/phyllomeos phyllo/test-runner bash

# Run tests manually
cd /phyllomeos
pytest tests/integration/test_ingredients.py -v
```

### Permission denied errors
```bash
# Run with security options (for rootless podman)
podman run --rm --security-opt label=disable -v .:/phyllomeos:ro phyllo/test-runner
```

## CI/CD Integration

This container will be used in Gitea Actions workflows for:
- Pull request validation
- Main branch testing
- Automated recipe generation checks

See `.gitea/workflows/` for workflow definitions.
