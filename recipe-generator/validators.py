"""Validation logic for recipes and templates."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

from pykickstart.parser import KickstartParser
from pykickstart.version import makeVersion, DEVEL


class TemplateValidator:
    """Validate template structure and fragment existence."""

    def __init__(self, project_root: Path):
        self.project_root = project_root

    def validate(self, template: Dict) -> List[str]:
        """Validate template structure and fragment existence.

        Returns a list of validation warnings (not errors).
        """
        errors = []

        # Check required keys
        required_keys = ['description', 'required']
        for key in required_keys:
            if key not in template:
                errors.append(f"Missing required key: {key}")

        # Validate required fragments exist
        for item in template.get('required', []):
            if isinstance(item, dict):
                fragment_path = list(item.values())[0]
            else:
                fragment_path = item

            full_path = self.project_root / fragment_path
            if not full_path.exists():
                errors.append(f"Required fragment not found: {fragment_path}")

        # Validate versioned fragments
        for key, fragment_path in template.get('versioned', {}).items():
            if '{version}' in fragment_path:
                # Will be resolved at generation time
                continue
            full_path = self.project_root / fragment_path
            if not full_path.exists():
                errors.append(f"Versioned fragment not found: {fragment_path}")

        # Validate conditional fragments
        conditional = template.get('conditional', {})
        for modifier, modifier_config in conditional.items():
            if isinstance(modifier_config, dict):
                for value, fragment_path in modifier_config.items():
                    if fragment_path is None:
                        continue
                    if isinstance(fragment_path, list):
                        for fp in fragment_path:
                            if fp is not None:
                                full_path = self.project_root / fp
                                if not full_path.exists():
                                    errors.append(f"Conditional fragment not found: {fp} (in list for {modifier}={value})")
                    else:
                        full_path = self.project_root / fragment_path
                        if not full_path.exists():
                            errors.append(f"Conditional fragment not found: {fragment_path} (for {modifier}={value})")

        # Validate flag fragments
        for key, fragment_path in template.get('flags', {}).items():
            if fragment_path is None:
                continue
            full_path = self.project_root / fragment_path
            if not full_path.exists():
                errors.append(f"Flag fragment not found: {fragment_path}")

        return errors


class ContentValidator:
    """Validate recipe content for fragment existence and duplicates."""

    def __init__(self, project_root: Path):
        self.project_root = project_root

    def validate(self, content: str) -> List[str]:
        """Validate recipe content.

        Returns a list of validation warnings (not errors).
        """
        issues = []
        includes = [line for line in content.split('\n') if line.startswith('%include')]

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

        # Check fragment existence
        for inc in includes:
            parts = inc.split()
            if len(parts) < 2:
                continue
            path = parts[1]
            fragment_path = self.project_root / path
            if not fragment_path.exists():
                issues.append(f"Missing fragment: {path}")

        return issues


class SemanticValidator:
    """Validate recipe using pykickstart parser."""

    def validate(self, content: str, version: str) -> List[str]:
        """Validate recipe using pykickstart parser.

        Returns a list of validation warnings (not errors).
        """
        issues = []

        try:
            ks_version_str = self._get_ksversion(version)
            if ks_version_str:
                ks_version = makeVersion(ks_version_str)
            else:
                ks_version = makeVersion(DEVEL)

            parser = KickstartParser(ks_version)
            parser.readKickstartFromString(content)
        except Exception as e:
            # Only report actual validation errors, not include resolution issues
            err_str = str(e)
            if 'Unable to open input kickstart file' not in err_str:
                issues.append(f"Validation error: {err_str}")

        return issues

    def _get_ksversion(self, version: str) -> Optional[str]:
        """Map Phyllome OS version to pykickstart version string."""
        if version == 'rawhide':
            return None
        else:
            return f'F{int(version) - 1}'


def validate_manifest(manifest: Dict) -> List[str]:
    """Validate manifest structure."""
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
        else:
            for variant in recipe_config.get('variants', []):
                if 'version' not in variant:
                    if 'name' in recipe_config:
                        errors.append(f"Recipe '{recipe_config['name']}' variant missing 'version'")
                    else:
                        errors.append("Recipe variant missing 'version'")

    return errors
