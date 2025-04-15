"""
Python REPL startup script.

This script ensures that:
- The `src/` directory is in the import path, allowing direct imports like `import sql_artifacts`
- Rich tracebacks are enabled if the `rich` library is installed, improving the readability of error messages
"""

import sys
import os

# Determine the absolute path to the `src/` directory
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
src_path = os.path.join(project_root, "src")

# Add `src/` to sys.path to allow clean imports from project code
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Attempt to enable rich tracebacks for improved debugging
try:
    from rich.traceback import install

    install(show_locals=True)
except ImportError:
    # If rich isn't available, continue silently
    pass
