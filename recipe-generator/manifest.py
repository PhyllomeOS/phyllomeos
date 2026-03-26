"""Manifest loading and variant expansion."""

from __future__ import annotations

from itertools import product
from pathlib import Path
from typing import Dict, List

import yaml


class ManifestProcessor:
    """Load and process recipe manifests."""

    def __init__(self, project_root: Path):
        self.project_root = project_root

    def load(self, path: Path) -> Dict:
        """Load and parse manifest YAML file."""
        with open(path, encoding='utf-8') as f:
            return yaml.safe_load(f)

    def validate(self, manifest: Dict) -> List[str]:
        """Validate manifest structure.

        Returns a list of validation warnings (not errors).
        """
        errors = []

        if 'recipes' not in manifest:
            errors.append("Manifest missing 'recipes' key")
            return errors

        for recipe_config in manifest.get('recipes', []):
            if 'name' not in recipe_config:
                errors.append("Recipe config missing 'name' key")
            if 'variants' not in recipe_config:
                errors.append(f"Recipe '{recipe_config.get('name', 'unnamed')}' "
                            "missing 'variants' key")

        return errors

    def expand_variants(self, variants: List[Dict]) -> List[Dict]:
        """Expand variants with list values into individual variants.

        Converts variants like:
            - version: ["43", "rawhide"]
            - storage: ["standard", "encrypted"]

        Into cartesian product of all combinations.
        """
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
