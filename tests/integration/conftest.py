"""Pytest fixtures and shared utilities for Phyllome OS integration tests."""

import pytest
from pathlib import Path
import sys

# Find project root (3 levels up from integration tests)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS_DIR = PROJECT_ROOT / 'recipe-generator'
sys.path.insert(0, str(SCRIPTS_DIR))


@pytest.fixture
def generator():
    """Create RecipeGenerator instance."""
    from recipe_generator import RecipeGenerator
    
    templates_file = PROJECT_ROOT / 'recipe-generator' / 'recipe_templates.yaml'
    
    return RecipeGenerator(templates_file)


@pytest.fixture
def project_root():
    """Return project root directory."""
    return PROJECT_ROOT


@pytest.fixture
def fragments_dir(project_root):
    """Return fragments directory."""
    return project_root / 'fragments'


@pytest.fixture
def recipes_dir(project_root):
    """Return recipes directory."""
    return project_root / 'recipes'


@pytest.fixture
def fragments(fragments_dir):
    """List all .ks fragment files."""
    return list(fragments_dir.glob('**/*.ks'))


@pytest.fixture
def expected_recipes_dir(project_root):
    """Return expected recipes directory for golden masters."""
    return project_root / 'tests' / 'fixtures' / 'expected_recipes'
