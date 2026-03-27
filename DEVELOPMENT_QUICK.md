# Phyllome OS Development Workflow

This is a quick-reference guide for developers. For comprehensive coverage, see [DEVELOPMENT.md](./DEVELOPMENT.md).

## Quick Start

```bash
# Prerequisites
sudo dnf install qemu libvirt virt-install pykickstart
pip install PyYAML

# Verify setup
cd recipe-generator && make generate-recipes 
```

## Core Workflows

### Add Fragment

```bash
# Create new kickstart snippet
cat > ingredients/shared/packages/new-package.ks << 'EOF'
%packages
new-package
%end
```

### Add to Recipe

```bash
# Edit recipe-generator/recipe_templates.yaml to include fragment
# Edit recipe-generator/recipes_manifest.yaml to add variant

# Regenerate
cd recipe-generator && make generate-recipes && make validate-recipes
```

```

### Validate Fragments

```bash
for f in $(find ingredients -name "*.ks"); do
    python3 -c "
from pykickstart.parser import KickstartParser
from pykickstart.version import makeVersion, DEVEL
parser = KickstartParser(makeVersion(DEVEL))
parser.readKickstart(open('$f').read())
" || echo "✗ $f"
done
```

## Architecture

```
ingredients/ (54 .ks) → recipe-generator/generate_recipe.py → recipes/ (16 .cfg) → ksflatten → dishes/ (28 .cfg)
```

See `DEVELOPMENT.md` Section 1 for detailed architecture overview.
