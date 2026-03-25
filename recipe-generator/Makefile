.PHONY: help generate-recipes validate-recipes test test-integration test-container clean install-deps

help:
	@echo "Phyllome OS Recipe Generator"
	@echo ""
	@echo "Available targets:"
	@echo "  generate-recipes  - Generate all recipes from manifest"
	@echo "  validate-recipes  - Validate existing recipes"
	@echo "  test              - Run pytest test suite (unit + integration)"
	@echo "  test-integration  - Run integration tests only"
	@echo "  test-container    - Run all tests in container"
	@echo "  clean             - Remove generated recipes"
	@echo "  install-deps      - Install Python dependencies"

install-deps:
	pip install -r requirements.txt

generate-recipes:
	rm -f ../recipes/*.cfg
	python generate_recipe.py \
		--manifest recipes_manifest.yaml \
		--output-dir ../recipes/

validate-recipes:
	python generate_recipe.py \
		--validate ../recipes/*.cfg

test:
	python3 -m pytest ../tests/ -v --tb=short

test-integration:
	python3 -m pytest ../tests/integration/ -v --tb=short

test-container:
	podman build -t phyllo/test-runner ../tests/container/
	podman run --rm -v .:/phyllomeos:ro phyllo/test-runner

clean:
	rm -f ../recipes/*.cfg
	@echo "Generated recipes removed. Edit recipes_manifest.yaml and run 'make generate-recipes' to regenerate."
