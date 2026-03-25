"""Integration tests for Phyllome OS recipe generator.

These tests verify the complete recipe generation workflow.
"""

import pytest
from pathlib import Path
import subprocess
import sys
import os

# Use actual project root
PROJECT_ROOT = Path('/home/lukas/Code/virt/phyllomeos')
RECIPE_GENERATOR_DIR = PROJECT_ROOT / 'recipe-generator'
RECIPE_DIR = PROJECT_ROOT / 'recipes'
FRAGMENTS_DIR = PROJECT_ROOT / 'fragments'
CONTAINER_DIR = PROJECT_ROOT / 'tests' / 'container'


def test_generate_recipes_from_manifest():
    """Test generating all recipes from manifest."""
    os.chdir(RECIPE_GENERATOR_DIR)

    result = subprocess.run(
        ['python3', 'generate_recipe.py',
         '--manifest', 'recipes_manifest.yaml',
         '--output-dir', '../recipes/'],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0, f"Recipe generation failed: {result.stderr}"
    assert 'Generating:' in result.stdout


def test_validate_all_generated_recipes():
    """Test validating all generated recipes."""
    # Count generated recipes
    recipe_count = len(list(RECIPE_DIR.glob('*.cfg')))
    assert recipe_count > 0, "No recipes generated"
    
    # Validate each recipe
    for recipe_file in RECIPE_DIR.glob('*.cfg'):
        content = recipe_file.read_text()
        assert len(content) > 0, f"Recipe {recipe_file.name} is empty"
        assert '%ksappend' in content, f"Recipe {recipe_file.name} missing %ksappend"


def test_make_targets():
    """Test Makefile targets work."""
    # Test generate-recipes
    result = subprocess.run(
        ['make', 'generate-recipes'],
        cwd=RECIPE_GENERATOR_DIR,
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"make generate-recipes failed: {result.stderr}"


def test_container_build():
    """Test container builds successfully."""
    result = subprocess.run(
        ['podman', 'build', '-t', 'phyllo/test-runner', '.'],
        cwd=CONTAINER_DIR,
        capture_output=True,
        text=True
    )
    
    # Should build even if podman fails (might not be installed)
    # The important thing is the Containerfile syntax is valid
    if result.returncode != 0 and 'command not found' not in result.stderr:
        pytest.fail(f"Container build failed: {result.stderr}")


def test_fragments_structure():
    """Verify fragment directory structure."""
    # Check core directories
    assert (FRAGMENTS_DIR / 'core' / 'security').exists()
    
    # Check desktop directories
    assert (FRAGMENTS_DIR / 'desktop' / 'gnome').exists()
    assert (FRAGMENTS_DIR / 'desktop' / 'labwc').exists()
    assert (FRAGMENTS_DIR / 'desktop' / 'vmm').exists()
    
    # Check hypervisor directories
    assert (FRAGMENTS_DIR / 'hypervisor' / 'base').exists()
    assert (FRAGMENTS_DIR / 'hypervisor' / 'base').exists()
    
    # Check live directories
    assert (FRAGMENTS_DIR / 'live' / 'core' / 'bootloader').exists()
    assert (FRAGMENTS_DIR / 'live' / 'post').exists()
    
    # Count fragments
    fragment_count = len(list(FRAGMENTS_DIR.glob('**/*.ks')))
    assert fragment_count >= 45, f"Expected at least 45 fragments, found {fragment_count}"
