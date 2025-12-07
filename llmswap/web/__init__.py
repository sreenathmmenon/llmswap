"""
LLMSwap Web UI Module

Provides a local web interface for comparing model responses side-by-side.
Requires optional dependencies: pip install llmswap[web]

Copyright (c) 2025 Sreenath M Menon
Licensed under the MIT License
"""

# Check if Flask is available
try:
    import flask
    import flask_cors

    WEB_AVAILABLE = True
except ImportError:
    WEB_AVAILABLE = False

__all__ = ["WEB_AVAILABLE"]

if WEB_AVAILABLE:
    from .app import create_app, start_server

    __all__.extend(["create_app", "start_server"])
