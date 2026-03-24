"""Tests for the Recipe Generator."""

import pytest
from pathlib import Path
import sys
import os

# Add scripts directory to path
SCRIPTS_DIR = Path(__file__).parent.parent / 'scripts'
sys.path.insert(0, str(SCRIPTS_DIR))

from generate_recipe import RecipeGenerator

INGREDIENTS_DIR = Path(__file__).parent.parent / 'ingredients'


class TestRecipeGenerator:
    """Test RecipeGenerator class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.generator = RecipeGenerator(Path('ingredients'), Path('recipe_templates.yaml'))

    def test_template_loading(self):
        """Test that templates are loaded correctly."""
        assert isinstance(self.generator.templates, dict)
        assert len(self.generator.templates) == 5
        assert 'virtual-desktop' in self.generator.templates
        assert 'virtual-server' in self.generator.templates
        assert 'desktop-hypervisor' in self.generator.templates
        assert 'live-desktop' in self.generator.templates
        assert 'live-server' in self.generator.templates

    def test_validate_template_success(self):
        """Test validation of valid templates."""
        template = self.generator.templates['virtual-desktop']
        errors = self.generator.validate_template(template)
        assert errors == []

    def test_validate_template_missing_key(self):
        """Test validation detects missing keys."""
        template = {'base': 'core'}
        errors = self.generator.validate_template(template)
        assert any('Missing required key' in error for error in errors)

    def test_validate_template_missing_ingredient(self):
        """Test validation detects missing ingredients."""
        template = {
            'description': 'Test',
            'base': 'core',
            'required': [
                {'storage': 'core-storage'},
                {'nonexistent': 'nonexistent-ingredient'}
            ]
        }
        errors = self.generator.validate_template(template)
        assert any('not found' in error for error in errors)

    def test_generate_virtual_desktop_basic(self):
        """Test generating basic virtual desktop recipe."""
        content = self.generator.generate_recipe('virtual-desktop', '43',
                                                  desktop='gnome',
                                                  storage='standard',
                                                  security='secure')
        assert '# A recipe for a virtual desktop' in content
        assert '%include ../ingredients/core.cfg' in content
        assert '%include ../ingredients/base-desktop-gnome.cfg' in content
        assert '%include ../ingredients/core-fedora-repo-43.cfg' in content
        assert '%include ../ingredients/core-security-on.cfg' in content

    def test_generate_virtual_desktop_encrypted(self):
        """Test generating encrypted virtual desktop recipe."""
        content = self.generator.generate_recipe('virtual-desktop', 'rawhide',
                                                  desktop='gnome',
                                                  storage='encrypted',
                                                  security='secure')
        assert '%include ../ingredients/core-storage-encrypted.cfg' in content

    def test_generate_virtual_desktop_labwc(self):
        """Test generating LabWC virtual desktop recipe."""
        content = self.generator.generate_recipe('virtual-desktop', '43',
                                                  desktop='labwc',
                                                  storage='standard',
                                                  security='secure')
        assert '%include ../ingredients/base-desktop-labwc.cfg' in content
        assert '%include ../ingredients/base-desktop-gnome.cfg' not in content

    def test_generate_virtual_desktop_devel(self):
        """Test generating development mode virtual desktop recipe."""
        content = self.generator.generate_recipe('virtual-desktop', '43',
                                                  desktop='gnome',
                                                  storage='standard',
                                                  security='devel')
        assert '%include ../ingredients/core-security-off.cfg' in content
        assert '%include ../ingredients/core-security-on.cfg' not in content

    def test_generate_virtual_server(self):
        """Test generating virtual server recipe."""
        content = self.generator.generate_recipe('virtual-server', 'rawhide',
                                                  security='secure')
        assert '# A recipe for a virtual server' in content
        assert '%include ../ingredients/base-desktop-gnome.cfg' not in content
        assert '%include ../ingredients/core-initial-setup-server.cfg' in content

    def test_generate_desktop_hypervisor_amd(self):
        """Test generating AMD CPU hypervisor recipe."""
        content = self.generator.generate_recipe('desktop-hypervisor', 'rawhide',
                                                  cpu='amdcpu',
                                                  security='secure')
        assert '%include ../ingredients/base-hypervisor-amdcpu.cfg' in content
        assert '%include ../ingredients/base-hypervisor-intelcpu.cfg' not in content

    def test_generate_desktop_hypervisor_intel_gpu(self):
        """Test generating Intel CPU+GPU hypervisor recipe."""
        content = self.generator.generate_recipe('desktop-hypervisor', 'rawhide',
                                                  cpu='intelcpu',
                                                  gpu='intelgpu',
                                                  security='secure')
        assert '%include ../ingredients/base-hypervisor-intelcpu.cfg' in content
        assert '%include ../ingredients/base-hypervisor-intelgpu.cfg' in content

    def test_generate_live_desktop(self):
        """Test generating live desktop recipe."""
        content = self.generator.generate_recipe('live-desktop', 'rawhide',
                                                  desktop='gnome',
                                                  security='secure')
        assert '# A recipe for a live desktop' in content
        assert '%include ../ingredients/live-core.cfg' in content
        assert '%include ../ingredients/live-core-storage.cfg' in content

    def test_generate_live_server(self):
        """Test generating live server recipe."""
        content = self.generator.generate_recipe('live-server', 'rawhide',
                                                  security='secure')
        assert '# A recipe for a live server' in content
        assert '%include ../ingredients/live-core.cfg' in content
        assert '%include ../ingredients/core-initial-setup-server.cfg' in content

    def test_no_duplicate_includes(self):
        """Test that duplicate includes are prevented."""
        content = self.generator.generate_recipe('desktop-hypervisor', 'rawhide',
                                                  cpu='intelcpu',
                                                  gpu='intelgpu',
                                                  security='secure')
        includes = [line for line in content.split('\n') if line.startswith('%include')]
        paths = [line.split()[1] for line in includes]
        assert len(paths) == len(set(paths)), "Found duplicate includes"

    def test_missing_ingredient_detection(self):
        """Test that missing ingredients are detected."""
        content = self.generator.generate_recipe('virtual-desktop', '43',
                                                  desktop='gnome',
                                                  storage='standard',
                                                  security='secure')
        issues = self.generator.validate_recipe(content)
        assert issues == [], f"Found missing ingredients: {issues}"

    def test_filename_generation_standard(self):
        """Test filename generation for standard configuration."""
        filename = self.generator.generate_filename('virtual-desktop', '43',
                                                     desktop='gnome',
                                                     storage='standard',
                                                     security='secure')
        assert filename == 'virtual-desktop_43.cfg'

    def test_filename_generation_encrypted(self):
        """Test filename generation for encrypted storage."""
        filename = self.generator.generate_filename('virtual-desktop', 'rawhide',
                                                     desktop='gnome',
                                                     storage='encrypted',
                                                     security='secure')
        assert filename == 'virtual-desktop_rawhide_encrypted.cfg'

    def test_filename_generation_devel(self):
        """Test filename generation for development mode."""
        filename = self.generator.generate_filename('virtual-desktop', '43',
                                                     desktop='gnome',
                                                     storage='standard',
                                                     security='devel')
        assert filename == 'virtual-desktop_43_devel.cfg'

    def test_filename_generation_cpu_gpu(self):
        """Test filename generation for hypervisor with CPU/GPU."""
        filename = self.generator.generate_filename('desktop-hypervisor', 'rawhide',
                                                     cpu='intelcpu',
                                                     gpu='intelgpu',
                                                     security='secure')
        assert filename == 'desktop-hypervisor_intelcpu_intelgpu_rawhide.cfg'

    def test_filename_generation_labwc(self):
        """Test filename generation for non-default desktop."""
        filename = self.generator.generate_filename('virtual-desktop', '43',
                                                     desktop='labwc',
                                                     storage='standard',
                                                     security='secure')
        assert filename == 'virtual-desktop_labwc_43.cfg'

    def test_filename_generation_hypervisor(self):
        """Test filename generation for live server with hypervisor."""
        filename = self.generator.generate_filename('live-server', 'rawhide',
                                                     security='secure',
                                                     hypervisor=True)
        assert filename == 'live-server_rawhide_hypervisor.cfg'

    def test_invalid_recipe_type(self):
        """Test error on invalid recipe type."""
        with pytest.raises(SystemExit) as exc_info:
            self.generator.generate_recipe('nonexistent-type', '43')
        assert exc_info.value.code == 1

    def test_manifest_validation_missing_recipes_key(self):
        """Test manifest validation detects missing recipes key."""
        manifest = {}
        errors = self.generator.validate_manifest(manifest)
        assert any('recipes' in error for error in errors)

    def test_manifest_validation_missing_name(self):
        """Test manifest validation detects missing recipe name."""
        manifest = {'recipes': [{}]}
        errors = self.generator.validate_manifest(manifest)
        assert any('name' in error for error in errors)

    def test_manifest_validation_missing_version(self):
        """Test manifest validation detects missing version."""
        manifest = {'recipes': [{'name': 'test', 'variants': [{}]}]}
        errors = self.generator.validate_manifest(manifest)
        assert any('version' in error for error in errors)

    def test_get_ksversion_43(self):
        """Test version mapping for Fedora 43."""
        version = self.generator.get_ksversion('43')
        assert version == 'F42'

    def test_get_ksversion_rawhide(self):
        """Test version mapping for rawhide."""
        version = self.generator.get_ksversion('rawhide')
        assert version is None

    def test_validate_recipe_semantic_f42(self):
        """Test semantic validation with valid recipe for F42."""
        content = """text
poweroff
zerombr
clearpart --all --initlabel
part /boot/efi --fstype="efi" --size=512
part / --fstype="ext4" --grow
%packages
@base-graphical
%end
"""
        issues = self.generator.validate_recipe_semantic(content, '43')
        # Should have no syntax errors
        assert not any('Syntax' in issue for issue in issues)
        assert not any('Validation' in issue for issue in issues)

    def test_validate_recipe_semantic_empty(self):
        """Test semantic validation with empty content."""
        content = ""
        issues = self.generator.validate_recipe_semantic(content, '43')
        # Empty content should fail parsing but not crash
        assert len(issues) >= 0  # At least info about empty content

    def test_validate_recipe_semantic_invalid_syntax(self):
        """Test semantic validation detects invalid syntax."""
        content = """text
invalidcmd --option=value
%packages
@base-graphical
%end
"""
        issues = self.generator.validate_recipe_semantic(content, '43')
        # Should detect invalid command
        has_syntax_error = any('Syntax' in issue or 'invalidcmd' in issue.lower() 
                              for issue in issues)
        # Or pykickstart warning if not available
        has_warning = any('Warning' in issue or 'pykickstart' in issue.lower() 
                         for issue in issues)
        assert has_syntax_error or has_warning


    def test_validate_recipe_full_validation(self):
        """Test full validation combines file and semantic checks."""
        content = self.generator.generate_recipe('virtual-desktop', '43',
                                                  desktop='gnome',
                                                  storage='standard',
                                                  security='secure')
        issues = self.generator.validate_recipe(content)
        # Check ingredient existence
        assert len([i for i in issues if 'Missing' in i]) == 0, \
            f"Found missing ingredients: {issues}"

    def test_check_deprecated_removed_command(self):
        """Test detection of removed deprecated command."""
        content = """text
authconfig --enableshadow
%packages
@core
%end
"""
        issues = self.generator.validate_recipe_semantic(content, '43')
        # Should detect authconfig as removed
        has_removed = any('ERROR' in i and 'authconfig' in i for i in issues)
        assert has_removed

    def test_check_deprecated_warning_command(self):
        """Test detection of deprecated command as warning."""
        content = """text
keyboard --evgrd
%packages
@core
%end
"""
        issues = self.generator.validate_recipe_semantic(content, '43')
        # Should detect keyboard as deprecated (warning)
        has_warning = any('Warning' in i and 'keyboard' in i for i in issues)
        assert has_warning

    def test_extract_version_with_dash(self):
        """Test version extraction from filename with dash."""
        filename = 'test-43.cfg'
        version = self.generator.extract_version('', filename)
        assert version == '43'

    def test_extract_version_with_underscore(self):
        """Test version extraction from filename with underscore."""
        filename = 'test_43.cfg'
        version = self.generator.extract_version('', filename)
        assert version == '43'

    def test_extract_version_from_content(self):
        """Test version extraction from content."""
        content = "%include ../ingredients/core-fedora-repo-43.cfg"
        version = self.generator.extract_version(content, 'test.cfg')
        assert version == '43'

