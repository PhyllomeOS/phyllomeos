# Phyllome OS Development Guide

This guide covers development workflows for contributors to Phyllome OS.

## Table of Contents
- [Architecture Overview](#architecture-overview)
- [Development Environment Setup](#development-environment-setup)
- [Ingredient Development](#ingredient-development)
- [Recipe Generation](#recipe-generation)
- [Testing](#testing)
- [CI/CD](#cicd)
- [Common Workflows](#common-workflows)
- [Migration Guide: Ingredient-Based Architecture](#migration-guide-ingredient-based-architecture)

---

## Architecture Overview

Phyllome OS uses a **ingredient-driven** kickstart generation system:

```
ingredients/ (54 .ks files)
    ↓ (modular snippets)
recipe-generator/generate_recipe.py
    ↓ (YAML templates + manifest)
recipes/ (16 auto-generated .cfg)
    ↓ (ksflatten)
dishes/ (28 flattened .cfg)
    ↓ (virt-install)
VMs and ISO images
```

### Directory Structure

| Path | Purpose | Contents |
|------|---------|----------|
| `ingredients/` | Modular kickstart snippets | 54 `.ks` files |
| `recipes/` | Generated recipes | Manifest-driven compositions |
| `dishes/` | Flattened kickstarts | Ready-to-deploy artifacts |
| `legacy/` | Legacy building blocks | 35 `.cfg` files (legacy) |
| `recipe-generator/` | Recipe generation | `generate_recipe.py`, YAML configs, Makefile |
| `deploy/` | Deployment scripts | Bash automation tools |
| `bin/` | Executables | Wrapper scripts (e.g., `generate-recipe`) |

### Data Flow

1. **Ingredients** (`ingredients/**/*.ks`) - Small, reusable kickstart snippets
2. **Templates** (`recipe-generator/recipe_templates.yaml`) - Define recipe structures
3. **Manifest** (`recipe-generator/recipes_manifest.yaml`) - Specify variants (version, desktop, storage, etc.)
4. **Generator** (`recipe-generator/generate_recipe.py`) - Composes ingredients via `%ksappend` directives
5. **Recipes** (`recipes/*.cfg`) - Generated kickstart files with ingredient references
6. **Flattening** (`ksflatten`) - Resolves `%ksappend` into single dish file
7. **Deployment** (`virt-install`) - Creates VMs from dish files

---

## Development Environment Setup

### Prerequisites

**System dependencies:**
```bash
# Fedora/RHEL-based systems
sudo dnf install qemu libvirt virt-install pykickstart

# Start libvirt
sudo systemctl start libvirtd
sudo systemctl enable libvirtd
```

**Python dependencies:**
```bash
cd scripts
pip install -r requirements.txt
# Required: PyYAML>=6.0, pytest>=7.0
# Optional: pykickstart (for validation)
```

### Verify Setup

```bash
# Generate all recipes from manifest
cd scripts
make generate-recipes

# Run all tests
make test

# Check recipe validation
make validate-recipes
```

---

## Fragment Development

Fragments are modular kickstart snippets stored in `ingredients/`. Each `.ks` file contains a single feature section.

### Creating a New Fragment

**Step 1: Choose location**
- `ingredients/shared/core/` - Base settings (security, services, networking)
- `ingredients/shared/storage/` - Partition layouts
- `ingredients/shared/packages/` - Package groups
- `ingredients/shared/desktop/` - Desktop environment configs
- `ingredients/shared/hypervisor/` - Virtualization hardware configs
- `ingredients/shared/live/` - Live system components
- `ingredients/shared/initial-setup/` - First-boot configuration
- `ingredients/platform/generic-43/` or `generic-rawhide/` - Version-specific

**Step 2: Create the fragment file**

```bash
# Example: Add Luanti game engine
cat > ingredients/shared/packages/luanti.ks << 'EOF'
%packages
luanti
%end
EOF
```

**Step 3: Validate with pykickstart**

```bash
python3 -c "
from pykickstart.parser import KickstartParser
from pykickstart.version import makeVersion, DEVEL

parser = KickstartParser(makeVersion(DEVEL))
try:
    with open('ingredients/shared/packages/luanti.ks') as f:
        parser.readKickstart(f.read())
    print('✓ Validation passed')
except Exception as e:
    print(f'✗ Validation failed: {e}')
"
```

### Fragment Naming Conventions

- **Pattern:** `<feature>/<subfeature>.ks`
- **Examples:**
  - `ingredients/shared/core/security/enabled.ks`
  - `ingredients/shared/desktop/gnome/packages.ks`
  - `ingredients/platform/generic-43/repo/fedora-mirrors.ks`

### Common Fragment Types

**Packages:**
```bash
%packages
@base-graphical
package-name
%end
```

**Storage:**
```bash
part / --fstype="ext4" --grow
part /boot/efi --fstype="efi" --size=512
```

**Services:**
```bash
%services
--enabled=sshd,chronyd
EOF
```

### Fragment Validation Script

Create `deploy/validate-fragment.sh`:

```bash
#!/bin/bash
set -e

fragment="$1"

if [ -z "$fragment" ]; then
    echo "Usage: $0 <fragment-path>"
    exit 1
fi

python3 -c "
from pykickstart.parser import KickstartParser
from pykickstart.version import makeVersion, DEVEL

parser = KickstartParser(makeVersion(DEVEL))
try:
    with open('$fragment') as f:
        parser.readKickstart(f.read())
    print('✓ Valid: $fragment')
except Exception as e:
    print(f'✗ Invalid: $fragment - {e}')
    exit(1)
"
```

---

## Recipe Generation

Recipes are generated from templates and the manifest file. This section covers modifying existing recipes and creating new ones.

### Manifest Editing

**File:** `recipe-generator/recipes_manifest.yaml`

The manifest defines all recipe variants using modifiers from templates.

**Structure:**
```yaml
recipes:
  - name: virtual-desktop          # Template name
    variants:                      # Modifier combinations
      - version: 43
        desktop: gnome
        storage: standard
        security: secure
        extras: true
      - version: rawhide
        desktop: labwc
        storage: encrypted
        security: devel
```

**Adding a new variant:**
```yaml
  - name: virtual-server
    variants:
      - version: 43
        security: secure
        extras: true
        post: true
      # Add new variant below
      - version: 43
        security: secure
        extras: false
        post: false
```

**Valid modifiers** (per template):
- `version`: `43` or `rawhide`
- `desktop`: `gnome` or `labwc` (desktop templates)
- `storage`: `standard` or `encrypted`
- `security`: `secure` or `devel`
- `cpu`: `amdcpu`, `intelcpu` (hypervisor)
- `gpu`: `intelgpu` (hypervisor)
- `extras`: `true` or `false`
- `post`: `true` or `false`

### Template Editing

**File:** `recipe-generator/recipe_templates.yaml`

Templates define the structure and fragment composition for each recipe type.

**Structure:**
```yaml
templates:
  virtual-desktop:
    description: "A recipe for a virtual desktop"
    base: core
    required:                      # Always included ingredients
      - core: ingredients/shared/core/base.ks
      - storage: ingredients/shared/storage/standard.ks
    optional:                      # Conditional ingredients
      security:
        secure: ingredients/shared/core/security/enabled.ks
        devel: ingredients/shared/core/security/disabled.ks
    modifiers:                     # Storage/bootloader alternatives
      storage:
        standard: ingredients/shared/storage/standard.ks
        encrypted: ingredients/shared/storage/encrypted.ks
```

**Adding a new required fragment:**
```yaml
    required:
      - core: ingredients/shared/core/base.ks
      - storage: ingredients/shared/storage/standard.ks
      # New fragment
      - packages: ingredients/shared/packages/hand-picked.ks
```

**Adding an optional modifier:**
```yaml
    optional:
      security:
        secure: ingredients/shared/core/security/enabled.ks
        devel: ingredients/shared/core/security/disabled.ks
      # New optional - post-install scripts
      post: ingredients/shared/section-data/post/base.ks
```

**Adding a modifier alternative:**
```yaml
    modifiers:
      storage:
        standard: ingredients/shared/storage/standard.ks
        encrypted: ingredients/shared/storage/encrypted.ks
        # New storage option
        btrfs: ingredients/shared/storage/btrfs.ks
```

### Generation Workflow

```bash
cd scripts

# Generate all recipes from manifest
make generate-recipes

# Validate generated recipes
make validate-recipes

# Validate with strict mode (checks fragment existence)
python3 generate_recipe.py --validate ../recipes/*.cfg --strict
```

**Output:**
```
Generating: virtual-desktop_43.cfg
Generating: virtual-desktop_rawhide_encrypted.cfg
Generating: virtual-server_43.cfg
...
✓ Generated 16 recipes
```

### Manual Recipe Creation

**Option 1: Copy existing recipe**

```bash
# Copy template
cp recipes/_list-of-ingredients.cfg recipes/my-custom.cfg

# Edit with your favorite editor
nano recipes/my-custom.cfg

# Add custom ingredient
echo "%include ../ingredients/extra-luanti.cfg" >> recipes/my-custom.cfg

# Flatten to dish
ksflatten -c recipes/my-custom.cfg -o dishes/my-custom.cfg
```

**Option 2: Create from scratch**

```bash
cat > recipes/my-distro.cfg << 'EOF'
# My custom Phyllome OS variant

# Installation method
%include ../ingredients/core.cfg

# Storage configuration
%include ../ingredients/core-storage.cfg

# Bootloader
%include ../ingredients/platform/generic-43/bootloader/grub.ks

# Network configuration
%include ../ingredients/shared/core/network.ks

# Desktop environment
%include ../ingredients/shared/desktop/gnome/packages.ks

# Additional packages
%packages
my-custom-package
@base-graphical
%end
EOF
```

### Flattening Recipes

Convert recipe (with `%ksappend`) to dish (flattened):

```bash
# Single recipe
ksflatten -c recipes/virtual-desktop_43.cfg -o dishes/virtual-desktop_43.cfg

# All recipes
cd recipes
for filename in *.cfg; do
    ksflatten -c "$filename" -o "../dishes/$filename"
done
```

---

## Testing

Phyllome OS uses a comprehensive test suite with 36+ tests covering unit, integration, and regression scenarios.

### Test Suite Structure

| Test File | Tests | Coverage |
|-----------|-------|----------|
| `tests/test_recipe_generator.py` | 36 | Unit tests for RecipeGenerator |
| `tests/integration/test_integration.py` | 5+ | End-to-end workflow tests |
| `tests/integration/test_ingredients.py` | ~15 | Fragment validation |
| `tests/integration/test_recipe_composition.py` | ~10 | Recipe generation |
| `tests/integration/test_semantic_validation.py` | ~10 | pykickstart validation |
| `tests/integration/test_golden_masters.py` | ~5 | Regression tests |

### Running Tests

```bash
cd scripts

# All tests (unit + integration)
make test

# Unit tests only
python3 -m pytest tests/test_recipe_generator.py -v

# Integration tests only
make test-integration

# Containerized tests
make test-container
# or: podman run --rm -v .:/phyllomeos:ro phyllo/test-runner
```

**Expected output:**
```
============================= test session starts =============================
collected 41 items

tests/test_recipe_generator.py .............                          [ 29%]
tests/integration/test_integration.py .....                                           [ 43%]
...

============================== 41 passed in 2.34s ==============================
```

### Fragment Validation Test

```bash
# Test all ingredients with pykickstart
for fragment in $(find ingredients -name "*.ks"); do
    python3 -c "
from pykickstart.parser import KickstartParser
from pykickstart.version import makeVersion, DEVEL
parser = KickstartParser(makeVersion(DEVEL))
parser.readKickstart(open('$fragment').read())
" && echo "✓ $fragment" || echo "✗ $fragment"
done
```

### Adding New Tests

**Unit test example:**

```python
# tests/test_recipe_generator.py

def test_generate_recipe_with_new_modifier():
    """Test recipe generation with custom modifier."""
    content = self.generator.generate_recipe(
        'virtual-desktop', '43',
        desktop='gnome',
        storage='standard',
        security='secure'
    )
    assert '# A recipe for a virtual desktop' in content
    assert '%ksappend ingredients/shared/desktop/gnome/packages.ks' in content
```

**Integration test example:**

```python
# tests/integration/test_recipe_composition.py

def test_manifest_generates_correct_count():
    """Test manifest generates expected number of recipes."""
    result = subprocess.run(
        ['python3', 'generate_recipe.py',
         '--manifest', 'recipes_manifest.yaml',
         '--output-dir', '../recipes/'],
        capture_output=True, text=True
    )
    assert result.returncode == 0
    recipe_count = len(list(Path('../recipes').glob('*.cfg')))
    assert recipe_count == 16
```

### Golden Master Tests

Golden masters (expected outputs) are stored in `tests/fixtures/expected_recipes/`:

```bash
# View expected output for virtual-desktop
cat tests/fixtures/expected_recipes/virtual-desktop_43.cfg
```

**To update golden masters** (after intentional changes):

```bash
# Generate and compare
python3 -m pytest tests/integration/test_golden_masters.py -v
```

---

## CI/CD

The project uses Gitea Actions for automated testing and building.

### Workflow Files

| File | Trigger | Purpose |
|------|---------|---------|
| `.gitea/workflows/validate-ingredients.yaml` | Push/PR ingredients | Validate all 54 .ks files |
| `.gitea/workflows/test-generation.yaml` | Push/PR scripts | Generate 16 recipes |
| `.gitea/workflows/validate-recipes.yaml` | Push PR main | Full validation suite |
| `.gitea/workflows/build-iso.yaml` | Push main, release | Build live ISO |

### Workflow: Validate Fragments

**File:** `.gitea/workflows/validate-ingredients.yaml`

**Triggers:**
- Push to any `ingredients/**/*.ks` file
- Pull request with fragment changes

**Steps:**
1. Checkout code
2. Install pykickstart
3. Validate each `.ks` file
4. Report errors

**Local equivalent:**
```bash
for fragment in $(find ingredients -name "*.ks"); do
    python3 -c "
from pykickstart.parser import KickstartParser
from pykickstart.version import makeVersion, DEVEL
parser = KickstartParser(makeVersion(DEVEL))
parser.readKickstart(open('$fragment').read())
" || exit 1
done
```

### Workflow: Test Generation

**File:** `.gitea/workflows/test-generation.yaml`

**Triggers:**
- Push to `recipe-generator/**/*.py` or `recipe-generator/**/*.yaml`
- Pull request with script changes

**Steps:**
1. Pull request with manifest changes

**Steps:**
1. Checkout code
2. Install dependencies (PyYAML, pykickstart)
3. Generate all recipes
4. Verify 16 recipes created
5. Upload as artifact

### Workflow: Build ISO

**File:** `.gitea/workflows/build-iso.yaml`

**Triggers:**
- Push to main branch
- Release published

**Steps:**
1. Generate and validate recipes
2. Initialize mock build environment
3. Install build tools (lorax-lmc-novirt, livemedia-creator)
4. Copy recipe to mock
5. Build ISO with livemedia-creator
6. Upload ISO as artifact

---

## Common Workflows

### Quick Reference

| Task | Command | File |
|------|---------|------|
| Generate all recipes | `cd scripts && make generate-recipes` | - |
| Validate all ingredients | `for f in $(find ingredients -name "*.ks"); do python3 -c "from pykickstart.parser import KickstartParser; from pykickstart.version import makeVersion, DEVEL; parser = KickstartParser(makeVersion(DEVEL)); parser.readKickstart(open('$f').read())" && echo "✓ $f"; done` | - |
| Run all tests | `cd scripts && make test` | - |
| Flatten recipe to dish | `ksflatten -c recipes/X.cfg -o dishes/X.cfg` | - |
| Deploy VM from dish | `./deploy-vm.sh` | `deploy.sh`, `deploy-distro.sh` |
| Build ISO | See `.gitea/workflows/build-iso.yaml` | - |
| Update golden masters | `python3 -m pytest tests/integration/test_golden_masters.py --snapshot-update` | - |

### Workflow: Add New Package

**Example: Add Luanti game engine**

```bash
# Step 1: Create fragment
cat > ingredients/shared/packages/luanti.ks << 'EOF'
%packages
luanti
%end
EOF

# Step 2: Add to recipe template
# Edit recipe-generator/recipe_templates.yaml
# Add to 'required' section:
#   - luanti: ingredients/shared/packages/luanti.ks

# Step 3: Regenerate recipes
cd recipe-generator
make generate-recipes

# Step 4: Validate
make validate-recipes

# Step 5: Flatten and test
ksflatten -c ../recipes/virtual-desktop_43.cfg -o ../dishes/virtual-desktop_43.cfg
```

### Workflow: Add New Desktop Environment

**Example: Add KDE Plasma**

```bash
# Step 1: Create desktop fragment
cat > ingredients/shared/desktop/kde/packages.ks << 'EOF'
%packages
@kde-desktop
plasma-workspace
EOF

# Step 2: Add to template
# Edit recipe-generator/recipe_templates.yaml
# Add to optional/desktop section:
#   kde: ingredients/shared/desktop/kde/packages.ks

# Step 3: Add variant to manifest
# Edit recipe-generator/recipes_manifest.yaml
# Add variant:
#   - version: 43
#     desktop: kde
#     storage: standard
#     security: secure

# Step 4: Generate and test
make generate-recipes
make test
```

### Workflow: Create New Recipe Type

**Example: Create minimal-server recipe**

```bash
# Step 1: Add template to recipe_templates.yaml
cat >> recipe-generator/recipe_templates.yaml << 'EOF'

  minimal-server:
    description: "A minimal server recipe"
    base: core
    required:
      - core: ingredients/shared/core/base.ks
      - storage: ingredients/shared/storage/standard.ks
      - bootloader: ingredients/platform/generic-43/bootloader/grub.ks
      - packages: ingredients/shared/packages/core-group.ks
      - fedora-remix: ingredients/shared/packages/fedora-remix.ks
    optional:
      security:
        secure: ingredients/shared/core/security/enabled.ks
        devel: ingredients/shared/core/security/disabled.ks
      version:
        "43": ingredients/platform/generic-43/repo/fedora-mirrors.ks
        "rawhide": ingredients/platform/generic-rawhide/repo/rawhide-mirrors.ks
EOF

# Step 2: Add variant to recipes_manifest.yaml
cat >> recipe-generator/recipes_manifest.yaml << 'EOF'

  - name: minimal-server
    variants:
      - version: 43
        security: secure
EOF

# Step 3: Generate and validate
make generate-recipes
make validate-recipes
```

---

## Migration Guide: Fragment-Based Architecture

Phyllome OS migrated from a monolithic ingredient-based system to a modular fragment-based architecture (Phase 2).

### Before: Ingredient-Based

**File:** `ingredients/extra-luanti.cfg`
```bash
%packages
luanti
%end
```

**Recipe:** `recipes/virtual-desktop-luanti.cfg`
```bash
%include ../ingredients/core.cfg
%include ../ingredients/extra-luanti.cfg
```

**Issues:**
- Duplicate `%include` directives across recipes
- Hard to maintain common patterns
- No automatic version matrix

### After: Fragment-Based

**Fragment:** `ingredients/shared/packages/luanti.ks`
```bash
%packages
luanti
%end
```

**Template:** `recipe-generator/recipe_templates.yaml`
```yaml
templates:
  virtual-desktop:
    required:
      - luanti: ingredients/shared/packages/luanti.ks
```

**Recipe:** `recipes/virtual-desktop_43.cfg`
```bash
# Generated automatically
%ksappend ingredients/shared/core/base.ks
%ksappend ingredients/shared/packages/luanti.ks
```

### Migration Benefits

| Aspect | Before | After |
|--------|--------|-------|
| Maintenance | Repetitive includes | Single source in template |
| Variants | Manual recipe creation | Manifest-driven generation |
| Testing | Per-recipe validation | Fragment-level validation |
| Code duplication | High | None (DRY principle) |

### Why `%ksappend` over `%include`?

- **`%include`** - Simple file inclusion (copied into result)
- **`%ksappend`** - References external file (keeps file path in flattened output)

**Benefits of `%ksappend`:**
1. Smaller dish files (no duplicate content)
2. Clear dependency tracking
3. Better validation (fragment existence checks)
4. Easier debugging (visible fragment References)

### Migration Checklist

- [ ] Review all `ingredients/*.cfg` files
- [ ] Identify reusable patterns
- [ ] Create `ingredients/shared/` for common components
- [ ] Update `recipe_templates.yaml` with new structure
- [ ] Update `recipes_manifest.yaml` for variants
- [ ] Regenerate recipes with `make generate-recipes`
- [ ] Validate with `make validate-recipes`
- [ ] Flatten to dishes with `ksflatten`
- [ ] Run tests with `make test`

---

## Troubleshooting

### Common Issues

**1. Duplicate %ksappend entries**

```bash
# Detect duplicates
grep "^%ksappend" recipes/*.cfg | sort | uniq -d
```

**Fix:** Check template for duplicate fragment references

**2. Missing fragment error**

```
ERROR: Missing fragment: ingredients/shared/unknown/missing.ks
```

**Fix:** Verify fragment exists in `ingredients/shared/`

**3. Deprecated command warning**

```
keyboard command is deprecated. Use keyboard --vckeymap instead.
```



**4. pykickstart validation fails**

```bash
# Check fragment with pykickstart
python3 -c "
from pykickstart.parser import KickstartParser
from pykickstart.version import makeVersion, DEVEL
parser = KickstartParser(makeVersion(DEVEL))
try:
    with open('fragment.ks') as f:
        parser.readKickstart(f.read())
    print('Valid')
except Exception as e:
    print(f'Error: {e}')
"
```

### Debugging Generator

```bash
# Verbose mode
python3 generate_recipe.py --manifest recipes_manifest.yaml --output-dir ../recipes/ --verbose

# Check template loading
python3 -c "
from pathlib import Path
import sys
sys.path.insert(0, '.')
from generate_recipe import RecipeGenerator
gen = RecipeGenerator(Path('../ingredients'), Path('recipe_templates.yaml'))
print('Templates:', list(gen.templates.keys()))
"
```

---

## Additional Resources

- **Kickstart Documentation:** https://pykickstart.readthedocs.io/
- **Fedora Kickstarts:** https://pagure.io/fedora-kickstarts
- **virt-install:** `man virt-install`
- **livemedia-creator:** `man livemedia-creator`

---

*Last updated: March 2026*
