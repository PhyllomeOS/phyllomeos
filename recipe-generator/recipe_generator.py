"""Core recipe generation logic.

This module is the heart of the Phyllome OS kickstart recipe generation system.
It works like a sophisticated template engine that:

1. Reads template definitions from recipe_templates.yaml
2. Each template defines:
   - Required ingredients (always included, like base system components)
   - Modifiers (user choices like desktop environment, storage type)
   - Optional ingredients (included based on modifier values)
   - Versioned ingredients (Fedora version-specific paths)
   - Conditional ingredients (complex logic based on multiple factors)
   - Flags (boolean on/off switches for features)

3. When you call generate(), it:
   - Looks up the template for your recipe type (e.g., "virtual-desktop")
   - Processes all the modifier values you passed in
   - Builds a list of %include directives pointing to ingredient fragments
   - Returns a complete kickstart file with header and includes

Think of it as a "recipe assembler" - the templates are the master recipes,
modifiers are your customizations, and the output is a complete installation
script that pulls in the right ingredient fragments.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from validators import (
    TemplateValidator,
    ContentValidator,
    SemanticValidator,
    validate_manifest,
)

import yaml

# ASCII art banner displayed at the top of every generated recipe file.
# This decorative header identifies the output as a Phyllome OS kickstart recipe.
# The backslashes are escaped because they're inside a Python string.
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
    """Generate kickstart recipes from templates and modifiers.
    
    This is the core class that powers the recipe generation system. It works by:
    1. Loading template definitions from a YAML file (recipe_templates.yaml)
    2. Taking a recipe type (like "virtual-desktop") and version (like "43")
    3. Accepting optional modifiers (like desktop environment, storage type, security mode)
    4. Building a list of %include directives that reference ingredient fragments
    5. Outputting a complete kickstart file with header and include statements
    
    The templates define which ingredients are required, optional, conditional, or version-specific.
    Modifiers control which optional ingredients get included based on user preferences.
    
    Example usage:
        generator = RecipeGenerator(Path('recipe_templates.yaml'))
        recipe = generator.generate('virtual-desktop', '43', desktop='gnome', storage='encrypted')
        # Returns a string containing the complete kickstart recipe
    """

    def __init__(self, templates_file: Path):
        """Initialize RecipeGenerator.
        
        Args:
            templates_file: Path to the templates YAML file.
                           This should be the full path to recipe_templates.yaml.
        """
        self.project_root = templates_file.parent.parent
        self.templates = self._load_templates(templates_file)

    def _load_templates(self, path: Path) -> Dict:
        """Load recipe templates from YAML file.
        
        This method reads the templates YAML file and extracts the 'templates' section.
        The YAML file contains a top-level 'templates' key with all recipe type definitions.
        
        Args:
            path: Path to the templates YAML file (can be absolute or relative)
        
        Returns:
            Dictionary mapping recipe types to their template definitions.
            Example structure:
            {
                'virtual-desktop': {
                    'description': 'Virtual machine with desktop',
                    'required': ['ingredients/base.cfg', ...],
                    'modifiers': {'desktop': {...}, 'storage': {...}},
                    'optional': {...},
                    'versioned': {...},
                    'conditional': {...},
                    'flags': {...}
                },
                ...
            }
        
        Raises:
            SystemExit: If the file is not found or contains invalid YAML
        """
        try:
            if path.is_absolute():
                template_path = path
            else:
                # Resolve relative paths from project root
                template_path = self.project_root / path
            with open(template_path, encoding='utf-8') as f:
                data = yaml.safe_load(f)
            # Extract the 'templates' section - the YAML file has this as top-level key
            return data['templates']
        except FileNotFoundError:
            print(f"Error: Templates file not found: {template_path}")
            exit(2)
        except yaml.YAMLError as e:
            print(f"Error: Invalid YAML in {template_path}: {e}")
            exit(2)

    def generate(self, recipe_type: str, version: str, **modifiers) -> str:
        """Generate a complete kickstart recipe from a template with modifiers.
        
        This is the main entry point for recipe generation. It takes a recipe type
        (like "virtual-desktop"), a Fedora version, and any number of modifier options,
        then returns a complete kickstart file as a string.
        
        Args:
            recipe_type: The type of recipe to generate. Must match a key in the templates.
                        Examples: 'virtual-desktop', 'server', 'hypervisor'
            version: Fedora version string, typically '43' or 'rawhide'.
                    This affects which versioned ingredients are included.
            **modifiers: Keyword arguments for recipe customization:
                        - desktop: 'gnome' or 'labwc'
                        - storage: 'standard' or 'encrypted'
                        - security: 'secure' or 'devel'
                        - cpu: 'generic', 'amdcpu', or 'intelcpu'
                        - gpu: 'none' or 'intelgpu'
                        - guest_agents: True/False for virtualization tools
                        - And many others...
        
        Returns:
            A string containing the complete kickstart recipe, including:
            - ASCII art header
            - Description comment
            - %include directives for all required and selected ingredients
            
        Raises:
            SystemExit: If the recipe_type is not found in templates
        """
        if recipe_type not in self.templates:
            print(f"Error: Unknown recipe type: {recipe_type}")
            exit(1)

        template = self.templates[recipe_type]

        # Build the output in two parts:
        # 1. Header with ASCII art and description
        # 2. All the %include lines for ingredients
        lines = self._build_header(template['description'])
        lines.extend(self._build_includes(template, version, modifiers))

        # Join all lines with newlines to create the final recipe string
        return '\n'.join(lines)
    
    generate_recipe = generate  # Compatibility alias - old code may use this name

    def _build_header(self, description: str) -> List[str]:
        """Build the ASCII art header and description for the recipe.
        
        Creates the decorative banner that appears at the top of every generated
        kickstart file. This helps identify the file as a Phyllome OS recipe and
        describes what type of system it will install.
        
        Args:
            description: Human-readable description of the recipe type
                        (e.g., "Virtual desktop environment")
        
        Returns:
            List of strings representing the header lines, including:
            - The ASCII art banner (from HEADER_ASCII_ART constant)
            - A comment line with the recipe description
            - An empty line to separate header from content
        """
        header = HEADER_ASCII_ART.copy()
        header.append(f"# {description}")
        header.append("")
        return header

    def _build_includes(self, template: Dict, version: str, modifiers: Dict) -> List[str]:
        """Build %include lines from template and modifiers.
        
        This is the most complex method in the class - it's the core logic that
        determines which ingredient fragments get included in the final recipe.
        
        The method processes six different types of ingredient sources:
        
        1. REQUIRED: Always included, no conditions
           Example: base system packages, partition layout
        
        2. MODIFIERS: User-specified options that map to ingredient paths
           Example: desktop='gnome' → ingredients/desktops/gnome.cfg
        
        3. OPTIONAL: Included only if the modifier is present
           Example: gpu='intelgpu' → ingredients/gpu/intel.cfg
        
        4. VERSIONED: Paths with {version} placeholder substituted
           Example: ingredients/repo/f{version}.cfg → ingredients/repo/f43.cfg
        
        5. CONDITIONAL: Complex logic based on modifier values
           Example: If security='devel', include development tools
        
        6. FLAGS: Boolean on/off switches
           Example: hardware_support=True → ingredients/hardware-detection.cfg
        
        The 'seen' set prevents duplicate includes if multiple paths reference
        the same ingredient.
        
        Args:
            template: The template dictionary for this recipe type
            version: Fedora version string for versioned paths
            modifiers: Dictionary of user-specified options
        
        Returns:
            List of %include directive strings, one per ingredient
        """
        includes = []
        seen = set()  # Track which ingredients we've already added

        # Add version to modifiers so templates can reference it
        modifiers = modifiers.copy()
        modifiers['version'] = version

        # === 1. REQUIRED INGREDIENTS ===
        # These are always included, regardless of user options
        # Example: base system, bootloader, partition scheme
        for item in template.get('required', []):
            if isinstance(item, dict):
                # Dict format allows conditional logic within required
                fragment_path = list(item.values())[0]
            else:
                # Simple string path
                fragment_path = item

            if fragment_path not in seen:
                includes.append(f"%include {fragment_path}")
                seen.add(fragment_path)

        # === 2. MODIFIER INGREDIENTS ===
        # Process user-specified options like desktop, storage, security
        for mod_key, mod_value in modifiers.items():
            # Normalize key: convert underscores to hyphens for template lookup
            # This allows Python-style snake_case (guest_agents) to match
            # YAML-style kebab-case (guest-agents)
            mod_key_normalized = mod_key.replace("_", "-")
            if mod_key_normalized in template.get("modifiers", {}):
                mod_key_to_use = mod_key_normalized
            elif mod_key in template.get("modifiers", {}):
                mod_key_to_use = mod_key
            else:
                # This modifier doesn't have a mapping in the template, skip it
                continue
            mod_config = template["modifiers"][mod_key_to_use]
            
            # Handle nested dict modifiers with string values
            # Example: mod_config = {'gnome': 'ingredients/gnome.cfg', 'labwc': 'ingredients/labwc.cfg'}
            #          mod_value = 'gnome'
            # Result: include ingredients/gnome.cfg
            if isinstance(mod_config, dict) and isinstance(mod_value, str):
                if mod_value in mod_config:
                    fragment_path = mod_config[mod_value]
                    if isinstance(fragment_path, list):
                        # Some modifiers map to multiple ingredients
                        for fp in fragment_path:
                            if fp is not None and fp not in seen:
                                includes.append(f"%include {fp}")
                                seen.add(fp)
                    elif fragment_path and fragment_path not in seen:
                        includes.append(f"%include {fragment_path}")
                        seen.add(fragment_path)
            
            # Handle list modifiers
            # Example: User passes multiple values like hypervisor_type=['kvm', 'xen']
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

        # === 3. OPTIONAL INGREDIENTS ===
        # Included based on modifier presence and value
        # More flexible than modifiers - can handle complex nested structures
        for opt_key, opt_config in template.get("optional", {}).items():
            if opt_key in modifiers:
                value = modifiers[opt_key]
                
                # Case 1: opt_config is nested dict, value is string/int
                # Example: opt_config = {'gnome': 'ingredients/gnome.cfg'}
                #          value = 'gnome'
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
                # Example: value = {'kvm': True, 'xen': False}
                # Include ingredients for keys that are present
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
                
                # Case 3: opt_config is nested dict, value is boolean True
                # Include ALL options when value is True
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
                
                # Case 4: opt_config is list, value is boolean True
                # Include all items in the list
                elif isinstance(opt_config, list) and value is True:
                    for fragment_path in opt_config:
                        if fragment_path is not None and fragment_path not in seen:
                            includes.append(f"%include {fragment_path}")
                            seen.add(fragment_path)

        # === 4. VERSIONED INGREDIENTS ===
        # Paths that change based on Fedora version
        # Example: 'repo': 'ingredients/repo/f{version}.cfg'
        # Becomes: ingredients/repo/f43.cfg or ingredients/repo/frawhide.cfg
        versioned = template.get('versioned', {})
        for fragment_path in versioned.values():
            # Substitute {version} placeholder with actual version
            resolved_path = fragment_path.format(version=version)
            if resolved_path not in seen:
                includes.append(f"%include {resolved_path}")
                seen.add(resolved_path)

        # === 5. CONDITIONAL INGREDIENTS ===
        # Similar to optional, but with different template structure
        # Used for more complex conditional logic
        conditional = template.get('conditional', {})
        for mod_key, mod_config in conditional.items():
            # Support both hyphenated and underscored key names
            if mod_key.replace('-', '_') in modifiers:
                value = modifiers[mod_key.replace('-', '_')]
            elif mod_key in modifiers:
                value = modifiers[mod_key]
            else:
                # This modifier wasn't provided, skip
                continue

            # Same four cases as optional section above
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

        # === 6. FLAG INGREDIENTS ===
        # Simple boolean on/off switches
        # Example: hardware_support=True → include hardware detection
        # Only includes when value is exactly True (not False or None)
        for mod_key, mod_value in modifiers.items():
            mod_key_normalized = mod_key.replace('_', '-')
            if mod_key_normalized in template.get('flags', {}):
                fragment_path = template['flags'][mod_key_normalized]
                if mod_value is True and fragment_path not in seen:
                    includes.append(f"%include {fragment_path}")
                    seen.add(fragment_path)

        return includes

    def _get_modifier(self, modifiers: dict, key: str, default=None):
        """Get modifier value, checking both hyphenated and underscored versions.
        
        This helper method handles the naming convention mismatch between:
        - Python code: uses snake_case (e.g., guest_agents)
        - YAML templates: use kebab-case (e.g., guest-agents)
        
        It tries both versions so users can pass modifiers using either convention.
        
        Args:
            modifiers: Dictionary of modifier values
            key: The key to look up (will try both this and the hyphenated version)
            default: Value to return if key is not found
        
        Returns:
            The modifier value if found, otherwise the default
        """
        if key in modifiers:
            return modifiers[key]
        alt_key = key.replace('_', '-')
        if alt_key in modifiers:
            return modifiers[alt_key]
        return default

    def generate_filename(self, recipe_type: str, version: str, **modifiers) -> str:
        """Generate recipe filename from parameters.
        
        Creates a descriptive filename that encodes the recipe's configuration.
        This allows users to identify what a recipe does just from its name.
        
        Filename format:
        {recipe_type}-{guest_type}-{variant}-{desktop}-{security}-{storage}-{version}.cfg
        
        Examples:
        - virtual-desktop_gnome_43.cfg
        - server_encrypted_43.cfg
        - hypervisor_kvm_devel_43.cfg
        
        The method only adds suffixes for non-default values:
        - GNOME is default → only add if different (labwc)
        - secure is default → only add if devel
        - standard is default → only add if encrypted
        
        Args:
            recipe_type: Base recipe type (e.g., 'virtual-desktop')
            version: Fedora version (e.g., '43' or 'rawhide')
            **modifiers: All the modifier values that affect the recipe
        
        Returns:
            Filename string ending in .cfg
        """
        # Extract variant subname if present
        # Used to distinguish between desktop/server/hypervisor variants
        variant_subname = modifiers.get('variant_subname', '')
        if not variant_subname:
            variant_subname = modifiers.get('variant_type', '')

        # Build base parts - start with recipe type
        parts = [recipe_type.replace('_', '-')]

        # Add guest_agents suffix (for both True and False)
        # Distinguishes between virtual machines and bare metal installs
        guest_agents = self._get_modifier(modifiers, 'guest_agents')
        if guest_agents is True:
            parts.append('virtual')
        elif guest_agents is False:
            parts.append('bare-metal')

        # Add variant_subname for install variants
        # Only include recognized variant types
        if variant_subname and variant_subname in ['desktop', 'server', 'hypervisor', 'hypervisor-desktop']:
            parts.append(variant_subname)

        # Add hypervisor_type suffix
        # For hypervisors, include the type (kvm, xen, etc.)
        if modifiers.get('hypervisor_type'):
            ht = modifiers['hypervisor_type']
            if isinstance(ht, list):
                # Multiple hypervisor types
                for h in ht:
                    if h:
                        parts.append(h)
            elif ht:
                # Single hypervisor type
                parts.append(ht)

        # Add desktop (non-GNOME only, since GNOME is default)
        # GNOME is the default desktop, so we only note alternatives
        desktop = self._get_modifier(modifiers, 'desktop')
        if desktop and desktop != 'gnome':
            parts.append(desktop)

        # Add security suffix (devel only, since secure is default)
        # Security defaults to 'secure', so only 'devel' gets noted
        security = self._get_modifier(modifiers, 'security')
        if security == 'off':
            parts.append('devel')

        # Add storage suffix (encrypted only, since standard is default)
        # Standard storage is default, encrypted gets noted
        storage = self._get_modifier(modifiers, 'storage')
        if storage == 'encrypted':
            parts.append('encrypted')

        # Add hardware_support suffix (for True only)
        # Hardware support detection is optional
        hardware_support = self._get_modifier(modifiers, 'hardware_support')
        if hardware_support is True:
            parts.append('hw')

        # Add initial_setup suffix (non-server values)
        # Server is default, other setup types get noted
        initial_setup = self._get_modifier(modifiers, 'initial_setup')
        if initial_setup and initial_setup != 'server':
            parts.append(f'{initial_setup}-setup')

        # Add bootloader suffix (systemd-boot only)
        # Default bootloader doesn't get noted
        bootloader = self._get_modifier(modifiers, 'bootloader')
        if bootloader == 'systemd-boot':
            parts.append('systemd-boot')

        # Add version - always included
        parts.append(str(version))

        # Join all parts with underscores and add .cfg extension
        return '_'.join(parts) + '.cfg'

    def expand_variants(self, variants: List[Dict]) -> List[Dict]:
        """Expand variants with list values into individual variants.
        
        This method enables batch generation by converting compact manifest
        entries with list values into all possible combinations.
        
        Example input:
            [
                {
                    'version': ['43', 'rawhide'],
                    'storage': ['standard', 'encrypted'],
                    'desktop': 'gnome'
                }
            ]
        
        Example output (cartesian product = 2×2×1 = 4 variants):
            [
                {'version': '43', 'storage': 'standard', 'desktop': 'gnome'},
                {'version': '43', 'storage': 'encrypted', 'desktop': 'gnome'},
                {'version': 'rawhide', 'storage': 'standard', 'desktop': 'gnome'},
                {'version': 'rawhide', 'storage': 'encrypted', 'desktop': 'gnome'}
            ]
        
        This uses itertools.product to generate the cartesian product of all
        list-valued keys, while preserving scalar values across all combinations.
        
        Args:
            variants: List of variant dictionaries, where some values may be lists
        
        Returns:
            Expanded list where each variant has only scalar (non-list) values
        """
        from itertools import product as itertools_product

        expanded = []

        for variant in variants:
            # Separate list-valued keys from scalar keys
            list_keys = {}
            scalar_keys = {}

            for key, value in variant.items():
                if isinstance(value, list):
                    list_keys[key] = value
                else:
                    scalar_keys[key] = value

            if not list_keys:
                # No lists to expand, keep as-is
                expanded.append(variant)
                continue

            # Get cartesian product of all list values
            keys = list(list_keys.keys())
            values_product = itertools_product(*[list_keys[k] for k in keys])

            # Create a new variant for each combination
            for combo in values_product:
                new_variant = scalar_keys.copy()
                for i, key in enumerate(keys):
                    new_variant[key] = combo[i]
                expanded.append(new_variant)

        return expanded

    # === VALIDATION METHODS ===
    # These are convenience wrappers that delegate to the validators module.
    # They provide a unified API so callers can validate through the generator.

    def validate_template(self, template: Dict) -> List[str]:
        """Validate template structure and fragment existence.
        
        Checks that:
        - Required keys are present (description, required)
        - All referenced ingredient files actually exist on disk
        - Versioned, conditional, and flag paths are valid
        
        Args:
            template: Template dictionary to validate
        
        Returns:
            List of validation error strings (empty if valid)
        """
        validator = TemplateValidator(self.project_root)
        return validator.validate(template)

    def validate_manifest(self, manifest: Dict) -> List[str]:
        """Validate manifest structure.
        
        Checks that the manifest has the required 'recipes' key and that
        each recipe has required fields (name, variants with version).
        
        Args:
            manifest: Manifest dictionary to validate
        
        Returns:
            List of validation error strings (empty if valid)
        """
        return validate_manifest(manifest)

    def validate_recipe(self, content: str) -> List[str]:
        """Validate recipe content.
        
        Checks that:
        - No duplicate %include directives
        - All referenced ingredient files exist
        
        Args:
            content: Recipe content string to validate
        
        Returns:
            List of validation error strings (empty if valid)
        """
        validator = ContentValidator(self.project_root)
        return validator.validate(content)

    def validate_recipe_semantic(self, content: str, version: str) -> List[str]:
        """Validate recipe using pykickstart parser.
        
        Uses the official pykickstart library to parse the recipe and check
        for syntax errors, invalid directives, or semantic issues.
        
        Args:
            content: Recipe content string to validate
            version: Fedora version for version-specific validation rules
        
        Returns:
            List of validation error strings (empty if valid)
        """
        validator = SemanticValidator()
        return validator.validate(content, version)

    def get_ksversion(self, version: str) -> Optional[str]:
        """Map Phyllome OS version to pykickstart version string.
        
        Pykickstart uses Fedora version naming (F42, F43, etc.).
        This method converts Phyllome OS versions to the corresponding
        kickstart version string.
        
        Args:
            version: Phyllome OS version (e.g., '43' or 'rawhide')
        
        Returns:
            Pykickstart version string (e.g., 'F42' for version 43)
            or None for rawhide (uses latest development version)
        """
        return SemanticValidator().get_ksversion(version)

    def extract_version(self, content: str, filename: str) -> Optional[str]:
        """Extract Fedora version from recipe content or filename.
        
        Uses multiple heuristics to determine which Fedora version a recipe
        targets:
        1. Check filename for version patterns (e.g., _43_, -rawhide.cfg)
        2. Check content for version-specific repository paths
        
        Args:
            content: Recipe content string
            filename: Recipe filename
        
        Returns:
            Version string ('43' or 'rawhide') or None if undetermined
        """
        import re

        # Try to extract from filename first
        filename_match = re.search(r'(?:_|-)(43|rawhide)(?:_|-|.cfg|.yaml|$)', filename)
        if filename_match:
            return filename_match.group(1)

        # Fall back to content inspection
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
        """Extract version from recipe file.
        
        Convenience wrapper that reads the file and delegates to extract_version.
        
        Args:
            recipe_path: Path to the recipe file
            filename: Filename (used for pattern matching)
        
        Returns:
            Version string or None
        """
        content = Path(recipe_path).read_text(encoding='utf-8')
        return self.extract_version(content, filename)

    def validate_recipe_content(self, recipe_path: str) -> List[str]:
        """Validate recipe content from file path.
        
        Reads a recipe file and validates its content for ingredient existence
        and duplicate includes.
        
        Args:
            recipe_path: Path to the recipe file
        
        Returns:
            List of validation error strings
        """
        content = Path(recipe_path).read_text(encoding='utf-8')
        return self.validate_recipe(content)

    def validate_recipe_semantic_from_file(self, recipe_path: str, version: str) -> List[str]:
        """Validate recipe from file path using pykickstart.
        
        Reads a recipe file and validates it with the pykickstart parser.
        
        Args:
            recipe_path: Path to the recipe file
            version: Fedora version for validation rules
        
        Returns:
            List of validation error strings
        """
        content = Path(recipe_path).read_text(encoding='utf-8')
        return self.validate_recipe_semantic(content, version)
