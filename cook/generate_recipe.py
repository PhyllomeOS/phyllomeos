"""Entry point for the recipe generator.

This is a simple wrapper script that provides the main entry point for running
the recipe generator. It follows the common Python pattern of having a script
that can be run directly or imported as a module.

Usage:
    # Run as script for single generation
    python generate_recipe.py --output my-recipe.cfg --version 43 --desktop gnome
    
    # Or using the universal template with modifiers
    python generate_recipe.py --output single.cfg --version 43 --guest-agents true
    
    # Or from another Python script
    from generate_recipe import main
    main()

This module doesn't do any processing itself - it delegates to the cli.main()
function which handles all the actual work. The separation allows for:
- Easy command-line execution (this file is the entry point)
- Module imports without triggering execution
- Clean separation of concerns (cli.py handles CLI, this just delegates)
"""

from cli import main

if __name__ == '__main__':
    main()
