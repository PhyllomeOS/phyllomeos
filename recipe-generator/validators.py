"""Validation logic for recipes and templates.

This module provides three layers of validation for Phyllome OS kickstart recipes:

1. TemplateValidator
   - Validates the template YAML structure itself
   - Checks that all referenced ingredient files actually exist on disk
   - Validates required, versioned, conditional, optional, and flag paths

2. ContentValidator
   - Validates the generated recipe content
   - Checks for duplicate %include directives
   - Verifies all referenced ingredients exist on disk

3. SemanticValidator
   - Uses the official pykickstart library to parse recipes
   - Checks for syntax errors and invalid kickstart directives
   - Validates against Fedora version-specific kickstart rules

All validators return lists of warning/error strings. They don't raise exceptions
for minor issues; instead, they collect and report issues so callers can decide
how to handle them (warn, error, exit, etc.)

The separation allows for:
- Early detection of template issues (TemplateValidator)
- Detection of generation issues (ContentValidator)  
- Detection of actual syntax errors (SemanticValidator)
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

from pykickstart.parser import KickstartParser
from pykickstart.version import makeVersion, DEVEL


class TemplateValidator:
    """Validate template structure and fragment existence.
    
    This validator checks that:
    1. Required template keys are present (description, required)
    2. All ingredient paths referenced in the template exist on disk
    3. The template structure matches expected format
    
    It's typically used:
    - During development to catch template errors early
    - In CI/CD pipelines to validate templates before use
    - Programmatically when loading templates
    
    The validator doesn't check for semantic issues in the ingredients themselves -
    it only verifies that they exist and are properly referenced.
    """

    def __init__(self, project_root: Path):
        """Initialize the validator with project root path.
        
        Args:
            project_root: Path to the phyllomeos project root directory.
                         All ingredient paths in templates are relative to this.
        """
        self.project_root = project_root

    def validate(self, template: Dict) -> List[str]:
        """Validate template structure and fragment existence.
        
        This method performs a comprehensive check of the template dictionary:
        
        1. Required Keys Check:
           - Verifies 'description' key exists (used in header)
           - Verifies 'required' key exists (base ingredients)
        
        2. Required Ingredients Check:
           - Iterates through template['required'] list
           - Resolves each path relative to project_root
           - Checks if the file actually exists
           - Reports missing files as errors
        
        3. Versioned Ingredients Check:
           - Checks paths in template['versioned']
           - If the path contains {version}, it's deferred to generation time
           - Otherwise checks if the resolved file exists
        
        4. Conditional Ingredients Check:
           - Iterates through template['conditional']
           - For each modifier and value, checks referenced files exist
           - Handles both single paths and lists of paths
        
        5. Flag Ingredients Check:
           - Checks all paths in template['flags']
           - Flags are boolean on/off switches
        
        Args:
            template: The template dictionary to validate
                     Structure: {'description': str, 'required': [...], ...}
        
        Returns:
            List of validation error strings (empty if valid)
            Example: ['Missing required key: description', 'Required ingredient not found: ingredients/gnome.cfg']
        """
        errors = []

        # Check required keys at the template level
        required_keys = ['description', 'required']
        for key in required_keys:
            if key not in template:
                errors.append(f"Missing required key: {key}")

        # Validate required ingredients exist on disk
        for item in template.get('required', []):
            if isinstance(item, dict):
                # Dict format: {priority: path} or {condition: path}
                fragment_path = list(item.values())[0]
            else:
                # Simple string path
                fragment_path = item

            # Resolve relative path from project root
            full_path = self.project_root / fragment_path
            if not full_path.exists():
                errors.append(f"Required ingredient not found: {fragment_path}")

        # Validate versioned ingredients exist on disk
        # These are paths like 'ingredients/repo/f{version}.cfg'
        # If the path has {version}, it'll be resolved at generation time
        # Otherwise, check if it exists now
        for key, fragment_path in template.get('versioned', {}).items():
            if '{version}' in fragment_path:
                # Will be resolved at generation time
                continue
            full_path = self.project_root / fragment_path
            if not full_path.exists():
                errors.append(f"Versioned ingredient not found: {fragment_path}")

        # Validate conditional ingredients exist on disk
        # Conditional ingredients depend on modifier values
        conditional = template.get('conditional', {})
        for modifier, modifier_config in conditional.items():
            if isinstance(modifier_config, dict):
                # Dict format: {'value': 'path'} or {'value': ['path1', 'path2']}
                for value, fragment_path in modifier_config.items():
                    if fragment_path is None:
                        # None means "don't include anything for this value"
                        continue
                    if isinstance(fragment_path, list):
                        # List of paths (e.g., multiple ingredients for this value)
                        for fp in fragment_path:
                            if fp is not None:
                                full_path = self.project_root / fp
                                if not full_path.exists():
                                    errors.append(f"Conditional ingredient not found: {fp} (in list for {modifier}={value})")
                    else:
                        full_path = self.project_root / fragment_path
                        if not full_path.exists():
                            errors.append(f"Conditional ingredient not found: {fragment_path} (for {modifier}={value})")

        # Validate flag ingredients exist on disk
        # Flags are simple boolean on/off switches
        for key, fragment_path in template.get('flags', {}).items():
            if fragment_path is None:
                continue
            full_path = self.project_root / fragment_path
            if not full_path.exists():
                errors.append(f"Flag ingredient not found: {fragment_path}")

        return errors


class ContentValidator:
    """Validate recipe content for ingredient existence and duplicates.
    
    This validator checks the content of a generated recipe file:
    
    1. Duplicate Include Detection:
       - Scans for all %include directives
       - Tracks which ingredient paths have been seen
       - Reports if the same path appears multiple times
       - This prevents redundant loading and potential conflicts
    
    2. Ingredient Existence Check:
       - For each %include directive, Verifies the referenced file exists
       - Uses project_root to resolve relative paths
       - Reports missing files so generators can catch issues early
    
    The validator is designed to run on generated recipes, not templates.
    It's lighter than TemplateValidator and runs during generation to
    catch issues immediately.
    """

    def __init__(self, project_root: Path):
        """Initialize the validator with project root path.
        
        Args:
            project_root: Path to the phyllomeos project root directory.
                         All ingredient paths are relative to this.
        """
        self.project_root = project_root

    def validate(self, content: str) -> List[str]:
        """Validate recipe content for issues.
        
        This method parses the recipe content string and checks for:
        
        1. Duplicate Includes:
           - Extracts all %include directives
           - Tracks seen paths in a set
           - Reports if a path appears more than once
           - Duplicates are problematic because they slow down generation
             and can cause conflicts in the final kickstart file
        
        2. Missing Ingredients:
           - For each %include directive, checks if the file exists
           - Path is resolved relative to project_root
           - Reports missing files that would cause generation to fail
           - This catches typos in template paths before runtime
        
        The validation is "best effort" - it doesn't raise exceptions for
        minor issues but collects all problems to report them together.
        
        Args:
            content: The recipe content string to validate
                    Contains %include directives and other kickstart code
        
        Returns:
            List of validation warning strings (empty if valid)
            Example: ['Duplicate include: ingredients/gnome.cfg', 'Missing ingredient: ingredients/unknown.cfg']
        """
        issues = []
        includes = [line for line in content.split('\n') if line.startswith('%include')]

        # Check for duplicate includes
        seen = set()
        for inc in includes:
            parts = inc.split()
            if len(parts) < 2:
                # Malformed include line, skip
                continue
            path = parts[1]
            if path in seen:
                issues.append(f"Duplicate include: {path}")
            seen.add(path)

        # Check ingredient existence
        for inc in includes:
            parts = inc.split()
            if len(parts) < 2:
                continue
            path = parts[1]
            ingredient_path = self.project_root / path
            if not ingredient_path.exists():
                issues.append(f"Missing ingredient: {path}")

        return issues


class SemanticValidator:
    """Validate recipe using pykickstart parser.
    
    This is the most thorough validator - it actually parses the recipe
    as a kickstart file and checks for syntax errors and semantic issues.
    
    It uses the pykickstart library, which is the same library Anaconda uses
    to parse kickstart files. This means it catches:
    - Syntax errors in kickstart directives
    - Invalid options or values
    - Incompatible directives for the target Fedora version
    - Other structural issues
    
    The validator is lenient about include resolution issues (file not found)
    because those are expected - the actual ingredient files are included
    during the installation, not at generation time.
    
    Version Mapping:
    - '43' -> pykickstart F42 (Phyllome OS 43 is based on Fedora 42)
    - 'rawhide' -> DEVEL (development version, uses latest rules)
    - This accounts for the fact that Phyllome OS lags Fedora by one version
    """

    def validate(self, content: str, version: str) -> List[str]:
        """Validate recipe using pykickstart parser.
        
        This method attempts to parse the recipe content as a kickstart file
        using the pykickstart library. It:
        
        1. Maps Phyllome OS version to pykickstart version string
        2. Creates a KickstartParser with the appropriate version
        3. Attempts to parse the content
        4. Catches and reports any parsing errors
        
        The parser is configured to be lenient about missing includes
        (file not found errors) because those are expected - the ingredients
        are resolved at installation time, not generation time.
        
        Args:
            content: The recipe content string to validate
            version: Phyllome OS version string ('43' or 'rawhide')
                    Determines which kickstart version rules to apply
        
        Returns:
            List of validation error strings (empty if valid)
            Only reports actual validation errors, not file missing errors
        """
        issues = []

        try:
            # Get pykickstart version string
            ks_version_str = self.get_ksversion(version)
            if ks_version_str:
                # Create version-specific parser
                ks_version = makeVersion(ks_version_str)
            else:
                # Use development version for rawhide
                ks_version = makeVersion(DEVEL)

            # Parse the content
            parser = KickstartParser(ks_version)
            parser.readKickstartFromString(content)
        except Exception as e:
            # Only report actual validation errors, not include resolution issues
            err_str = str(e)
            if 'Unable to open input kickstart file' not in err_str:
                # This is a real validation error, not a missing include
                issues.append(f"Validation error: {err_str}")

        return issues

    def get_ksversion(self, version: str) -> Optional[str]:
        """Map Phyllome OS version to pykickstart version string.
        
        This helper method converts Phyllome OS version strings to the
        corresponding pykickstart version strings.
        
        Pykickstart uses Fedora version naming:
        - F42, F43, etc. for stable releases
        - DEVEL for development versions
        
        Phyllome OS version mapping:
        - Phyllome OS 43 is based on Fedora 42, so use F42
        - Phyllome OS 44 is based on Fedora 43, so use F43
        - The pattern: F(Phyllome_OS_version - 1)
        
        For rawhide, we use None which tells pykickstart to use the
        latest development version.
        
        Args:
            version: Phyllome OS version string ('43' or 'rawhide')
        
        Returns:
            Pykickstart version string ('F42', 'F43', etc.) or None for rawhide
        """
        if version == 'rawhide':
            return None
        else:
            # Phyllome OS 43 -> Fedora 42 -> F42
            return f'F{int(version) - 1}'


def validate_manifest(manifest: Dict) -> List[str]:
    """Validate manifest structure.
    
    This function validates the high-level structure of a manifest YAML file.
    It checks that the manifest has the required sections and that each recipe
    configuration has the necessary fields.
    
    The manifest structure:
        recipes:
          - name: virtual-desktop
            variants:
              - version: 43
                desktop: gnome
              - version: rawhide
                storage: encrypted
    
    Validation checks:
    1. 'recipes' key exists at top level
    2. Each recipe config has 'name' key
    3. Each recipe config has 'variants' key
    4. Each variant has 'version' key
    
    This is a schema-level validation that catches structural errors before
    trying to process the manifest. It's less detailed than template validation
    but catches the most obvious problems early.
    
    Args:
        manifest: The manifest dictionary to validate
    
    Returns:
        List of validation error strings (empty if valid)
        Example: ["Manifest missing 'recipes' key", "Recipe 'virtual-desktop' variant missing 'version'"]
    """
    errors = []

    # Check for required top-level key
    if 'recipes' not in manifest:
        errors.append("Manifest missing 'recipes' key")
        return errors  # Can't continue without recipes

    # Validate each recipe configuration
    for recipe_config in manifest.get('recipes', []):
        if 'name' not in recipe_config:
            errors.append("Recipe config missing 'name' key")
        
        if 'variants' not in recipe_config:
            # Recipe doesn't have variants, can't validate further
            errors.append(f"Recipe '{recipe_config.get('name', 'unnamed')}' "
                        "missing 'variants' key")
        else:
            # Each variant must have version
            for variant in recipe_config.get('variants', []):
                if 'version' not in variant:
                    errors.append(f"Recipe '{recipe_config['name']}' variant missing 'version'")

    return errors
