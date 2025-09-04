#!/usr/bin/env python3
"""Entry point for llmswap CLI when run as `python -m llmswap`"""

from .cli import main

if __name__ == '__main__':
    exit(main())