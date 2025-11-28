#!/usr/bin/env python3
"""
MCP Tool Helper - Wrapper for OMA Core MCP Tool Inspector

This wrapper script delegates to the oxsci_oma_core.utils.mcp_tool_inspector module,
ensuring that updates to the tool inspection logic are automatically available
through package updates without requiring script changes.

Usage:
    # All arguments are passed through to the underlying inspector

  # default OMA protocol
  poetry run python tool_helper.py --tools --input

  # Claude Code CLI protocol
  poetry run python tool_helper.py --tools -p cc_cli --input

  # Claude Code SDK protocol
  poetry run python tool_helper.py --tools -p cc_sdk --detail

  # View specific tool
  poetry run python tool_helper.py --tools get_pdf_pages -p cc_cli --input

For detailed usage, run: poetry run python tool_helper.py --help
"""

import sys
from oxsci_oma_core.utils.mcp_tool_inspector import main

if __name__ == "__main__":
    sys.exit(main())
