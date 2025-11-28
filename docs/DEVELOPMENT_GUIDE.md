# OMA Agent Service Development Guide

This guide covers comprehensive documentation for developing OMA (OxSci Multi-Agent) agent services.

## Prerequisites

- Python 3.11 or higher
- Poetry for dependency management
- AWS CLI configured with access to CodeArtifact (for installing dependencies from CodeArtifact)

> **Note**: Docker is only required for CI/CD deployment workflows, not for local development.

## Environment Setup (Required)

**Before starting local development, you MUST configure your environment variables:**

1. Copy the sample environment file to create your local `.env` file:

   ```bash
   cp .env.sample .env
   ```

2. Edit `.env` and fill in all required values according to the comments in the file.

> **Important Notes:**
> - `MCP_ENV` must be set to `dev` for local development. Do NOT use `test` for MCP_ENV locally.
> - Configure `app/config/mcp/dev.json` for MCP server settings, do NOT modify `mcp/test.json`.
> - The `.env` file is gitignored and should never be committed.
> - Contact your team lead for the actual credential values.

## Project Structure

```
oma-{service-name}/
├── .github/
│   └── workflows/
│       └── docker-builder.yml    # CI/CD workflow for building and deploying
├── app/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py             # Service configuration
│   │   └── main.py               # FastAPI application entry point
│   ├── config/
│   │   └── mcp/                  # MCP tool configuration
│   │       ├── base.json         # Base MCP server definitions
│   │       ├── dev.json          # Development environment overrides
│   │       ├── test.json         # Test environment overrides
│   │       └── prod.json         # Production environment overrides
│   ├── agents/
│   │   └── {agent_name}.py       # Your agent implementation
│   └── tools/
│       └── __init__.py           # Custom tools (if needed)
├── tests/
│   ├── test_agents.py            # Agent tests
│   └── sample/                   # Sample test files (PDFs, etc.)
│       └── .gitkeep
├── .vscode/
│   └── extensions.json           # Recommended VS Code extensions
├── Dockerfile                     # Multi-stage Docker build
├── entrypoint-dev.sh             # CodeArtifact configuration script
├── tool_helper.py                # MCP tool inspection utility (wrapper for oma-core)
├── pyproject.toml                # Project dependencies and configuration
├── .env.sample                    # Environment variables template (copy to .env)
└── README.md                      # Project readme
```

## MCP Tool Configuration

### What are MCP Tools?

MCP (Model Context Protocol) tools are external services that provide specialized capabilities to your agents:

- **journal-insight-service**: Article search, journal information, PDF processing
- **mcp-article-processing**: Structured content processing, section management

MCP tools are automatically discovered and registered at startup based on your configuration.

### Configuration Files

MCP servers are configured using JSON files in `app/config/mcp/`:

1. **base.json**: Defines all available MCP servers with complete configuration
   - Server endpoints (service_name, port)
   - Connection settings (timeout, retry_interval)
   - Proxy configuration (for cloud access)
   - Default: all servers disabled

2. **Environment-specific files** (dev.json, test.json, prod.json):
   - Override base.json settings
   - Enable/disable servers per environment
   - Set environment-specific URLs or proxy settings

Example base.json:

```json
{
  "servers": {
    "journal-insight-service": {
      "enabled": false,
      "service_name": "journal-insight-service-prod",
      "port": 8010,
      "timeout": 30,
      "proxy": false,
      "proxy_url": "${MCP_PROXY_URL}",
      "api_key": "${PROXY_API_KEY}"
    }
  }
}
```

Example dev.json (only overrides):

```json
{
  "servers": {
    "journal-insight-service": {
      "enabled": true
    }
  }
}
```

### Configuring MCP Servers

1. **Development (Local)**: Edit `app/config/mcp/dev.json` to enable/disable MCP servers
   ```json
   {
     "servers": {
       "mcp-article-processing": {
         "enabled": true
       }
     }
   }
   ```

2. **Test/Production (Cloud)**: MCP servers can use proxy mode for cloud access
   - Set `"proxy": true` in environment-specific config
   - Configure `MCP_PROXY_URL` and `PROXY_API_KEY` environment variables

For local development, ensure the required MCP services are running on their configured ports (see base.json).

### Checking Available MCP Tools

Use the `tool_helper.py` script to inspect configured MCP servers and their available tools:

```bash
# List all configured MCP servers
poetry run python tool_helper.py

# List all available tools from MCP servers (basic info)
poetry run python tool_helper.py --tools

# List specific tools by name
poetry run python tool_helper.py --tools search_articles get_article

# List tools with input parameters only
poetry run python tool_helper.py --tools --input

# List tools with detailed metadata (input parameters + output schemas)
poetry run python tool_helper.py --tools --detail

# Filter tools by specific MCP server
poetry run python tool_helper.py --tools --server journal-insight-service

# Combine options: specific tools with input parameters
poetry run python tool_helper.py --tools search_articles fetch_article --input

# Combine options: server filter with detailed output
poetry run python tool_helper.py --tools --server mcp-article-processing --detail
```

### Using MCP Tools in Agents

MCP tools are automatically available to all agents through the tool registry. You don't need to import them explicitly - just reference them by name in your agent configuration:

```python
from crewai import Agent, Task

agent = Agent(
    role="Research Assistant",
    goal="Find and analyze academic articles",
    tools=[
        "search_articles",      # MCP tool from journal-insight-service
        "get_article",          # MCP tool from journal-insight-service
        "get_pdf_pages"         # MCP tool from mcp-article-processing
    ]
)
```

## Agent Development

### Creating a New Agent

1. Create a new file in `app/agents/` (e.g., `my_agent.py`)
2. Extend the `ITaskExecutor` interface
3. Implement required methods:
   - `get_agent_config()`: Define agent metadata and I/O schema
   - `execute()`: Main execution logic
   - Agent and task definitions using CrewAI

Refer to `app/agents/agent_template.py` for a complete example.

### Registering Your Agent

Add your agent to the `agent_executors` list in `app/core/main.py`:

```python
from app.agents.my_agent import MyAgent

agent_executors = [
    MyAgent,
    # Add more agents here
]
```

## Testing

The project uses the `oxsci-oma-core` test module which provides:

- `@agent_test` decorator for single agent tests
- `@integration_test` decorator for multi-agent pipeline tests
- Automatic test environment setup and teardown
- Sample PDF processing for document-based agents

### Running Tests

```bash
# Run all tests
python tests/test_agents.py --all

# Run specific agent test
python tests/test_agents.py --test your_agent_name

# Run integration tests
python tests/test_agents.py --integration full_pipeline

# Enable verbose logging
python tests/test_agents.py --test your_agent_name -v
```

See `tests/test_agents.py` for examples.

## Deployment

### Building Docker Image

The CI/CD workflow automatically builds and pushes Docker images when:

- Tags matching `v*` are pushed
- Manually triggered via workflow_dispatch

### Manual Deployment

```bash
# Build image
docker build -t your-agent-service .

# Run container
docker run -p 8080:8080 \
  -e ENV=test \
  your-agent-service
```

## Configuration

Service configuration is managed through environment variables. See `app/core/config.py` for available options.

Key environment variables:

- `SERVICE_PORT`: Port to run the service (default: 8080)
- `ENV`: Environment (development/test/production)
- `LOG_LEVEL`: Logging level

## Tools and Frameworks

This template integrates:

- **FastAPI**: Web framework for building APIs
- **CrewAI**: Multi-agent orchestration framework
- **oxsci-oma-core**: Core OMA agent functionality
- **oxsci-shared-core**: Shared utilities and configuration

## License

© 2025 OxSci.AI. All rights reserved.
