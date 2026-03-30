#!/usr/bin/env python3
"""
Recipe generator for Phyllome OS.
Reads recipes_manifest.yaml and generates kickstart recipe files.
"""

import argparse
import itertools
import os
import sys

import yaml


# Template mappings from recipe_templates.yaml
TEMPLATES = {
    'required': {
        'repository': {
            '43': 'repo/fedora-43-mirrors.ks',
            'rawhide': 'repo/rawhide-mirrors.ks',
        },
        'core': {
            'base': 'core/base.ks',
        },
        'bootloader': {
            'grub': 'bootloader/grub.ks',
            'systemd-boot': 'bootloader/systemd-boot.ks',
        },
        'storage': {
            'standard': 'storage/standard.ks',
            'encrypted': 'storage/encrypted.ks',
        },
        'locale': {
            'default': 'core/locale.ks',
        },
        'services': {
            'minimal': 'core/services.ks',
        },
        'network': {
            'network-manager': 'core/network.ks',
        },
        'packages': {
            'core': 'packages/core.ks',
        },
        'brand': {
            'fedora-remix': 'packages/fedora-remix.ks',
        },
        'extra': {
            'extra': 'packages/hand-picked.ks',
        },
        'security': {
            'secure': 'core/security/enabled.ks',
            'insecure': 'core/security/disabled.ks',
        },
        'initial-setup': {
            'server': 'initial-setup/server/config.ks',
            'gnome': 'initial-setup/gnome/config.ks',
            'generic-wayland': 'initial-setup/generic-wayland/config.ks',
        },
    },
    'optional': {
        'hardware-support': 'packages/hardware-support.ks',
        'guest-agents': 'guest-agents/base.ks',
        'hypervisor': {
            'base': [
                'hypervisor/base/packages.ks',
                'hypervisor/base/services.ks',
                'hypervisor/base/post-scripts.ks',
            ],
            'desktop': [
                'packages/virtual-machine-manager/packages.ks',
                'packages/virtual-machine-manager/post-scripts.ks',
            ],
        },
        'desktop': {
            'gnome': [
                'desktop/gnome/config.ks',
                'desktop/gnome/packages.ks',
                'desktop/gnome/post-scripts.ks',
            ],
            'labwc': [
                'desktop/labwc/config.ks',
            ],
        },
        'hypervisor_type': {
            'amdcpu': 'hypervisor/amdcpu.ks',
            'intelcpu': 'hypervisor/intelcpu.ks',
            'intelgpu': 'hypervisor/intelgpu.ks',
        },
    },
    'live': {
        'core': [
            'live/core/base.ks',
            'live/core/storage.ks',
            'live/core/packages.ks',
        ],
        'bootloader': {
            'grub': 'live/core/bootloader/grub.ks',
            'systemd-boot': 'live/core/bootloader/systemd-boot.ks',
        },
        'post': [
            'live/post/base.ks',
            'live/post/session.ks',
        ],
    },
}


def expand_variants(variant_config):
    """Expand variant config with list values into cartesian product."""
    keys = variant_config.keys()
    values = []
    for key in keys:
        val = variant_config[key]
        if isinstance(val, list):
            values.append([(key, v) for v in val])
        else:
            values.append([(key, val)])
    
    combos = itertools.product(*values)
    return [dict(combo) for combo in combos]


def get_required_ingredients(variant):
    """Get required ingredients for a variant."""
    ingredients = []
    
    # Build variant dict with special mappings
    variant_map = dict(variant)
    
    for category, mapping in TEMPLATES['required'].items():
        key = variant_map.get(category, list(mapping.keys())[0])
        if category == 'version':
            key = str(key)
        path = mapping.get(key)
        if path:
            ingredients.append(path)
    
    return ingredients


def get_optional_ingredients(variant):
    """Get optional ingredients based on variant flags."""
    ingredients = []
    
    # Handle boolean flags
    for opt_key in ['hardware-support', 'guest-agents']:
        if variant.get(opt_key):
            path = TEMPLATES['optional'].get(opt_key)
            if path:
                ingredients.append(path)
    
    # Handle live flag
    if variant.get('live'):
        ingredients.extend(TEMPLATES['live']['core'])
        bootloader = variant.get('bootloader', 'grub')
        ingredients.append(TEMPLATES['live']['bootloader'][bootloader])
        ingredients.extend(TEMPLATES['live']['post'])
    
    # Handle desktop
    desktop = variant.get('desktop')
    if desktop:
        desktop_map = TEMPLATES['optional']['desktop']
        if desktop in desktop_map:
            ingredients.extend(desktop_map[desktop])
    
    # Handle hypervisor
    hypervisor = variant.get('hypervisor')
    if hypervisor:
        hypervisor_map = TEMPLATES['optional']['hypervisor']
        if hypervisor in hypervisor_map:
            ingredients.extend(hypervisor_map[hypervisor])
    
    # Handle hypervisor_type
    hypervisor_type = variant.get('hypervisor_type')
    if hypervisor_type:
        path = TEMPLATES['optional']['hypervisor_type'].get(hypervisor_type)
        if path:
            ingredients.append(path)
    
    return ingredients


def generate_filename(variant, group_name=None):
    """Generate filename from variant configuration."""
    parts = []

    # Guest agents
    if variant.get('guest-agents'):
        parts.append('virtual')

    # Desktop
    desktop = variant.get('desktop')
    if desktop:
        parts.append(desktop)

    # Hypervisor type
    if variant.get('hypervisor'):
        parts.append(f"hypervisor-{variant['hypervisor']}")
    
    if variant.get('hypervisor_type'):
        parts.append(variant['hypervisor_type'])
    
    # Storage
    if variant.get('storage') == 'encrypted':
        parts.append('encrypted')
    
    # Bootloader
    if variant.get('bootloader') == 'systemd-boot':
        parts.append('systemd-boot')

    # Hardware support
    if variant.get('hardware-support'):
        parts.append('hardware-support')
        
    # Security (only if not default)
    if variant.get('security') == 'disabled':
        parts.append('security-disabled')
    
    # Add group name if specified (for uniqueness)
    if group_name and group_name in ['desktop-live', 'server-live']:
        parts.append(group_name.replace('live', ''))
    
    # Version
    parts.append(str(variant.get('repository', '43')))
    
    return '_'.join(parts) + '.cfg'


def write_recipe_file(ingredients, variant, output_dir, group_name=None):
    """Write recipe file with header and includes."""
    os.makedirs(output_dir, exist_ok=True)
    
    filename = generate_filename(variant, group_name)
    filepath = os.path.join(output_dir, filename)
    
    header = f"""#            __          ____                        ____  _____
#     ____  / /_  __  __/ / /___  ____ ___  ___     / __ \\/ ___/
#    / __ \\/ __ \\/ / / / / / __ \\/ __ `__ \\/ _ \\   / / / /\\__ \\
#   / /_/ / / / / /_/ / / / /_/ / / / / / /  __/  / /_/ /___/ /
#  / .___/_/ /_/\\__, /_/_/\\____/_/ /_/ /_/\\___/   \\____//____/
# /_/          /____/

# Universal template to generate kickstart recipes for a server, a desktop or a hypervisor system

"""
    
    # Use ingredient paths as-is (simple paths relative to project root)
    # ksflatten-relative will handle conversion during flattening
    seen = set()
    unique_ingredients = []
    for ing in ingredients:
        if ing not in seen:
            seen.add(ing)
            unique_ingredients.append(ing)
    
    includes = '\n'.join(f'%include {ing}' for ing in unique_ingredients)
    
    content = header + includes + '\n'
    
    with open(filepath, 'w') as f:
        f.write(content)
    
    return filepath


def generate_recipes(manifest_path, output_dir):
    """Generate all recipes from manifest."""
    with open(manifest_path) as f:
        manifest = yaml.safe_load(f)
    
    generated = []
    
    for recipe_group in manifest.get('recipes', []):
        group_name = recipe_group.get('name', 'unknown')
        for variant_config in recipe_group.get('variants', []):
            for variant in expand_variants(variant_config):
                required = get_required_ingredients(variant)
                optional = get_optional_ingredients(variant)
                all_ingredients = required + optional
                
                filepath = write_recipe_file(all_ingredients, variant, output_dir, group_name)
                generated.append(filepath)
    
    return generated


def validate_recipe(recipe_path):
    """Validate a recipe file using pykickstart."""
    try:
        from pykickstart.parser import KickstartParser
        from pykickstart.version import returnClassForVersion
        
        ks_class = returnClassForVersion()
        parser = KickstartParser(ks_class)
        
        # Get absolute path and change to that directory for include resolution
        abs_path = os.path.abspath(recipe_path)
        recipe_dir = os.path.dirname(abs_path)
        original_dir = os.getcwd()
        
        os.chdir(recipe_dir)
        parser.readKickstart(abs_path)
        os.chdir(original_dir)
        return True, None
    except Exception as e:
        os.chdir(original_dir)
        return False, str(e)


def validate_all(recipes_dir):
    """Validate all recipes in directory."""
    if not os.path.isdir(recipes_dir):
        print(f"Error: {recipes_dir} is not a directory", file=sys.stderr)
        return False
    
    errors = []
    for filename in sorted(os.listdir(recipes_dir)):
        if filename.endswith('.cfg'):
            filepath = os.path.join(recipes_dir, filename)
            valid, error = validate_recipe(filepath)
            if valid:
                print(f"✓ {filename}")
            else:
                print(f"✗ {filename}: {error}", file=sys.stderr)
                errors.append((filename, error))
    
    return len(errors) == 0


def main():
    parser = argparse.ArgumentParser(description='Generate Phyllome OS recipes')
    parser.add_argument('--manifest', default='recipes_manifest.yaml',
                        help='Path to recipes manifest YAML')
    parser.add_argument('--output-dir', default='recipes/',
                        help='Output directory for recipe files')
    parser.add_argument('--validate', action='store_true',
                        help='Validate generated recipes')
    parser.add_argument('files', nargs='*', default=[],
                        help='Recipe files to validate')
    args = parser.parse_args()
    
    # Generate recipes from cook/ directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Paths relative to cook/ directory
    manifest_path = args.manifest
    if not os.path.isabs(args.manifest):
        manifest_path = os.path.join(script_dir, args.manifest)
    
    output_dir = args.output_dir
    if not os.path.isabs(args.output_dir):
        output_dir = os.path.join(script_dir, args.output_dir)
    
    print(f"Generating recipes from {manifest_path} to {output_dir}...")
    recipes = generate_recipes(manifest_path, output_dir)
    print(f"✓ Generated {len(recipes)} recipe files")
    
    # Validate if requested (from command line files or directory)
    if args.validate or args.files:
        print("\nValidating recipes...")
        if args.files:
            # Validate specific files
            all_valid = True
            for filepath in args.files:
                valid, error = validate_recipe(filepath)
                if valid:
                    print(f"✓ {os.path.basename(filepath)}")
                else:
                    print(f"✗ {os.path.basename(filepath)}: {error}", file=sys.stderr)
                    all_valid = False
            if not all_valid:
                sys.exit(1)
        else:
            # Validate output directory
            if not validate_all(output_dir):
                sys.exit(1)
        print("✓ All recipes validated")


if __name__ == '__main__':
    main()
