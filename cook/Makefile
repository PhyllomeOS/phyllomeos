.PHONY: help generate-recipes validate-recipes clean clean-dishes install-deps flatten-dishes all

help:
	@echo "Phyllome OS Recipe Generator"
	@echo ""
	@echo "Available targets:"
	@echo "  generate-recipes  - Generate all recipes from manifest"
	@echo "  validate-recipes  - Validate existing recipes"
	@echo "  all               - Generate, validate, and flatten all recipes (default)"
	@echo "  flatten-dishes    - Flatten all recipes to dishes"
	@echo "  clean-dishes      - Remove flattened dishes"
	@echo "  clean             - Remove generated recipes"
	@echo "  install-deps      - Install Python dependencies"

all: generate-recipes flatten-dishes validate-recipes
	@echo "✓ All recipes generated, flattened, and validated"

install-deps:
	pip install -r requirements.txt

generate-recipes:
	@rm -f recipes/*.cfg
	@python3 generate_recipe.py \
		--manifest recipes_manifest.yaml \
		--output-dir recipes/

validate-recipes:
	@echo "Validating recipes..."
	@for f in dishes/*.cfg; do \
		if [ -f "$$f" ]; then \
			echo "  Processing: $$(basename $$f)"; \
			ksflatten -c "$$f" -o /dev/null 2>&1 && echo "    ✓ OK" || { echo "    ✗ FAILED"; exit 1; }; \
		fi; \
	done

flatten-dishes:
	@echo "Flattening recipes to dishes..."
	@python bin/ksflatten-relative recipes dishes

clean-dishes:
	rm -f dishes/*.cfg
	@echo "✓ Flattened dishes removed. Run 'make flatten-dishes' to regenerate."

clean:
	rm -f recipes/*.cfg
	@echo "Generated recipes removed. Edit recipes_manifest.yaml and run 'make generate-recipes' to regenerate. Run 'make clean-dishes' to remove flattened dishes."
