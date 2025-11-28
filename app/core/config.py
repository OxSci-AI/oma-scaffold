"""
Configuration Management
"""

from oxsci_shared_core.config import BaseConfig


class Config(BaseConfig):
    """
    Application configuration

    MCP server configuration is now managed through JSON config files:
    - app/config/mcp/base.json - Base configuration
    - app/config/mcp/dev.json - Locol development overrides
    - app/config/mcp/test.json - Test environment overrides
    - app/config/mcp/prod.json - Production environment overrides
    """

    # agent service always use port 8080
    SERVICE_PORT: int = 8080
    # do not set the following 3 variables here,
    # use .env to set MCP_ENV to "dev" for local dev, and config the app/config/mcp/dev.json accordingly
    MCP_ENV: str = ""
    MCP_PROXY_URL: str = ""
    PROXY_API_KEY: str = ""

    # Claude Code integration mode: "cli" or "sdk"
    # - cli: Use subprocess-based CLI (default, production-ready),
    # - sdk: Use Python SDK (experimental, better API but tighter coupling)
    CLAUDE_CODE_MODE: str = "sdk"


# Global config instance
config = Config()
