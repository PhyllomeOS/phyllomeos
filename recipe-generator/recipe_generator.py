"""Core recipe generation logic."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

from validators import (
    TemplateValidator,
    ContentValidator,
    SemanticValidator,
    validate_manifest,
)

import yaml

HEADER_ASCII_ART = [
    "#            __          ____                        ____  _____",
    "#     ____  / /_  __  __/ / /___  ____ ___  ___     / __ \\/ ___/",
    "#    / __ \\/ __ \\/ / / / / / __ \\/ __ `__ \\/ _ \\   / / / /\\__ \\",
    "#   / /_/ / / / / /_/ / / / /_/ / / / / / /  __/  / /_/ /___/ /",
    "#  / .___/_/ /_/\\__, /_/_/\\____/_/ /_/ /_/\\___/   \\____//____/",
    "# /_/          /____/",
    "",
]


class RecipeGenerator:
    """Generate kickstart recipes from templates and modifiers."""

    def __init__(self, ingredients_dir_or_templates: Optional[Path] = None, templates_file: Optional[Path] = None):
        """Initialize RecipeGenerator.
        
        Args:
            ingredients_dir_or_templates: Either ingredients_dir (deprecated) or templates_file
            templates_file: Path to the templates YAML file (if ingredients_dir provided)
        """
        # Handle both positional arg patterns:
        # RecipeGenerator(templates_file) - new style
        # RecipeGenerator(ingredients_dir, templates_file) - old style
        if templates_file is None:
            # Old style: single arg which is actually templates_file
            templates_file = ingredients_dir_or_templates
        else:
            # New style: both args provided (old style with ingredients_dir)
            pass
        
        self.project_root = templates_file.parent.parent
        self.templates = self._load_templates(templates_file)

    def _load_templates(self, path: Path) -> Dict:
        """Load recipe templates from YAML file."""
        try:
            if path.is_absolute():
                template_path = path
            else:
                template_path = self.project_root / path
            with open(template_path, encoding='utf-8') as f:
                data = yaml.safe_load(f)
            return data['templates']
        except FileNotFoundError:
            print(f"Error: Templates file not found: {template_path}")
            exit(2)
        except yaml.YAMLError as e:
            print(f"Error: Invalid YAML in {template_path}: {e}")
            exit(2)

    def generate(self, recipe_type: str, version: str, **modifiers) -> str:
        """Generate a recipe from template with modifiers."""
        if recipe_type not in self.templates:
            print(f"Error: Unknown recipe type: {recipe_type}")
            exit(1)

        template = self.templates[recipe_type]

        lines = self._build_header(template['description'])
        lines.extend(self._build_includes(template, version, modifiers))

        return '\n'.join(lines)
    
    generate_recipe = generate  # Compatibility alias

    def _build_header(self, description: str) -> List[str]:
        """Build the ASCII art header and description."""
        header = HEADER_ASCII_ART.copy()
        header.append(f"# {description}")
        header.append("")
        return header

    def _build_includes(self, template: Dict, version: str, modifiers: Dict) -> List[str]:
        """Build %include lines from template and modifiers."""
        includes = []
        seen = set()

        # Add version to modifiers for template processing
        modifiers = modifiers.copy()
        modifiers['version'] = version

        # Add required includes (all ingredients listed under 'required')
        for item in template.get('required', []):
            if isinstance(item, dict):
                fragment_path = list(item.values())[0]
            else:
                fragment_path = item

            if fragment_path not in seen:
                includes.append(f"%include {fragment_path}")
                seen.add(fragment_path)

        # Add modifiers section includes
        for mod_key, mod_value in modifiers.items():
            # Normalize key: convert underscores to hyphens for template lookup
            mod_key_normalized = mod_key.replace("_", "-")
            if mod_key_normalized in template.get("modifiers", {}):
                mod_key_to_use = mod_key_normalized
            elif mod_key in template.get("modifiers", {}):
                mod_key_to_use = mod_key
            else:
                continue
            mod_config = template["modifiers"][mod_key_to_use]
            
            # Handle nested dict modifiers with string values
            if isinstance(mod_config, dict) and isinstance(mod_value, str):
                if mod_value in mod_config:
                    fragment_path = mod_config[mod_value]
                    if isinstance(fragment_path, list):
                        for fp in fragment_path:
                            if fp is not None and fp not in seen:
                                includes.append(f"%include {fp}")
                                seen.add(fp)
                    elif fragment_path and fragment_path not in seen:
                        includes.append(f"%include {fragment_path}")
                        seen.add(fragment_path)
            
            # Handle list modifiers
            elif isinstance(mod_config, dict) and isinstance(mod_value, list):
                for item in mod_value:
                    if item in mod_config:
                        fragment_path = mod_config[item]
                        if isinstance(fragment_path, list):
                            for fp in fragment_path:
                                if fp is not None and fp not in seen:
                                    includes.append(f"%include {fp}")
                                    seen.add(fp)
                        elif fragment_path and fragment_path not in seen:
                            includes.append(f"%include {fragment_path}")
                            seen.add(fragment_path)

        # Add optional includes based on modifiers
        for opt_key, opt_config in template.get("optional", {}).items():
            if opt_key in modifiers:
                value = modifiers[opt_key]
                
                # Case 1: opt_config is nested dict, value is string/int
                if isinstance(opt_config, dict) and not isinstance(value, (dict, list)):
                    if value in opt_config:
                        fragment_path = opt_config[value]
                        if isinstance(fragment_path, list):
                            for fp in fragment_path:
                                if fp is not None and fp not in seen:
                                    includes.append(f"%include {fp}")
                                    seen.add(fp)
                        elif fragment_path and fragment_path not in seen:
                            includes.append(f"%include {fragment_path}")
                            seen.add(fragment_path)
                
                # Case 2: opt_config is nested dict, value is dict
                elif isinstance(opt_config, dict) and isinstance(value, dict):
                    for nested_key in value:
                        if nested_key in opt_config:
                            nested_value = opt_config[nested_key]
                            if isinstance(nested_value, list):
                                for fp in nested_value:
                                    if fp is not None and fp not in seen:
                                        includes.append(f"%include {fp}")
                                        seen.add(fp)
                            elif nested_value is not None and nested_value not in seen:
                                includes.append(f"%include {nested_value}")
                                seen.add(nested_value)
                
                # Case 3: opt_config is nested dict, value is boolean
                elif isinstance(opt_config, dict) and isinstance(value, bool) and value:
                    for nested_key, nested_value in opt_config.items():
                        if isinstance(nested_value, list):
                            for fp in nested_value:
                                if fp is not None and fp not in seen:
                                    includes.append(f"%include {fp}")
                                    seen.add(fp)
                        elif nested_value is not None and nested_value not in seen:
                            includes.append(f"%include {nested_value}")
                            seen.add(nested_value)
                
                # Case 4: opt_config is list, value is boolean
                elif isinstance(opt_config, list) and value is True:
                    for fragment_path in opt_config:
                        if fragment_path is not None and fragment_path not in seen:
                            includes.append(f"%include {fragment_path}")
                            seen.add(fragment_path)

        # Add versioned includes
        versioned = template.get('versioned', {})
        for fragment_path in versioned.values():
            # Substitute {version} placeholder
            resolved_path = fragment_path.format(version=version)
            if resolved_path not in seen:
                includes.append(f"%include {resolved_path}")
                seen.add(resolved_path)

        # Add conditional includes based on modifiers
        conditional = template.get('conditional', {})
        for mod_key, mod_config in conditional.items():
            if mod_key.replace('-', '_') in modifiers:
                value = modifiers[mod_key.replace('-', '_')]
            elif mod_key in modifiers:
                value = modifiers[mod_key]
            else:
                continue

            if isinstance(mod_config, dict) and not isinstance(value, (dict, list)):
                if value in mod_config:
                    fragment_path = mod_config[value]
                    if isinstance(fragment_path, list):
                        for fp in fragment_path:
                            if fp is not None and fp not in seen:
                                includes.append(f"%include {fp}")
                                seen.add(fp)
                    elif fragment_path and fragment_path not in seen:
                        includes.append(f"%include {fragment_path}")
                        seen.add(fragment_path)

            elif isinstance(mod_config, dict) and isinstance(value, dict):
                for nested_key in value:
                    if nested_key in mod_config:
                        nested_value = mod_config[nested_key]
                        if isinstance(nested_value, list):
                            for fp in nested_value:
                                if fp is not None and fp not in seen:
                                    includes.append(f"%include {fp}")
                                    seen.add(fp)
                        elif nested_value is not None and nested_value not in seen:
                            includes.append(f"%include {nested_value}")
                            seen.add(nested_value)

            elif isinstance(mod_config, dict) and isinstance(value, bool) and value:
                for nested_key, nested_value in mod_config.items():
                    if isinstance(nested_value, list):
                        for fp in nested_value:
                            if fp is not None and fp not in seen:
                                includes.append(f"%include {fp}")
                                seen.add(fp)
                    elif nested_value is not None and nested_value not in seen:
                        includes.append(f"%include {nested_value}")
                        seen.add(nested_value)

            elif isinstance(mod_config, list) and isinstance(value, bool) and value:
                for fragment_path in mod_config:
                    if fragment_path is not None and fragment_path not in seen:
                        includes.append(f"%include {fragment_path}")
                        seen.add(fragment_path)

        # Add flag includes (boolean toggles)
        for mod_key, mod_value in modifiers.items():
            mod_key_normalized = mod_key.replace('_', '-')
            if mod_key_normalized in template.get('flags', {}):
                fragment_path = template['flags'][mod_key_normalized]
                if mod_value is True and fragment_path not in seen:
                    includes.append(f"%include {fragment_path}")
                    seen.add(fragment_path)

        return includes

    def _get_modifier(self, modifiers: dict, key: str, default=None):
        """Get modifier value, checking both hyphenated and underscored versions."""
        if key in modifiers:
            return modifiers[key]
        alt_key = key.replace('_', '-')
        if alt_key in modifiers:
            return modifiers[alt_key]
        return default

    def generate_filename(self, recipe_type: str, version: str, **modifiers) -> str:
        """Generate recipe filename from parameters."""

        # Extract variant subname if present
        variant_subname = modifiers.get('variant_subname', '')
        if not variant_subname:
            variant_subname = modifiers.get('variant_type', '')

        # Build base parts
        parts = [recipe_type.replace('_', '-')]

        # Add guest_agents suffix (for both True and False)
        guest_agents = self._get_modifier(modifiers, 'guest_agents')
        if guest_agents is True:
            parts.append('virtual')
        elif guest_agents is False:
            parts.append('bare-metal')

        # Add variant_subname for install variants
        if variant_subname and variant_subname in ['desktop', 'server', 'hypervisor', 'hypervisor-desktop']:
            parts.append(variant_subname)

        # Add hypervisor_type suffix
        if modifiers.get('hypervisor_type'):
            ht = modifiers['hypervisor_type']
            if isinstance(ht, list):
                for h in ht:
                    if h:
                        parts.append(h)
            elif ht:
                parts.append(ht)

        # Add desktop (non-GNOME only, since GNOME is default)
        desktop = self._get_modifier(modifiers, 'desktop')
        if desktop and desktop != 'gnome':
            parts.append(desktop)

        # Add security suffix (devel only, since secure is default)
        security = self._get_modifier(modifiers, 'security')
        if security == 'off':
            parts.append('devel')

        # Add storage suffix (encrypted only, since standard is default)
        storage = self._get_modifier(modifiers, 'storage')
        if storage == 'encrypted':
            parts.append('encrypted')

        # Add hardware_support suffix (for True only)
        hardware_support = self._get_modifier(modifiers, 'hardware_support')
        if hardware_support is True:
            parts.append('hw')

        # Add initial_setup suffix (non-server values)
        initial_setup = self._get_modifier(modifiers, 'initial_setup')
        if initial_setup and initial_setup != 'server':
            parts.append(f'{initial_setup}-setup')

        # Add bootloader suffix (systemd-boot only)
        bootloader = self._get_modifier(modifiers, 'bootloader')
        if bootloader == 'systemd-boot':
            parts.append('systemd-boot')

        # Add version
        parts.append(str(version))

        return '_'.join(parts) + '.cfg'

    def expand_variants(self, variants: List[Dict]) -> List[Dict]:
        """Expand variants with list values into individual variants."""
        from itertools import product as itertools_product

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
            values_product = itertools_product(*[list_keys[k] for k in keys])

            for combo in values_product:
                new_variant = scalar_keys.copy()
                for i, key in enumerate(keys):
                    new_variant[key] = combo[i]
                expanded.append(new_variant)

        return expanded

    def validate_template(self, template: Dict) -> List[str]:
        """Validate template structure and fragment existence."""
        validator = TemplateValidator(self.project_root)
        return validator.validate(template)

    def validate_manifest(self, manifest: Dict) -> List[str]:
        """Validate manifest structure."""
        return validate_manifest(manifest)

    def validate_recipe(self, content: str) -> List[str]:
        """Validate recipe content."""
        validator = ContentValidator(self.project_root)
        return validator.validate(content)

    def validate_recipe_semantic(self, content: str, version: str) -> List[str]:
        """Validate recipe using pykickstart parser."""
        validator = SemanticValidator()
        return validator.validate(content, version)

    def get_ksversion(self, version: str) -> Optional[str]:
        """Map Phyllome OS version to pykickstart version string."""
        return SemanticValidator().get_ksversion(version)

    def extract_version(self, content: str, filename: str) -> Optional[str]:
        """Extract Fedora version from recipe content or filename."""
        import re

        filename_match = re.search(r'(?:_|-)(43|rawhide)(?:_|-|.cfg|.yaml|$)', filename)
        if filename_match:
            return filename_match.group(1)

        for line in content.split('\n'):
            if 'core-fedora-repo-43' in line:
                return '43'
            elif 'core-fedora-repo-rawhide' in line:
                return 'rawhide'
            if 'generic-43/repo' in line:
                return '43'
            elif 'generic-rawhide/repo' in line:
                return 'rawhide'

        return None

    def extract_version_from_file(self, recipe_path: str, filename: str) -> Optional[str]:
        """Extract version from recipe file."""
        content = Path(recipe_path).read_text(encoding='utf-8')
        return self.extract_version(content, filename)

    def validate_recipe_content(self, recipe_path: str) -> List[str]:
        """Validate recipe content from file path."""
        content = Path(recipe_path).read_text(encoding='utf-8')
        return self.validate_recipe(content)

    def validate_recipe_semantic_from_file(self, recipe_path: str, version: str) -> List[str]:
        """Validate recipe from file path using pykickstart."""
        content = Path(recipe_path).read_text(encoding='utf-8')
        return self.validate_recipe_semantic(content, version)
