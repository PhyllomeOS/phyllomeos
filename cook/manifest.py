"""Manifest loading and variant expansion.

This module provides functionality for processing manifest YAML files, which
are used in batch recipe generation mode. It has two main responsibilities:

1. Loading and Parsing Manifests
   - Reads YAML files containing recipe configurations
   - Validates basic structure of the manifest

2. Variant Expansion
   - Converts compact manifest entries with list values into individual variants
   - Uses cartesian product to generate all combinations
   - Enables generating many recipes from a single manifest entry

Manifest Example:
    recipes:
      - name: desktop
        variants:
          - version: 43
            desktop: gnome
            storage: encrypted
          - version: ["43", "rawhide"]
            storage: ["standard", "encrypted"]
    
    The above would generate 3 recipes (1 desktop + 2 rawhide variants).

With the universal template (proteus), recipes are generated using a single
template that supports all system types. The 'name' field is purely for
organization and doesn't affect the generated filenames.

The key insight is that list values in variants represent "multiple values for
this field", and we want to generate one recipe for each combination. This is
the classic cartesian product problem.
"""

from __future__ import annotations

from itertools import product
from pathlib import Path
from typing import Dict, List

import yaml


class ManifestProcessor:
    """Load and process recipe manifests.
    
    This class handles the loading and processing of manifest YAML files.
    A manifest is a YAML file that defines which recipes to generate and
    what variations (variants) of each recipe to create.
    
    Key features:
    - Loads and parses YAML manifest files
    - Validates manifest structure (schema-level checks)
    - Expands variants with list values into all combinations
    
    The variant expansion is particularly useful for generating multiple
    versions (e.g., both Fedora 43 and rawhide) or multiple configurations
    (e.g., both standard and encrypted storage) in a compact format.
    """

    def __init__(self, project_root: Path):
        """Initialize the processor with project root path.
        
        Args:
            project_root: Path to the phyllomeos project root directory.
                         Not currently used but available for future enhancements.
        """
        self.project_root = project_root

    def load(self, path: Path) -> Dict:
        """Load and parse manifest YAML file.
        
        This method reads a YAML file from disk and parses it into a Python
        dictionary. It's a simple wrapper around yaml.safe_load that provides
        error handling and a consistent interface.
        
        Args:
            path: Path to the manifest YAML file
        
        Returns:
            Parsed manifest as a dictionary
        
        Raises:
            FileNotFoundError: If the file doesn't exist
            yaml.YAMLError: If the file contains invalid YAML
        """
        with open(path, encoding='utf-8') as f:
            return yaml.safe_load(f)

    def validate(self, manifest: Dict) -> List[str]:
        """Validate manifest structure.
        
        This method performs schema-level validation of a manifest dictionary.
        It checks that:
        1. The top-level 'recipes' key exists
        2. Each recipe configuration has a 'name' field (for organization only)
        3. Each recipe configuration has a 'variants' field
        4. Each variant has a 'version' field
        5. No 'recipe_type' field exists (old format, removed with universal template)
        
        This is a basic structural check that catches obvious errors before
        trying to process the manifest. It doesn't validate the content of
        individual recipes (that's done by RecipeGenerator and validators).
        
        Args:
            manifest: The manifest dictionary to validate
        
        Returns:
            List of validation error strings (empty if valid)
        """
        errors = []

        # Check for required top-level key
        if 'recipes' not in manifest:
            errors.append("Manifest missing 'recipes' key")
            return errors  # Can't proceed without recipes

        # Validate each recipe configuration
        for recipe_config in manifest.get('recipes', []):
            if 'name' not in recipe_config:
                errors.append("Recipe config missing 'name' key")
            if 'variants' not in recipe_config:
                errors.append(f"Recipe '{recipe_config.get('name', 'unnamed')}' "
                            "missing 'variants' key")
            
            # Check for old recipe_type field (which is no longer used)
            if 'recipe_type' in recipe_config:
                errors.append(f"Recipe '{recipe_config.get('name', 'unnamed')}' "
                            "has 'recipe_type' field which is no longer used with universal template")

        return errors

    def expand_variants(self, variants: List[Dict]) -> List[Dict]:
        """Expand variants with list values into individual variants.
        
        This is the core functionality of the manifest processor. It converts
        a compact representation with list values into a complete list of
        individual variants by generating the cartesian product.
        
        Example Input:
            [
                {
                    'version': ['43', 'rawhide'],
                    'storage': ['standard', 'encrypted'],
                    'desktop': 'gnome'
                },
                {
                    'version': '43',
                    'security': 'devel'
                }
            ]
        
        Example Output:
            [
                {'version': '43', 'storage': 'standard', 'desktop': 'gnome'},
                {'version': '43', 'storage': 'encrypted', 'desktop': 'gnome'},
                {'version': 'rawhide', 'storage': 'standard', 'desktop': 'gnome'},
                {'version': 'rawhide', 'storage': 'encrypted', 'desktop': 'gnome'},
                {'version': '43', 'security': 'devel'}
            ]
        
        How it works:
        1. For each variant dictionary, separate list-valued keys from scalar keys
        2. If there are no lists, keep the variant as-is
        3. If there are lists, generate the cartesian product of all list values
        4. For each combination, create a new variant with scalar values preserved
        5. Return the complete list of expanded variants
        
        This enables generating many recipes from a single compact manifest entry,
        making it easy to generate variations across multiple dimensions.
        
        Args:
            variants: List of variant dictionaries, where some values may be lists
        
        Returns:
            Expanded list where each variant has only scalar (non-list) values
        """
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
                # No lists to expand, keep variant as-is
                expanded.append(variant)
                continue

            # Get the cartesian product of all list values
            keys = list(list_keys.keys())
            values_product = product(*[list_keys[k] for k in keys])

            # Create a new variant for each combination
            for combo in values_product:
                new_variant = scalar_keys.copy()
                for i, key in enumerate(keys):
                    new_variant[key] = combo[i]
                expanded.append(new_variant)

        return expanded
