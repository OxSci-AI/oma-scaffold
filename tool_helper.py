#!/usr/bin/env python3
"""
MCP Tool Helper - Wrapper for OMA Core MCP Tool Inspector

This wrapper script delegates to the oxsci_oma_core.utils.mcp_tool_inspector module,
ensuring that updates to the tool inspection logic are automatically available
through package updates without requiring script changes.

Usage:
    # All arguments are passed through to the underlying inspector
    poetry run python tool_helper.py --tools
    poetry run python tool_helper.py --tools tool1 tool2 --input
    poetry run python tool_helper.py --tools --server mcp-article-processing --detail

For detailed usage, run: poetry run python tool_helper.py --help
"""

import sys
from oxsci_oma_core.utils.mcp_tool_inspector import main

if __name__ == "__main__":
    sys.exit(main())
