#!/usr/bin/env python3
"""
Recipe Generator for Phyllome OS Kickstart Files

Generates .cfg recipe files from templates and YAML manifest.
"""

import argparse
import sys
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
from itertools import product


# Deprecated/removed command mappings for Fedora 43 (F42) and rawhide
DEPRECATED_COMMANDS: Dict[str, Dict[str, str]] = {
    'authconfig': {
        'status': 'removed',
        'removed_in': 'F34',
        'alternative': 'authselect',
        'message': 'authconfig was removed in Fedora 34. Use authselect instead.'
    },
    'keyboard': {
        'status': 'deprecated',
        'deprecated_in': 'F18',
        'alternative': 'keyboard --vckeymap',
        'message': 'keyboard command is deprecated. Use keyboard --vckeymap instead.'
    },
    'langsupport': {
        'status': 'deprecated',
        'deprecated_in': 'F21',
        'alternative': 'lang',
        'message': 'langsupport is deprecated. Use lang command instead.'
    },
    'nfs': {
        'status': 'deprecated',
        'deprecated_in': 'F23',
        'alternative': 'repo --name=nfs',
        'message': 'nfs command is deprecated. Use repo command instead.'
    },
    'parted': {
        'status': 'deprecated',
        'deprecated_in': 'F13',
        'alternative': 'part',
        'message': 'parted command is deprecated. Use part command instead.'
    },
}


def _import_pykickstart():
    """Import pykickstart modules, returns None if not available."""
    try:
        from pykickstart.parser import KickstartParser
        from pykickstart.version import makeVersion
        from pykickstart.version import DEVEL
        from pykickstart.errors import KickstartParseError, KickstartError
        return {
            'parser': KickstartParser,
            'makeVersion': makeVersion,
            'DEVEL': DEVEL,
            'KickstartParseError': KickstartParseError,
            'KickstartError': KickstartError
        }
    except ImportError:
        return None


class RecipeGenerator:
    """Generate kickstart recipes from templates and modifiers."""

    def __init__(self, ingredients_dir: Path, templates_file: Path):
        self.project_root = Path(__file__).parent.parent
        self.ingredients_dir = self.project_root / ingredients_dir
        self.templates = self.load_templates(templates_file)

    def get_ksversion(self, version: str) -> Optional[str]:
        """Map Phyllome OS version to pykickstart version string."""
        if version == 'rawhide':
            return None
        else:
            return f'F{int(version) - 1}'

    def load_templates(self, path: Path) -> Dict:
        """Load recipe templates from YAML file."""
        try:
            # Template path could be:
            # - Absolute path (already resolved)
            # - Relative path (resolve relative to project root)
            if path.is_absolute():
                template_path = path
            else:
                template_path = self.project_root / path
            with open(template_path) as f:
                data = yaml.safe_load(f)
            return data['templates']
        except FileNotFoundError:
            print(f"Error: Templates file not found: {template_path}", file=sys.stderr)
            sys.exit(2)
        except yaml.YAMLError as e:
            print(f"Error: Invalid YAML in {template_path}: {e}", file=sys.stderr)
            sys.exit(2)

    def validate_template(self, template: Dict) -> List[str]:
        """Validate template structure and fragment existence."""
        errors = []

        # Check required keys
        required_keys = ['description', 'base', 'required']
        for key in required_keys:
            if key not in template:
                errors.append(f"Missing required key: {key}")

        # Validate base ingredient exists (for compatibility with old ingredients)
        if 'base' in template:
            base_path = self.ingredients_dir / f"{template['base']}.cfg"
            if not base_path.exists():
                errors.append(f"Base ingredient not found: {template['base']}.cfg")

        # Validate required fragments exist
        for item in template.get('required', []):
            if isinstance(item, dict):
                fragment_path = list(item.values())[0]
            else:
                continue
            
            # Handle both absolute fragment paths and old ingredient names
            if fragment_path.startswith('fragments/'):
                full_path = self.project_root / fragment_path
            else:
                full_path = self.ingredients_dir / f"{fragment_path}.cfg"
            
            if not full_path.exists():
                errors.append(f"Required fragment not found: {fragment_path}")

        # Validate optional fragment values
        for opt_key, opt_config in template.get('optional', {}).items():
            if isinstance(opt_config, dict):
                for value, fragment_path in opt_config.items():
                    # Skip None values
                    if fragment_path is None:
                        continue
                    # Handle lists
                    if isinstance(fragment_path, list):
                        for fp in fragment_path:
                            if fp is None:
                                continue
                            if fp.startswith('fragments/'):
                                full_path = self.project_root / fp
                            else:
                                full_path = self.ingredients_dir / f"{fp}.cfg"
                            if not full_path.exists():
                                errors.append(f"Optional fragment not found: {fp} (in list for {opt_key}={value})")
                    else:
                        if fragment_path.startswith('fragments/'):
                            full_path = self.project_root / fragment_path
                        else:
                            full_path = self.ingredients_dir / f"{fragment_path}.cfg"
                        
                        if not full_path.exists():
                            errors.append(f"Optional fragment not found: {fragment_path} (for {opt_key}={value})")
            elif isinstance(opt_config, list):
                for fragment_path in opt_config:
                    if fragment_path is None:
                        continue
                    if fragment_path.startswith('fragments/'):
                        full_path = self.project_root / fragment_path
                    else:
                        full_path = self.ingredients_dir / f"{fragment_path}.cfg"
                    
                    if not full_path.exists():
                        errors.append(f"Optional fragment not found: {fragment_path} (in list)")

        return errors
    def validate_manifest(self, manifest: Dict) -> List[str]:
        """Validate manifest structure."""
        errors = []

        if 'recipes' not in manifest:
            errors.append("Manifest missing 'recipes' key")
            return errors

        for recipe_config in manifest['recipes']:
            if 'name' not in recipe_config:
                errors.append("Recipe config missing 'name' key")
            if 'variants' not in recipe_config:
                errors.append(f"Recipe '{recipe_config.get('name', 'unnamed')}' missing 'variants' key")
                continue

            for variant in recipe_config['variants']:
                if 'version' not in variant:
                    errors.append(f"Recipe '{recipe_config['name']}' variant missing 'version'")
                # Support explicit variant name for install variants
                if 'name' in variant:
                    variant_subname = variant['name']
                else:
                    variant_subname = ''

        return errors

    def generate_recipe(self, recipe_type: str, version: str, **modifiers) -> str:
        """Generate a recipe from template with modifiers."""
        if recipe_type not in self.templates:
            print(f"Error: Unknown recipe type: {recipe_type}", file=sys.stderr)
            sys.exit(1)

        template = self.templates[recipe_type]

        # Validate template
        errors = self.validate_template(template)
        if errors:
            print(f"Error: Invalid template '{recipe_type}':", file=sys.stderr)
            for error in errors:
                print(f"  - {error}", file=sys.stderr)
            sys.exit(1)

        lines = self.build_header(template['description'], recipe_type, version, modifiers)
        lines.extend(self.build_includes(template, version, modifiers))

        return '\n'.join(lines)

    def build_header(self, description: str, recipe_type: str, 
                     version: str, modifiers: Dict) -> List[str]:
        """Build the ASCII art header and description."""
        header = [
            "#            __          ____                        ____  _____",
            "#     ____  / /_  __  __/ / /___  ____ ___  ___     / __ \\/ ___/",
            "#    / __ \\/ __ \\/ / / / / / __ \\/ __ `__ \\/ _ \\   / / / /\\__ \\",
            "#   / /_/ / / / / /_/ / / / /_/ / / / / / /  __/  / /_/ /___/ /",
            "#  / .___/_/ /_/\\__, /_/_/\\____/_/ /_/ /_/\\___/   \\____//____/",
            "# /_/          /____/",
            "",
            f"# {description}",
            "",
        ]
        return header

    def build_includes(self, template: Dict, version: str, modifiers: Dict) -> List[str]:
        """Build %ksappend lines from template and modifiers."""
        includes = []
        seen = set()  # Track to prevent duplicates
        # Add version to modifiers for template processing
        modifiers = modifiers.copy()
        modifiers['version'] = version

        # Keys that can be overridden by modifiers
        override_keys = {'security', 'bootloader', 'version'}

        # Add required includes
        for item in template.get('required', []):
            if isinstance(item, dict):
                key = list(item.keys())[0]
                fragment_path = list(item.values())[0]
                
                # Skip required fragment if modifier overrides it
                if key in override_keys and key in modifiers:
                    continue

                if fragment_path not in seen:
                    includes.append(f"%ksappend {fragment_path}")
                    seen.add(fragment_path)

        # Add optional includes based on modifiers
        for opt_key, opt_config in template.get('optional', {}).items():
            if opt_key in modifiers:
                value = modifiers[opt_key]
                
                # Case 1: opt_config is nested dict (e.g., virtualization, variant_type)
                # and value is string/int (select from options)
                if isinstance(opt_config, dict) and not isinstance(value, (dict, list)):
                    if value in opt_config:
                        fragment_path = opt_config[value]
                        if isinstance(fragment_path, list):
                            for fp in fragment_path:
                                if fp is not None and fp not in seen:
                                    includes.append(f"%ksappend {fp}")
                                    seen.add(fp)
                        elif fragment_path and fragment_path not in seen:
                            includes.append(f"%ksappend {fragment_path}")
                            seen.add(fragment_path)
                
                # Case 2: opt_config is nested dict (e.g., virtualization)
                # and value is dict (nested structure)
                elif isinstance(opt_config, dict) and isinstance(value, dict):
                    for nested_key in value:
                        if nested_key in opt_config:
                            nested_value = opt_config[nested_key]
                            if isinstance(nested_value, list):
                                for fp in nested_value:
                                    if fp is not None and fp not in seen:
                                        includes.append(f"%ksappend {fp}")
                                        seen.add(fp)
                            elif nested_value is not None and nested_value not in seen:
                                includes.append(f"%ksappend {nested_value}")
                                seen.add(nested_value)
                
                # Case 3: opt_config is nested dict, value is boolean (additive)
                elif isinstance(opt_config, dict) and isinstance(value, bool) and value:
                    for nested_key, nested_value in opt_config.items():
                        if isinstance(nested_value, list):
                            for fp in nested_value:
                                if fp is not None and fp not in seen:
                                    includes.append(f"%ksappend {fp}")
                                    seen.add(fp)
                        elif nested_value is not None and nested_value not in seen:
                            includes.append(f"%ksappend {nested_value}")
                            seen.add(nested_value)
                
                # Case 4: opt_config is list, value is boolean (boolean flag)
                elif isinstance(opt_config, list) and value is True:
                    for fragment_path in opt_config:
                        if fragment_path is not None and fragment_path not in seen:
                            includes.append(f"%ksappend {fragment_path}")
                            seen.add(fragment_path)
        
        # Handle modifiers section
        for mod_key, mod_value in modifiers.items():
            # Normalize key: convert underscores to hyphens for template lookup
            mod_key_normalized = mod_key.replace('_', '-')
            if mod_key_normalized in template.get('modifiers', {}):
                mod_key_to_use = mod_key_normalized
            elif mod_key in template.get('modifiers', {}):
                mod_key_to_use = mod_key
            else:
                continue
            mod_config = template['modifiers'][mod_key_to_use]
            
            # Handle nested dict modifiers
            if isinstance(mod_config, dict) and isinstance(mod_value, str):
                if mod_value in mod_config:
                    fragment_path = mod_config[mod_value]
                    if isinstance(fragment_path, list):
                        for fp in fragment_path:
                            if fp is not None and fp not in seen:
                                includes.append(f"%ksappend {fp}")
                                seen.add(fp)
                    elif fragment_path and fragment_path not in seen:
                        includes.append(f"%ksappend {fragment_path}")
                        seen.add(fragment_path)
            
            # Handle list modifiers
            elif isinstance(mod_config, dict) and isinstance(mod_value, list):
                for item in mod_value:
                    if item in mod_config:
                        fragment_path = mod_config[item]
                        if isinstance(fragment_path, list):
                            for fp in fragment_path:
                                if fp is not None and fp not in seen:
                                    includes.append(f"%ksappend {fp}")
                                    seen.add(fp)
                        elif fragment_path and fragment_path not in seen:
                            includes.append(f"%ksappend {fragment_path}")
                            seen.add(fragment_path)

        return includes

    def validate_recipe(self, content: str) -> List[str]:
        """Validate recipe content, return list of warnings/errors."""
        issues = []
        includes = [line for line in content.split('\n') if line.startswith('%ksappend')]
        
        # Check for duplicate includes
        seen = set()
        for inc in includes:
            parts = inc.split()
            if len(parts) < 2:
                continue
            path = parts[1]
            if path in seen:
                issues.append(f"Duplicate include: {path}")
            seen.add(path)

        # Check fragment existence (relative to project root)
        for inc in includes:
            parts = inc.split()
            if len(parts) < 2:
                continue
            path = parts[1]
            fragment_path = self.project_root / path
            if not fragment_path.exists():
                issues.append(f"Missing fragment: {path}")

        return issues

    def validate_recipe_semantic(self, content: str, version: str) -> List[str]:
        """Validate recipe using pykickstart parser with version-specific checks."""
        issues = []
        
        modules = _import_pykickstart()
        if modules is None:
            issues.append("Warning: pykickstart not installed, skipping semantic validation")
            return issues
        
        KickstartParser = modules['parser']
        makeVersion = modules['makeVersion']
        KickstartParseError = modules['KickstartParseError']
        KickstartError = modules['KickstartError']
        
        ks_version_str = self.get_ksversion(version)
        if ks_version_str:
            ks_version = makeVersion(ks_version_str)
        else:
            ks_version = makeVersion(modules['DEVEL'])
        
        try:
            parser = KickstartParser(ks_version)
            parser.readKickstartFromString(content)
        except KickstartParseError as e:
            issues.append(f"Syntax error line {e.lineno}: {e.message}")
        except KickstartError as e:
            issues.append(f"Validation error: {str(e)}")
        except Exception as e:
            issues.append(f"Unexpected error during parsing: {str(e)}")
        
        # Check for deprecated commands in the content
        issues.extend(self._check_deprecated_commands(content))
        
        return issues

    def _check_deprecated_commands(self, content: str) -> List[str]:
        """Check for deprecated and removed commands with suggestions."""
        issues = []
        
        for line_num, line in enumerate(content.split('\n'), start=1):
            # Skip comments and empty lines
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
                continue
            
            # Extract command (first word after % if in section, or just the first word)
            if stripped.startswith('%'):
                continue  # Skip section headers
            
            parts = stripped.split()
            if not parts:
                continue
            
            cmd = parts[0]
            
            if cmd in DEPRECATED_COMMANDS:
                cmd_info = DEPRECATED_COMMANDS[cmd]
                status = cmd_info['status']
                msg = cmd_info['message']
                
                if status == 'removed':
                    issues.append(f"ERROR: Line {line_num}: {msg}")
                else:
                    issues.append(f"Warning: Line {line_num}: {msg}")
        
        return issues

    def extract_version(self, content: str, filename: str) -> Optional[str]:
        """Extract Fedora version from recipe content or filename."""
        import re
        filename_match = re.search(r'(?:_|-)(43|rawhide)(?:_|-|.cfg|.yaml|$)', filename)
        if filename_match:
            return filename_match.group(1)
        
        for line in content.split('\n'):
            # Check for old %include references
            if 'core-fedora-repo-43' in line:
                return '43'
            elif 'core-fedora-repo-rawhide' in line:
                return 'rawhide'
            # Check for new %ksappend references
            if 'generic-43/repo' in line:
                return '43'
            elif 'generic-rawhide/repo' in line:
                return 'rawhide'
        
        return None

    def generate_filename(self, recipe_type: str, version: str, **modifiers) -> str:
        """Generate recipe filename from parameters."""
        # Extract variant subname if present
        variant_subname = modifiers.get('variant_subname', '')
        if not variant_subname:
            variant_subname = modifiers.get('variant_type', '')
        
        # Build base parts
        parts = [recipe_type.replace('_', '-')]
        
        # Add variant subname for install variants (desktop, server, hypervisor, hypervisor-desktop)
        if variant_subname and variant_subname in ['desktop', 'server', 'hypervisor', 'hypervisor-desktop']:
            parts.append(variant_subname)
        
        # Add hypervisor-type suffix (list or single value)
        if modifiers.get('hypervisor_type'):
            ht = modifiers['hypervisor_type']
            if isinstance(ht, list):
                for h in ht:
                    if h:
                        parts.append(h)
            elif ht:
                parts.append(ht)
        
        # Add desktop (non-GNOME only, since GNOME is default)
        if modifiers.get('desktop') and modifiers['desktop'] != 'gnome':
            parts.append(modifiers['desktop'])
        
        # Add version
        parts.append(str(version))
        
        # Add security suffix (devel only, since secure is default)
        if modifiers.get('security') == 'off':
            parts.append('devel')
        
        # Add storage suffix (encrypted only, since standard is default)
        if modifiers.get('storage') == 'encrypted':
            parts.append('encrypted')
        
        # Add hardware-support suffix (hw when enabled)
        if modifiers.get('hardware-support') is True:
            parts.append('hw')
        
        # Add guest-agents suffix (ga when enabled)
        if modifiers.get('guest-agents') is True:
            parts.append('ga')
        
        return '_'.join(parts) + '.cfg'


    def expand_variants(self, variants: List[Dict]) -> List[Dict]:
        """Expand variants with list values into individual variants."""
        expanded = []
        
        for variant in variants:
            list_keys = {}
            scalar_keys = {}
            
            for key, value in variant.items():
                if isinstance(value, list):
                    list_keys[key] = value
                else:
                    scalar_keys[key] = value
            
            if not list_keys:
                expanded.append(variant)
                continue
            
            keys = list(list_keys.keys())
            values_product = product(*[list_keys[k] for k in keys])
            
            for combo in values_product:
                new_variant = scalar_keys.copy()
                for i, key in enumerate(keys):
                    new_variant[key] = combo[i]
                expanded.append(new_variant)
        
        return expanded


def main():
    parser = argparse.ArgumentParser(
        description='Generate Phyllome OS kickstart recipes from templates',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Global options
    SCRIPTS_DIR = Path(__file__).resolve().parent
    PROJECT_ROOT = SCRIPTS_DIR.parent
    
    parser.add_argument('--ingredients', '-i',
                        type=Path, default=PROJECT_ROOT / 'ingredients',
                        help='Ingredients directory (default: parent/ingredients)')
    parser.add_argument('--templates', '-t',
                        type=Path, default=SCRIPTS_DIR / 'recipe_templates.yaml',
                        help='Templates YAML file (default: ./recipe_templates.yaml)')
    
    # Batch mode
    parser.add_argument('--manifest', '-m',
                        type=Path, help='Manifest YAML for batch generation')
    parser.add_argument('--output-dir', '-d',
                        type=Path, default=SCRIPTS_DIR / 'recipes',
                        help='Output directory (batch generation, default: ./recipes)')
    parser.add_argument('--dry-run', '-n',
                        action='store_true',
                        help='Show what would be generated without writing files')
    
    # Single generation mode
    parser.add_argument('--type', '-T',
                        help='Recipe type (e.g., virtual-desktop)')
    parser.add_argument('--output', '-o',
                        type=Path, help='Output file (single generation)')
    
    # Recipe parameters
    parser.add_argument('--version', '-v',
                        choices=['43', 'rawhide'], default='43',
                        help='Fedora version (default: 43)')

    parser.add_argument('--desktop',
                        choices=['gnome', 'labwc'],
                        default='gnome',
                        help='Desktop environment (default: gnome)')
    parser.add_argument('--storage',
                        choices=['standard', 'encrypted'],
                        help='Storage type (default: standard)')
    parser.add_argument('--security',
                        choices=['secure', 'devel'],
                        help='Security mode (default: secure)')
    parser.add_argument('--cpu',
                        choices=['generic', 'amdcpu', 'intelcpu'],
                        help='CPU optimization')
    parser.add_argument('--gpu',
                        choices=['none', 'intelgpu'],
                        default='none',
                        help='GPU passthrough (default: none)')
    
    # Validation mode
    parser.add_argument('--validate', '-V',
                        nargs='+',
                        help='Validate recipe files')
    
    # Strict mode for CI
    parser.add_argument('--strict',
                        action='store_true',
                        help='Treat warnings as errors (CI mode)')
    
    args = parser.parse_args()

    # Initialize generator
    generator = RecipeGenerator(args.ingredients, args.templates)

    # Validation mode
    if args.validate:
        all_issues = []
        for recipe_path in args.validate:
            try:
                with open(recipe_path) as f:
                    content = f.read()
                issues = generator.validate_recipe(content)
                
                # Extract version and perform semantic validation
                filename = Path(recipe_path).stem
                version = generator.extract_version(content, filename)
                if version:
                    semantic_issues = generator.validate_recipe_semantic(content, version)
                    issues.extend(semantic_issues)
                else:
                    issues.append("Warning: Could not determine version, skipping semantic validation")
                
                if issues:
                    all_issues.append((recipe_path, issues))
            except FileNotFoundError:
                print(f"Error: Recipe not found: {recipe_path}", file=sys.stderr)
                sys.exit(2)
        
        if all_issues:
            print("=== Recipe Validation Report ===", file=sys.stderr)
            for path, issues in all_issues:
                print(f"\n{path}:", file=sys.stderr)
                error_count = sum(1 for i in issues if 'ERROR' in i)
                warning_count = sum(1 for i in issues if 'Warning:' in i)
                
                if error_count > 0:
                    for issue in issues:
                        if 'ERROR' in issue:
                            print(f"  {issue}", file=sys.stderr)
                
                if warning_count > 0:
                    for issue in issues:
                        if 'Warning:' in issue:
                            print(f"  {issue}", file=sys.stderr)
                
                if error_count == 0 and warning_count == 0:
                    print(f"  No issues found (file exists)", file=sys.stderr)
            
            print(f"\nSummary:", file=sys.stderr)
            print(f"  - {len(all_issues)} recipe(s) checked", file=sys.stderr)
            
            total_errors = sum(len([i for i in issues if 'ERROR' in i]) for _, issues in all_issues)
            total_warnings = sum(len([i for i in issues if 'Warning:' in i]) for _, issues in all_issues)
            print(f"  - {total_errors} error(s), {total_warnings} warning(s)", file=sys.stderr)
            
            # Strict mode: treat warnings as errors
            if args.strict and total_warnings > 0:
                print("\nStrict mode: Warnings treated as errors", file=sys.stderr)
                sys.exit(1)
            
            if total_errors > 0:
                sys.exit(1)
        else:
            print("All recipes validated successfully")
            sys.exit(0)

    # Batch generation mode
    if args.manifest:
        try:
            with open(args.manifest) as f:
                manifest = yaml.safe_load(f)
        except FileNotFoundError:
            print(f"Error: Manifest file not found: {args.manifest}", file=sys.stderr)
            sys.exit(2)
        except yaml.YAMLError as e:
            print(f"Error: Invalid YAML in manifest: {e}", file=sys.stderr)
            sys.exit(2)

        # Validate manifest
        errors = generator.validate_manifest(manifest)
        if errors:
            print(f"Error: Invalid manifest:", file=sys.stderr)
            for error in errors:
                print(f"  - {error}", file=sys.stderr)
            sys.exit(1)

        # Generate all recipes
        for recipe_config in manifest.get('recipes', []):
            recipe_type = recipe_config['name']
            if recipe_type not in generator.templates:
                print(f"Error: Unknown recipe type in manifest: {recipe_type}", file=sys.stderr)
                sys.exit(1)

            variants = recipe_config.get('variants', [])
            variants = generator.expand_variants(variants)
            for variant in variants:
                version = variant['version']
                # Build modifiers dict (exclude 'name', 'version')
                modifiers = {k: v for k, v in variant.items() if k not in ['name', 'version']}
                # Extract subname (variant name) if present, otherwise empty
                variant_subname = variant.get('name', '')
                # Use variant_name as variant_type modifier
                if variant_subname:
                    modifiers['variant_type'] = variant_subname
                # Add variant_subname to modifiers for generate_filename
                if variant_subname:
                    modifiers['variant_subname'] = variant_subname

                content = generator.generate_recipe(recipe_type, version, **modifiers)

                if args.validate and not args.dry_run:
                    issues = generator.validate_recipe(content)
                    semantic_issues = generator.validate_recipe_semantic(content, version)
                    all_issues = issues + semantic_issues
                    if all_issues:
                        print(f"Validation issues for {recipe_type} {version}:", file=sys.stderr)
                        for issue in issues:
                            print(f"  - {issue}", file=sys.stderr)
                        sys.exit(1)

                filename = generator.generate_filename(recipe_type, version, **modifiers)
                output_path = args.output_dir / filename

                if args.dry_run:
                    print(f"Would generate: {output_path}")
                else:
                    print(f"Generating: {output_path}")
                    with open(output_path, 'w') as f:
                        f.write(content)

        sys.exit(0)

    # Single generation mode
    if args.type:
        modifiers = {
            'variant_type': 'desktop',
            'desktop': args.desktop if args.desktop else None,
            'storage': args.storage if args.storage != 'standard' else None,
            'security': args.security if args.security != 'secure' else None,
            'cpu': args.cpu if args.cpu and args.cpu != 'generic' else None,
            'gpu': args.gpu if args.gpu and args.gpu != 'none' else None,
        }
        # Filter out None/False values
        modifiers = {k: v for k, v in modifiers.items() if v is not None}

        content = generator.generate_recipe(args.type, args.version, **modifiers)

        if args.validate:
            issues = generator.validate_recipe(content)
            semantic_issues = generator.validate_recipe_semantic(content, args.version)
            all_issues = issues + semantic_issues
            if all_issues:
                print("Validation issues:", file=sys.stderr)
                for issue in issues:
                    print(f"  - {issue}", file=sys.stderr)
                sys.exit(1)
            else:
                print("Validation passed")

        if args.output:
            if args.dry_run:
                print(f"Would write to: {args.output}")
            else:
                with open(args.output, 'w') as f:
                    f.write(content)
                print(f"Generated: {args.output}")
        else:
            print(content)

        sys.exit(0)

    # No mode specified, show help
    parser.print_help()
    sys.exit(1)


if __name__ == '__main__':
    main()
