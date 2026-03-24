.PHONY: help generate-recipes validate-recipes test clean install-deps

help:
	@echo "Phyllome OS Recipe Generator"
	@echo ""
	@echo "Available targets:"
	@echo "  generate-recipes  - Generate all recipes from manifest"
	@echo "  validate-recipes  - Validate existing recipes"
	@echo "  test              - Run pytest test suite"
	@echo "  clean             - Remove generated recipes"
	@echo "  install-deps      - Install Python dependencies"

install-deps:
	pip install -r requirements.txt

generate-recipes:
	python generate_recipe.py \
		--manifest recipes_manifest.yaml \
		--output-dir ../recipes/

validate-recipes:
	python generate_recipe.py \
		--validate ../recipes/*.cfg

test:
	pytest ../tests/test_recipe_generator.py -v

clean:
	rm -f ../recipes/*.cfg
	@echo "Generated recipes removed. Edit recipes_manifest.yaml and run 'make generate-recipes' to regenerate."
