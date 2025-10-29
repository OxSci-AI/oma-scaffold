# OMA Agent Service Template

A scaffold template for building OMA (Orchestration & Multi-Agent) services using the CrewAI framework.

## Prerequisites

- Python 3.11 or higher
- Poetry for dependency management
- AWS CLI configured with access to CodeArtifact
- Docker (for containerized deployment)

## Installation

### Option 1: Quick Install (Recommended)

Install directly from GitHub with a single command:

```bash
curl -sSL https://raw.githubusercontent.com/OxSci-AI/oma-scaffold/main/install.py | python3 -
```

This will:
1. Download the latest scaffold template
2. Prompt you for service name and agent name
3. Create a new project directory with all files configured
4. Initialize a git repository

### Option 2: Manual Setup

If you prefer to clone the repository first:

```bash
# Clone the repository
git clone https://github.com/OxSci-AI/oma-scaffold.git
cd oma-scaffold

# Run setup script
python setup.py
```

The setup script will prompt you for:
- Service name (will create `oma-{service-name}` directory)
- Agent name (will create the agent file and configure it)

## Quick Start

After installation, navigate to your new service directory:

```bash
cd oma-{your-service-name}
```

### 1. Configure AWS CodeArtifact

Before installing dependencies, configure access to the private package repository:

```bash
# Make the script executable (if not already)
chmod +x entrypoint-dev.sh

# Run the configuration script (valid for 12 hours)
./entrypoint-dev.sh
```

> **Note**: The authentication token expires after 12 hours. Re-run this script when needed.

### 2. Install Dependencies

```bash
poetry install
```

### 3. Development

#### Run Tests

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

#### Run Service Locally

```bash
poetry run uvicorn app.core.main:app --reload --port 8080
```

Access the API documentation at: http://localhost:8080/docs

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
│   ├── agents/
│   │   └── {agent_name}.py       # Your agent implementation
│   └── tools/
│       └── __init__.py           # Custom tools (if needed)
├── tests/
│   └── test_agents.py            # Agent tests
├── .vscode/
│   └── extensions.json           # Recommended VS Code extensions
├── Dockerfile                     # Multi-stage Docker build
├── entrypoint-dev.sh             # CodeArtifact configuration script
├── pyproject.toml                # Project dependencies and configuration
└── README.md                      # This file
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

## Contributing

[To be added - Guidelines for contributing to your service]

## License

[To be added - Your license information]
