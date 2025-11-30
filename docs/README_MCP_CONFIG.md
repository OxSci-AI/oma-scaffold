# MCP Configuration Testing Script

This script helps verify MCP server configuration and discover available tools.
**Uses `app.core.config` to ensure 100% identical behavior with app runtime.**

## Location

`agent-service-template/tool_helper.py` (wrapper for `oxsci_oma_core.utils.mcp_tool_inspector`)

**Why this architecture?**
- Core logic in `oxsci-oma-core` package - updates automatically with package upgrades
- Wrapper script delegates all functionality to the package module
- Directly imports `app.core.config` - guaranteed identical behavior to app runtime
- No manual .env loading - uses the same Config class as the app
- Same configuration paths (`app/config/mcp/`)
- Same environment variable handling

## Features

1. **Print MCP Server Configuration**
   - Show server name, URL, connection mode
   - Verify configuration merging (base.json + env.json)
   - Check environment variable substitution

2. **Discover and Print Tools**
   - Connect to MCP servers and fetch tool metadata
   - Display tool name, description, version
   - Show input parameters with types and requirements

## Usage

### 1. Print Server Configuration

```bash
cd agent-service-template

# Default environment (from app.core.config)
poetry run python tool_helper.py

# Specific environment (using ENV variable - same as app runtime)
ENV=dev poetry run python tool_helper.py
ENV=test poetry run python tool_helper.py
ENV=prod poetry run python tool_helper.py
```

**Output Example:**
```
================================================================================
 MCP Configuration Report - Environment: DEV
================================================================================

--------------------------------------------------------------------------------
 MCP Server Configuration
--------------------------------------------------------------------------------

Total Servers: 2
Enabled Servers: 2

Server List:

1. mcp-article-processing
   Status: ✅ Enabled
   Connection Mode: URL Override
   Service Name: mcp-article-processing-test
   URL: http://localhost:8060
   Port: 8060
   Timeout: 30s

2. journal-insight-service
   Status: ✅ Enabled
   Connection Mode: URL Override
   Service Name: journal-insight-service-test
   URL: http://localhost:8010
   Port: 8010
   Timeout: 30s
```

### 2. Discover Tools from All Servers

```bash
# Discover tools from all configured servers
poetry run python tool_helper.py --tools

# Discover tools with specific environment
ENV=test poetry run python tool_helper.py --tools
```

**Output Example:**
```
================================================================================
 MCP Tool Discovery
================================================================================

--------------------------------------------------------------------------------
 Server: mcp-article-processing
--------------------------------------------------------------------------------
  URL: http://localhost:8060
  Discovering tools...

  ✅ Found 3 tools

  1. extract_article_metadata (v1.0.0)
     Description: Extract metadata from article files
     Parameters:
       - file_path (string, required): Path to article file
       - format (string, optional): Output format (json/xml)

  2. process_references (v1.0.0)
     Description: Process and validate article references
     ...
```

### 3. Discover Tools from Specific Server

```bash
# Query specific server
poetry run python tool_helper.py --tools --server mcp-article-processing

# Combine with environment
ENV=dev poetry run python tool_helper.py --tools --server journal-insight-service
```

## Environment Configuration

### Environment Selection

**The script uses `app.core.config` - 100% identical to app runtime.**

```bash
# Default (from app.core.config)
poetry run python tool_helper.py
# → Uses config.ENV (from .env or default: Environment.DEVELOPMENT)

# Override with ENV variable (same as app runtime)
ENV=test poetry run python tool_helper.py
# → Uses test environment
```

**How it works:**
- Script imports `from app.core.config import config`
- `Config` class loads `.env` automatically (via BaseConfig)
- ENV priority:
  1. `ENV` environment variable (can override at runtime)
  2. `.env` file: `ENV=test`
  3. Default: `Environment.DEVELOPMENT` (dev)

**Key point:** Using `ENV=xxx` before the command is the same as setting it in .env or when running the actual app.

### Configuration Files

The script reads MCP configuration from:
- `app/config/mcp/base.json` - Base configuration
- `app/config/mcp/{env}.json` - Environment-specific overrides

### Environment Variables

Required environment variables (from `.env`):
```bash
ENV=test                    # Environment name (dev/test/prod)
MCP_PROXY_URL=https://...   # Proxy server URL (for proxy mode)
PROXY_API_KEY=xxx           # API key for proxy authentication
```

### Connection Modes

1. **URL Override** (dev environment - local development)
   ```json
   {
     "url_override": "http://localhost:8060"
   }
   ```
   - Highest priority
   - Direct connection to specified URL
   - Ignores proxy and service_name settings

2. **Proxy Mode** (external access)
   ```json
   {
     "proxy": true,
     "proxy_url": "${MCP_PROXY_URL}",
     "service_name": "mcp-article-processing-test",
     "api_key_env": "PROXY_API_KEY"
   }
   ```
   - Connects through proxy server
   - URL format: `{proxy_url}/{service_name}:{port}`

3. **Direct Mode** (ECS internal - test/prod)
   ```json
   {
     "proxy": false,
     "service_name": "mcp-article-processing-test",
     "port": 8060
   }
   ```
   - Direct ECS internal connection
   - URL format: `http://{service_name}.oxsci.internal:{port}`

## Configuration Tips

### Flexible Switching in dev.json

You can keep all configuration options and switch by commenting/uncommenting `url_override`:

```json
{
  "servers": {
    "mcp-article-processing": {
      "proxy": true,
      "proxy_url": "${MCP_PROXY_URL}",
      "service_name": "mcp-article-processing-test",
      "api_key_env": "PROXY_API_KEY",
      "url_override": "http://localhost:8060"  // Comment this to use proxy mode
    }
  }
}
```

- With `url_override`: Direct local connection to localhost:8060
- Without `url_override`: Proxy connection through MCP_PROXY_URL

## Troubleshooting

### Server Startup Timeout

```
⚠️  Server startup timeout: MCP server startup timeout after 300s
```

**Solution:**
- MCP servers may need time to cold start (up to 5 minutes)
- Increase `max_startup_wait` in configuration if needed
- Check if server is actually running on the specified URL

### Connection Refused

```
❌ Error discovering tools: Connection refused
```

**Solution:**
- Verify server is running: `curl http://localhost:8060/health`
- Check URL configuration in dev.json
- Ensure .env variables are loaded correctly

### Invalid Configuration

```
❌ Error: proxy_url is required when proxy=true
```

**Solution:**
- Set `MCP_PROXY_URL` in .env file
- Or use `url_override` for direct connection
- Or set `proxy: false` for direct mode

## Development Workflow

1. **Start local MCP server** (if testing locally)
   ```bash
   cd ~/git/mcp-article-processing
   poetry run uvicorn app.main:app --port 8060
   ```

2. **Verify configuration**
   ```bash
   cd ~/git/oxsci-oma-core/agent-service-template
   poetry run python tool_helper.py --env dev
   ```

3. **Discover available tools**
   ```bash
   poetry run python tool_helper.py --env dev --tools
   ```

4. **Test tool functionality** (in your agent service)
   ```python
   from oxsci_oma_core.tools.registry import tool_registry

   # Tools are automatically discovered from MCP servers
   tool = tool_registry.get_tool_meta("extract_article_metadata")
   print(tool)
   ```
