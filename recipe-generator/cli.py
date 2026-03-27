"""CLI entry point for recipe generator.

This module handles the command-line interface for the recipe generator. It:
1. Parses command-line arguments and options
2. Selects the appropriate mode (validation, batch generation, single generation)
3. Sets up generators and validators with proper configuration
4. Orchestrates the workflow based on user input
5. Handles output and exit codes for integration with CI systems

The CLI supports three main modes:
- Single generation: Generate one recipe with specific options
- Batch generation: Generate many recipes from a manifest file
- Validation mode: Check existing recipes for errors

Exit codes:
- 0: Success
- 1: Validation errors or generation failed
- 2: Invalid arguments or missing files
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List

import yaml

from manifest import ManifestProcessor
from recipe_generator import RecipeGenerator
from validators import (
    ContentValidator,
    SemanticValidator,
    TemplateValidator,
    validate_manifest,
)


def main() -> None:
    """Main entry point for recipe generator CLI.
    
    This is the primary function that gets called when running the script.
    It handles argument parsing, mode selection, and workflow orchestration.
    
    Command-line arguments:
        --ingredients (-i): Directory containing ingredient fragments (default: parent/ingredients)
        --templates (-t): Path to templates YAML file (default: ./recipe_templates.yaml)
        
        Batch mode flags:
        --manifest (-m): Path to manifest YAML for batch generation
        --output-dir (-d): Output directory for generated recipes (default: ./recipes)
        --dry-run (-n): Show what would be generated without writing files
        
        Single generation flags:
        --type (-T): Recipe type to generate (e.g., virtual-desktop)
        --output (-o): Output file path for single generation
        
        Recipe parameters:
        --version (-v): Fedora version (43 or rawhide, default: 43)
        --desktop: Desktop environment (gnome or labwc, default: gnome)
        --storage: Storage type (standard or encrypted, default: standard)
        --security: Security mode (secure or devel, default: secure)
        --cpu: CPU optimization (generic, amdcpu, or intelcpu)
        --gpu: GPU passthrough (none or intelgpu, default: none)
        
        Validation mode:
        --validate (-V): Validate existing recipe files
        --strict: Treat warnings as errors (CI mode)
    
    Modes:
        1. Validation mode (--validate): Check recipe files without generating new ones
        2. Batch generation mode (--manifest): Generate many recipes from a manifest
        3. Single generation mode (--type): Generate one recipe with specified options
        4. Help mode: No arguments or --help shows usage information
    """
    # Set up argument parser with descriptive help text
    parser = argparse.ArgumentParser(
        description='Generate Phyllome OS kickstart recipes from templates',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # Calculate paths relative to this script's location
    # SCRIPTS_DIR points to recipe-generator/
    # PROJECT_ROOT points to phyllomeos/
    SCRIPTS_DIR = Path(__file__).resolve().parent  # noqa: N806 - Constant
    PROJECT_ROOT = SCRIPTS_DIR.parent  # noqa: N806 - Constant

    parser.add_argument('--ingredients', '-i',
                        type=Path, default=PROJECT_ROOT / 'ingredients',
                        help='Ingredients directory (default: parent/ingredients)')
    parser.add_argument('--templates', '-t',
                        type=Path, default=SCRIPTS_DIR / 'recipe_templates.yaml',
                        help='Templates YAML file (default: ./recipe_templates.yaml)')

    # Batch mode options
    parser.add_argument('--manifest', '-m',
                        type=Path, help='Manifest YAML for batch generation')
    parser.add_argument('--output-dir', '-d',
                        type=Path, default=SCRIPTS_DIR / 'recipes',
                        help='Output directory (batch generation, default: ./recipes)')
    parser.add_argument('--dry-run', '-n',
                        action='store_true',
                        help='Show what would be generated without writing files')

    # Single generation mode options
    parser.add_argument('--type', '-T',
                        help='Recipe type (e.g., virtual-desktop)')
    parser.add_argument('--output', '-o',
                        type=Path, help='Output file (single generation)')

    # Recipe customization parameters (default to safe/common values)
    parser.add_argument('--version', '-v',
                        choices=['43', 'rawhide'], default='43',
                        help='Fedora version (default: 43)')

    parser.add_argument('--desktop',
                        choices=['gnome', 'labwc'],
                        default='gnome',
                        help='Desktop environment (default: gnome)')
    parser.add_argument('--storage',
                        choices=['standard', 'encrypted'],
                        help='Storage type (default: standard)')
    parser.add_argument('--security',
                        choices=['secure', 'devel'],
                        help='Security mode (default: secure)')
    parser.add_argument('--cpu',
                        choices=['generic', 'amdcpu', 'intelcpu'],
                        help='CPU optimization')
    parser.add_argument('--gpu',
                        choices=['none', 'intelgpu'],
                        default='none',
                        help='GPU passthrough (default: none)')

    # Validation mode
    parser.add_argument('--validate', '-V',
                        nargs='+',
                        help='Validate recipe files')

    # Strict mode for CI
    parser.add_argument('--strict',
                        action='store_true',
                        help='Treat warnings as errors (CI mode)')

    # Parse arguments from command line
    args = parser.parse_args()

    # Initialize the recipe generator with loaded templates
    generator = RecipeGenerator(args.templates)

    # Initialize validators - they'll be used throughout the workflow
    template_validator = TemplateValidator(generator.project_root)
    content_validator = ContentValidator(generator.project_root)
    semantic_validator = SemanticValidator()

    # === VALIDATION MODE ===
    # If --validate is specified, skip generation and just check existing recipes
    if args.validate:
        all_issues = validate_recipes(args.validate, content_validator, semantic_validator, args.strict)
        handle_validation_results(all_issues, args.strict)
        return

    # === BATCH GENERATION MODE ===
    # If --manifest is specified, generate many recipes from a manifest file
    if args.manifest:
        generate_from_manifest(args, generator)
        return

    # === SINGLE GENERATION MODE ===
    # If --type is specified, generate one recipe with the given options
    if args.type:
        generate_single(args, generator)
        return

    # === NO MODE SPECIFIED ===
    # Show help and exit with error
    parser.print_help()
    sys.exit(1)


def validate_recipes(recipe_paths: List[str], content_validator: ContentValidator, 
                     semantic_validator: SemanticValidator, strict: bool) -> List:
    """Validate multiple recipes from file paths.
    
    This function iterates through a list of recipe file paths, validates each one
    for both content issues (duplicates, missing ingredients) and semantic issues
    (kickstart syntax errors).
    
    The validation process for each file:
    1. Read the file content
    2. Run ContentValidator to check ingredient existence and duplicates
    3. Try to extract the Fedora version from content or filename
    4. Run SemanticValidator (pykickstart parser) to check kickstart syntax
    5. Collect all issues found
    
    Args:
        recipe_paths: List of file paths to validate
        content_validator: ContentValidator instance for ingredient checks
        semantic_validator: SemanticValidator instance for kickstart parsing
        strict: If True, treat warnings as errors (exit with 1)
    
    Returns:
        List of (path, issues) tuples for files that have issues
        Example: [('recipes/gnome.cfg', ['ERROR: Missing ingredient', 'Warning: ...'])]
    """
    all_issues = []
    for recipe_path in recipe_paths:
        try:
            # Validate content - check for duplicates and missing ingredients
            content = Path(recipe_path).read_text(encoding='utf-8')
            issues = content_validator.validate(content)

            # Extract version from content or filename for semantic validation
            filename = Path(recipe_path).stem
            version = extract_version(content, filename)
            if version:
                semantic_issues = semantic_validator.validate(content, version)
                issues.extend(semantic_issues)
            else:
                # Could not determine version, can't do semantic validation
                issues.append("Warning: Could not determine version, "
                            "skipping semantic validation")

            if issues:
                # Only track files that have issues
                all_issues.append((recipe_path, issues))
        except FileNotFoundError:
            print(f"Error: Recipe not found: {recipe_path}", file=sys.stderr)
            sys.exit(2)

    return all_issues


def extract_version(content: str, filename: str) -> str | None:
    """Extract Fedora version from recipe content or filename.
    
    This function tries multiple heuristics to determine which Fedora version
    a recipe is targeting. It checks the filename first, then falls back to
    searching the content for version-specific patterns.
    
    The method checks for:
    1. Version in filename: patterns like _43_, -rawhide.cfg, _43.cfg
    2. Version in content: repository paths like 'core-fedora-repo-43'
    
    This is useful for batch operations where the version might not be
    explicitly stated but can be inferred from naming conventions or content.
    
    Args:
        content: The content of the recipe file (as a string)
        filename: Just the filename without path
    
    Returns:
        Version string ('43' or 'rawhide') if found, None otherwise
    """
    import re

    # Try to extract from filename first using regex
    # Matches patterns like _43, -43, _rawhide, -rawhide, etc.
    # The lookahead for .cfg|.yaml|$ ensures we don't match 43 in '431'
    filename_match = re.search(r'(?:_|-)(43|rawhide)(?:_|-|.cfg|.yaml|$)', filename)
    if filename_match:
        return filename_match.group(1)

    # Fall back to content inspection
    # Check for Fedora repository paths that contain version info
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


def handle_validation_results(all_issues: List, strict: bool) -> None:
    """Handle validation results and exit with appropriate code.
    
    This function formats and displays validation results to the user,
    then exits with the appropriate code based on the results and strict mode.
    
    The output format:
    - Group issues by file
    - Show errors first (separate from warnings)
    - Show summary totals at the end
    
    Exit codes:
    - 0: All files passed validation
    - 1: Any issues found (or warnings in strict mode)
    - 2: Error during processing
    
    Args:
        all_issues: List of (path, issues) tuples from validate_recipes()
        strict: If True, warnings are treated as errors
    """
    if all_issues:
        # Display issues for each file that has problems
        for path, issues in all_issues:
            print(f"\n{path}:", file=sys.stderr)
            
            # Count errors and warnings separately
            error_count = sum(1 for i in issues if 'ERROR' in i or 'error' in i.lower())
            warning_count = sum(1 for i in issues if 'Warning' in i or 'warning' in i.lower())

            # Display errors (if any)
            if error_count > 0:
                for issue in issues:
                    if 'ERROR' in issue or 'error' in issue.lower():
                        print(f"  {issue}", file=sys.stderr)

            # Display warnings (if any)
            if warning_count > 0:
                for issue in issues:
                    if 'Warning' in issue or 'warning' in issue.lower():
                        print(f"  {issue}", file=sys.stderr)

            # Handle case where no issues match expected patterns
            if error_count == 0 and warning_count == 0:
                print(f"  No issues found (file exists)", file=sys.stderr)

        # Print summary
        print(f"\nSummary:", file=sys.stderr)
        print(f"  - {len(all_issues)} recipe(s) checked", file=sys.stderr)

        # Calculate totals across all files
        total_errors = sum(len([i for i in issues if 'ERROR' in i or 'error' in i.lower()]) 
                         for _, issues in all_issues)
        total_warnings = sum(len([i for i in issues if 'Warning' in i or 'warning' in i.lower()]) 
                           for _, issues in all_issues)
        print(f"  - {total_errors} error(s), {total_warnings} warning(s)", file=sys.stderr)

        # In strict mode, warnings are treated as errors
        if strict and total_warnings > 0:
            print("\nStrict mode: Warnings treated as errors", file=sys.stderr)
            sys.exit(1)

        # Exit with error if any issues found
        if total_errors > 0 or all_issues:
            sys.exit(1)
    else:
        # All recipes validated successfully
        print("All recipes validated successfully")
        sys.exit(0)


def generate_from_manifest(args: argparse.Namespace, generator: RecipeGenerator) -> None:
    """Generate recipes in batch from a manifest file.
    
    This function handles batch generation mode. It:
    1. Loads and parses the manifest YAML file
    2. Validates the manifest structure
    3. Iterates through each recipe configuration in the manifest
    4. Expands any variants with list values (cartesian product)
    5. Generates each variant and writes to output files
    6. Optionally runs validation or dry-run checks
    
    The manifest YAML format:
        recipes:
          - name: virtual-desktop
            variants:
              - version: 43
                desktop: gnome
                storage: encrypted
              - version: ["43", "rawhide"]
                security: secure
    
    The list-valued variants (like version) get expanded into all combinations.
    
    Args:
        args: Parsed command-line arguments containing paths and settings
        generator: Pre-configured RecipeGenerator instance
    """
    manifest_path = args.manifest
    try:
        # Load manifest YAML file
        with open(manifest_path, encoding='utf-8') as f:
            manifest = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Error: Manifest file not found: {manifest_path}", file=sys.stderr)
        sys.exit(2)
    except yaml.YAMLError as e:
        print(f"Error: Invalid YAML in manifest: {e}", file=sys.stderr)
        sys.exit(2)

    # Validate manifest structure before processing
    manifest_processor = ManifestProcessor(generator.project_root)
    errors = manifest_processor.validate(manifest)
    if errors:
        print(f"Error: Invalid manifest:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        sys.exit(1)

    # Generate all recipes from the manifest
    for recipe_config in manifest.get('recipes', []):
        recipe_type = recipe_config['name']
        if recipe_type not in generator.templates:
            print(f"Error: Unknown recipe type in manifest: {recipe_type}", file=sys.stderr)
            sys.exit(1)

        # Get variants for this recipe type
        variants = recipe_config.get('variants', [])
        
        # Expand list-valued variants (e.g., version: ["43", "rawhide"])
        variants = generator.expand_variants(variants)
        
        for variant in variants:
            # Extract version and other modifiers from variant
            version = variant['version']
            modifiers = {k: v for k, v in variant.items() if k not in ['name', 'version']}
            variant_subname = variant.get('name', '')

            # Add variant name as modifier if present
            if variant_subname:
                modifiers['variant_type'] = variant_subname
                modifiers['variant_subname'] = variant_subname

            # Generate the recipe content
            content = generator.generate(recipe_type, version, **modifiers)

            # Optional validation on generated content
            if args.validate and not args.dry_run:
                issues = content_validator.validate(content)
                semantic_issues = semantic_validator.validate(content, version)
                all_issues = issues + semantic_issues
                if all_issues:
                    print(f"Validation issues for {recipe_type} {version}:", file=sys.stderr)
                    for issue in issues:
                        print(f"  - {issue}", file=sys.stderr)
                    sys.exit(1)

            # Generate output filename based on recipe parameters
            filename = generator.generate_filename(recipe_type, version, **modifiers)
            output_path = args.output_dir / filename

            # Handle dry-run mode
            if args.dry_run:
                print(f"Would generate: {output_path}")
            else:
                # Actually write the file
                print(f"Generating: {output_path}")
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(content)


def generate_single(args: argparse.Namespace, generator: RecipeGenerator) -> None:
    """Generate a single recipe with the specified parameters.
    
    This function handles single recipe generation mode. It:
    1. Constructs a modifiers dictionary from command-line arguments
    2. Only includes non-default values (e.g., only adds 'encrypted' if storage is encrypted)
    3. Generates the recipe content
    4. Optionally validates the content
    5. Outputs to a file or stdout based on arguments
    
    Command-line parameter to modifier mapping:
        --type -> recipe_type (required)
        --version -> version (43 or rawhide)
        --desktop -> desktop (gnome or labwc)
        --storage -> storage (standard or encrypted)
        --security -> security (secure or devel)
        --cpu -> cpu (generic, amdcpu, or intelcpu)
        --gpu -> gpu (none or intelgpu)
    
    Args:
        args: Parsed command-line arguments
        generator: Pre-configured RecipeGenerator instance
    """
    # Build modifiers dictionary from command-line arguments
    # Only include non-default values to keep filenames clean
    modifiers = {
        'variant_type': 'desktop',
        'desktop': args.desktop if args.desktop else None,
        'storage': args.storage if args.storage != 'standard' else None,
        'security': args.security if args.security != 'secure' else None,
        'cpu': args.cpu if args.cpu and args.cpu != 'generic' else None,
        'gpu': args.gpu if args.gpu and args.gpu != 'none' else None,
    }
    # Remove Nones from modifiers
    modifiers = {k: v for k, v in modifiers.items() if v is not None}

    # Generate the recipe
    content = generator.generate(args.type, args.version, **modifiers)

    # Optional validation
    if args.validate:
        content_validator = ContentValidator(generator.project_root)
        issues = content_validator.validate(content)
        semantic_validator = SemanticValidator()
        semantic_issues = semantic_validator.validate(content, args.version)
        all_issues = issues + semantic_issues
        if all_issues:
            print("Validation issues:", file=sys.stderr)
            for issue in issues:
                print(f"  - {issue}", file=sys.stderr)
            sys.exit(1)
        else:
            print("Validation passed")

    # Output the recipe
    if args.output:
        # Write to file
        if args.dry_run:
            print(f"Would write to: {args.output}")
        else:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Generated: {args.output}")
    else:
        # Print to stdout
        print(content)
