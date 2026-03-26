"""Tests for the Recipe Generator."""

import pytest
from pathlib import Path
import sys

RECIPE_GENERATOR_DIR = Path(__file__).parent.parent / 'recipe-generator'
sys.path.insert(0, str(RECIPE_GENERATOR_DIR))

from recipe_generator import RecipeGenerator


class TestRecipeGenerator:
    """Test RecipeGenerator class."""

    def setup_method(self):
        """Set up test fixtures."""
        project_root = Path(__file__).parent.parent
        self.generator = RecipeGenerator(
            project_root / 'recipe-generator' / 'recipe_templates.yaml'
        )

    def test_template_loading(self):
        """Test that templates are loaded correctly."""
        assert isinstance(self.generator.templates, dict)
        assert len(self.generator.templates) == 2
        assert 'install' in self.generator.templates
        assert 'live' in self.generator.templates

    def test_validate_template_success(self):
        """Test validation of valid templates."""
        template = self.generator.templates['install']
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
        """Test generating basic desktop recipe."""
        content = self.generator.generate_recipe('install', '43',
                                                  desktop='gnome',
                                                  storage='standard',
                                                  security='secure')
        assert '# An install recipe for desktop, server, or hypervisor' in content
        assert '%include ingredients/core/base.ks' in content
        assert '%include ingredients/desktop/gnome/packages.ks' in content
        assert '%include ingredients/repo/fedora-43-mirrors.ks' in content
        assert '%include ingredients/core/security/enabled.ks' in content

    def test_generate_virtual_desktop_encrypted(self):
        """Test generating encrypted desktop recipe."""
        content = self.generator.generate_recipe('install', 'rawhide',
                                                  desktop='gnome',
                                                  storage='encrypted',
                                                  security='secure')
        assert '%include ingredients/storage/encrypted.ks' in content

    def test_generate_virtual_desktop_labwc(self):
        """Test generating LabWC desktop recipe."""
        content = self.generator.generate_recipe('install', '43',
                                                  desktop='labwc',
                                                  storage='standard',
                                                  security='secure')
        assert '%include ingredients/desktop/labwc/config.ks' in content
        assert '%include ingredients/desktop/gnome/packages.ks' not in content

    def test_generate_virtual_desktop_devel(self):
        """Test generating development mode desktop recipe."""
        content = self.generator.generate_recipe('install', '43',
                                                  desktop='gnome',
                                                  storage='standard',
                                                  security='off')
        assert '%include ingredients/core/security/disabled.ks' in content

    def test_generate_virtual_server(self):
        """Test generating server recipe."""
        content = self.generator.generate_recipe('install', 'rawhide',
                                                  initial_setup='server',
                                                  security='secure')
        assert '# An install recipe for desktop, server, or hypervisor' in content
        assert '%include ingredients/initial-setup/server/config.ks' in content

    def test_generate_desktop_hypervisor_amd(self):
        """Test generating AMD CPU hypervisor recipe."""
        content = self.generator.generate_recipe('install', 'rawhide',
                                                  variant_type='hypervisor',
                                                  hypervisor='base',
                                                  hypervisor_type='amdcpu',
                                                  security='secure')
        assert '%include ingredients/hypervisor/amdcpu.ks' in content
        assert '%include ingredients/hypervisor/intelcpu.ks' not in content

    def test_generate_desktop_hypervisor_intel_gpu(self):
        """Test generating Intel CPU+GPU hypervisor recipe."""
        content = self.generator.generate_recipe('install', 'rawhide',
                                                  variant_type='hypervisor',
                                                  hypervisor='base',
                                                  hypervisor_type='intelcpu',
                                                  security='secure')
        assert '%include ingredients/hypervisor/intelcpu.ks' in content

    def test_generate_live_desktop(self):
        """Test generating live desktop recipe."""
        content = self.generator.generate_recipe('live', 'rawhide',
                                                  desktop='gnome',
                                                  security='secure')
        assert '# A live recipe for live-desktop or live-server' in content
        assert '%include ingredients/live/core/base.ks' in content
        assert '%include ingredients/live/core/storage.ks' in content

    def test_generate_live_server(self):
        """Test generating live server recipe."""
        content = self.generator.generate_recipe('live', 'rawhide',
                                                  security='secure')
        assert '# A live recipe for live-desktop or live-server' in content
        assert '%include ingredients/live/core/base.ks' in content

    def test_no_duplicate_includes(self):
        """Test that duplicate includes are prevented."""
        content = self.generator.generate_recipe('install', 'rawhide',
                                                  variant_type='hypervisor',
                                                  hypervisor='base',
                                                  hypervisor_type='intelcpu',
                                                  security='secure')
        includes = [line for line in content.split('\n') if line.startswith('%include')]
        paths = [line.split()[1] for line in includes]
        assert len(paths) == len(set(paths)), "Found duplicate %include entries"

    def test_missing_ingredient_detection(self):
        """Test that missing ingredients are detected."""
        content = self.generator.generate_recipe('install', '43',
                                                  desktop='gnome',
                                                  storage='standard',
                                                  security='secure')
        issues = self.generator.validate_recipe(content)
        assert issues == [], f"Found missing ingredients: {issues}"

    def test_filename_generation_standard(self):
        """Test filename generation for standard configuration."""
        filename = self.generator.generate_filename('install', '43',
                                                      desktop='gnome',
                                                      storage='standard',
                                                      security='secure')
        assert filename == 'install_43.cfg'

    def test_filename_generation_encrypted(self):
        """Test filename generation for encrypted storage."""
        filename = self.generator.generate_filename('install', 'rawhide',
                                                      desktop='gnome',
                                                      storage='encrypted',
                                                      security='secure')
        assert filename == 'install_encrypted_rawhide.cfg'

    def test_filename_generation_devel(self):
        """Test filename generation for development mode."""
        filename = self.generator.generate_filename('install', '43',
                                                      desktop='gnome',
                                                      storage='standard',
                                                      security='off')
        assert filename == 'install_devel_43.cfg'

    def test_filename_generation_hypervisor(self):
        """Test filename generation for hypervisor."""
        filename = self.generator.generate_filename('install', 'rawhide',
                                                      variant_type='hypervisor',
                                                      hypervisor='base',
                                                      hypervisor_type='intelcpu',
                                                      security='secure')
        assert filename == 'install_hypervisor_intelcpu_rawhide.cfg'

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

%end
"""
        issues = self.generator.validate_recipe_semantic(content, '43')
        assert issues == []

    def test_validate_recipe_semantic_invalid_syntax(self):
        """Test semantic validation detects invalid syntax."""
        content = "validcommand\ninvalidcommand without proper format\n%packages\n%end"
        issues = self.generator.validate_recipe_semantic(content, '43')
        assert len(issues) > 0

    def test_validate_recipe_semantic_empty(self):
        """Test semantic validation with empty content."""
        content = ""
        issues = self.generator.validate_recipe_semantic(content, '43')
        assert issues == []

    def test_filename_generation_with_guest_agents(self):
        """Test filename includes 'virtual' when guest_agents=True."""
        filename = self.generator.generate_filename('install', '43',
                                                      variant_type='desktop',
                                                      guest_agents=True)
        assert filename == 'install_virtual_desktop_43.cfg'

    def test_filename_generation_with_hardware_support(self):
        """Test filename includes 'hardware-support' when enabled."""
        filename = self.generator.generate_filename('install', '43',
                                                      variant_type='desktop',
                                                      hardware_support=True)
        assert filename == 'install_desktop_hardware-support_43.cfg'

    def test_filename_generation_with_both_modifiers(self):
        """Test filename includes both modifiers when enabled."""
        filename = self.generator.generate_filename('install', '43',
                                                      variant_type='desktop',
                                                      guest_agents=True,
                                                      hardware_support=True)
        assert filename == 'install_virtual_desktop_hardware-support_43.cfg'
