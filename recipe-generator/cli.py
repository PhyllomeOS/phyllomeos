"""CLI entry point for recipe generator."""

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
    """Main entry point for recipe generator CLI."""
    parser = argparse.ArgumentParser(
        description='Generate Phyllome OS kickstart recipes from templates',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # Global options
    SCRIPTS_DIR = Path(__file__).resolve().parent  # noqa: N806 - Constant
    PROJECT_ROOT = SCRIPTS_DIR.parent  # noqa: N806 - Constant

    parser.add_argument('--ingredients', '-i',
                        type=Path, default=PROJECT_ROOT / 'ingredients',
                        help='Ingredients directory (default: parent/ingredients)')
    parser.add_argument('--templates', '-t',
                        type=Path, default=SCRIPTS_DIR / 'recipe_templates.yaml',
                        help='Templates YAML file (default: ./recipe_templates.yaml)')

    # Batch mode
    parser.add_argument('--manifest', '-m',
                        type=Path, help='Manifest YAML for batch generation')
    parser.add_argument('--output-dir', '-d',
                        type=Path, default=SCRIPTS_DIR / 'recipes',
                        help='Output directory (batch generation, default: ./recipes)')
    parser.add_argument('--dry-run', '-n',
                        action='store_true',
                        help='Show what would be generated without writing files')

    # Single generation mode
    parser.add_argument('--type', '-T',
                        help='Recipe type (e.g., virtual-desktop)')
    parser.add_argument('--output', '-o',
                        type=Path, help='Output file (single generation)')

    # Recipe parameters
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

    args = parser.parse_args()

    # Initialize generator
    generator = RecipeGenerator(args.templates)

    # Initialize validators
    template_validator = TemplateValidator(generator.project_root)
    content_validator = ContentValidator(generator.project_root)
    semantic_validator = SemanticValidator()

    # Validation mode
    if args.validate:
        all_issues = validate_recipes(args.validate, content_validator, semantic_validator, args.strict)
        handle_validation_results(all_issues, args.strict)
        return

    # Batch generation mode
    if args.manifest:
        generate_from_manifest(args, generator)
        return

    # Single generation mode
    if args.type:
        generate_single(args, generator)
        return

    # No mode specified, show help
    parser.print_help()
    sys.exit(1)


def validate_recipes(recipe_paths: List[str], content_validator: ContentValidator, 
                     semantic_validator: SemanticValidator, strict: bool) -> List:
    """Validate multiple recipes."""
    all_issues = []
    for recipe_path in recipe_paths:
        try:
            # Validate content
            content = Path(recipe_path).read_text(encoding='utf-8')
            issues = content_validator.validate(content)

            # Extract version and validate semantically
            filename = Path(recipe_path).stem
            version = extract_version(content, filename)
            if version:
                semantic_issues = semantic_validator.validate(content, version)
                issues.extend(semantic_issues)
            else:
                issues.append("Warning: Could not determine version, "
                            "skipping semantic validation")

            if issues:
                all_issues.append((recipe_path, issues))
        except FileNotFoundError:
            print(f"Error: Recipe not found: {recipe_path}", file=sys.stderr)
            sys.exit(2)

    return all_issues


def extract_version(content: str, filename: str) -> str | None:
    """Extract Fedora version from recipe content or filename."""
    import re

    filename_match = re.search(r'(?:_|-)(43|rawhide)(?:_|-|.cfg|.yaml|$)', filename)
    if filename_match:
        return filename_match.group(1)

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
    """Handle validation results and exit with appropriate code."""
    if all_issues:
        for path, issues in all_issues:
            print(f"\n{path}:", file=sys.stderr)
            error_count = sum(1 for i in issues if 'ERROR' in i or 'error' in i.lower())
            warning_count = sum(1 for i in issues if 'Warning' in i or 'warning' in i.lower())

            if error_count > 0:
                for issue in issues:
                    if 'ERROR' in issue or 'error' in issue.lower():
                        print(f"  {issue}", file=sys.stderr)

            if warning_count > 0:
                for issue in issues:
                    if 'Warning' in issue or 'warning' in issue.lower():
                        print(f"  {issue}", file=sys.stderr)

            if error_count == 0 and warning_count == 0:
                print(f"  No issues found (file exists)", file=sys.stderr)

        print(f"\nSummary:", file=sys.stderr)
        print(f"  - {len(all_issues)} recipe(s) checked", file=sys.stderr)

        total_errors = sum(len([i for i in issues if 'ERROR' in i or 'error' in i.lower()]) 
                         for _, issues in all_issues)
        total_warnings = sum(len([i for i in issues if 'Warning' in i or 'warning' in i.lower()]) 
                           for _, issues in all_issues)
        print(f"  - {total_errors} error(s), {total_warnings} warning(s)", file=sys.stderr)

        if strict and total_warnings > 0:
            print("\nStrict mode: Warnings treated as errors", file=sys.stderr)
            sys.exit(1)

        if total_errors > 0:
            sys.exit(1)
        if all_issues:
            sys.exit(1)
    else:
        print("All recipes validated successfully")
        sys.exit(0)


def generate_from_manifest(args: argparse.Namespace, generator: RecipeGenerator) -> None:
    """Generate recipes from manifest."""
    manifest_path = args.manifest
    try:
        with open(manifest_path, encoding='utf-8') as f:
            manifest = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Error: Manifest file not found: {manifest_path}", file=sys.stderr)
        sys.exit(2)
    except yaml.YAMLError as e:
        print(f"Error: Invalid YAML in manifest: {e}", file=sys.stderr)
        sys.exit(2)

    # Validate manifest
    manifest_processor = ManifestProcessor(generator.project_root)
    errors = manifest_processor.validate(manifest)
    if errors:
        print(f"Error: Invalid manifest:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        sys.exit(1)

    # Track seen filenames to avoid overwriting duplicates
    seen_filenames = set()

    # Generate all recipes
    for recipe_config in manifest.get('recipes', []):
        recipe_type = recipe_config['name']
        if recipe_type not in generator.templates:
            print(f"Error: Unknown recipe type in manifest: {recipe_type}", file=sys.stderr)
            sys.exit(1)

        variants = recipe_config.get('variants', [])
        variants = generator.expand_variants(variants)
        for variant in variants:
            version = variant['version']
            modifiers = {k: v for k, v in variant.items() if k not in ['name', 'version']}
            variant_subname = variant.get('name', '')

            if variant_subname:
                modifiers['variant_type'] = variant_subname
                modifiers['variant_subname'] = variant_subname

            content = generator.generate(recipe_type, version, **modifiers)

            if args.validate and not args.dry_run:
                content_validator = ContentValidator(generator.project_root)
                issues = content_validator.validate(content)
                semantic_validator = SemanticValidator()
                semantic_issues = semantic_validator.validate(content, version)
                all_issues = issues + semantic_issues
                if all_issues:
                    print(f"Validation issues for {recipe_type} {version}:", file=sys.stderr)
                    for issue in issues:
                        print(f"  - {issue}", file=sys.stderr)
                    sys.exit(1)

            filename = generator.generate_filename(recipe_type, version, **modifiers)
            output_path = args.output_dir / filename


            
            if filename in seen_filenames:
                continue  # Already generated this filename
            seen_filenames.add(filename)

            if args.dry_run:
                print(f"Would generate: {output_path}")
            else:
                print(f"Generating: {output_path}")
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(content)


def generate_single(args: argparse.Namespace, generator: RecipeGenerator) -> None:
    """Generate a single recipe."""
    modifiers = {
        'variant_type': 'desktop',
        'desktop': args.desktop if args.desktop else None,
        'storage': args.storage if args.storage != 'standard' else None,
        'security': args.security if args.security != 'secure' else None,
        'cpu': args.cpu if args.cpu and args.cpu != 'generic' else None,
        'gpu': args.gpu if args.gpu and args.gpu != 'none' else None,
    }
    modifiers = {k: v for k, v in modifiers.items() if v is not None}

    content = generator.generate(args.type, args.version, **modifiers)

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

    if args.output:
        if args.dry_run:
            print(f"Would write to: {args.output}")
        else:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Generated: {args.output}")
    else:
        print(content)
