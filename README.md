# OMA Agent Service Template

A scaffold template for building OMA (OxSci Multi-Agent) services using the CrewAI framework. More frameworks will be added in the future.

## Prerequisites

- Python 3.11 or higher
- Poetry for dependency management
- AWS CLI configured with access to CodeArtifact (for installing dependencies from CodeArtifact)

> **Note**: Docker is only required for CI/CD deployment workflows, not for local development.

## Installation

### Installation Prerequisites

The installer script itself only requires **Python 3.11+** (uses only Python standard library, no external packages needed).

However, to complete the installation, you also need:
- **Git** installed (for initializing the repository)
- **Network connectivity** to GitHub (for downloading the template)
- **Write permissions** in the directory where you'll run the script

The installer will also check for:
- **AWS CLI** (warning only - required later for CodeArtifact access, but not needed during installation)

The installer will automatically check these prerequisites before proceeding.

### Option 1: Quick Install (Recommended)

Install directly from GitHub with a single command. You can use either command-line arguments (recommended) or interactive prompts.

> **Important**: Run the script from the **parent directory** where you want to create the service. For example:
> - To create `/git/oma-my-service/`, run the script from `/git/` directory
> - The script will create `oma-{service-name}/` in the current working directory

#### Direct Installation with Arguments (Recommended)

The simplest way - directly download and execute with parameters:

```bash
# Navigate to the parent directory where you want to create the service
cd /git

# Run the installer
curl -sSL https://raw.githubusercontent.com/OxSci-AI/oma-scaffold/main/install.py | python3 - \
  --service-name document-processor \
  --agent-name document_processor \
  --yes
```

Command-line options:
- `--service-name`: Service name (must start with a letter, lowercase letters/numbers/hyphens only)
- `--agent-name`: Agent name (must start with a letter, lowercase letters/numbers/underscores only)
- `--yes` or `-y`: Skip confirmation prompt (recommended for non-interactive mode)
- `--skip-env-check`: Skip environment prerequisites check (not recommended)

#### Interactive Mode

If you prefer to answer prompts interactively, download the script first:

```bash
# Navigate to the parent directory where you want to create the service
cd /git

# Download and run interactively
curl -sSL https://raw.githubusercontent.com/OxSci-AI/oma-scaffold/main/install.py > install.py
python3 install.py
```

The script will:
1. **Check environment prerequisites** (Python 3.11+, Git, network connectivity)
2. **Show current directory** and confirm where the service will be created
3. **Prompt for service name** (e.g., `document-processor` - will create `oma-document-processor` directory)
4. **Prompt for agent name** (e.g., `document_processor` - will create the agent file and configure it)

> **Note**: If you try to use the pipe method without arguments, you'll get an `EOFError` because stdin is redirected. Always provide `--service-name` and `--agent-name` when using the pipe method.

The installer will:
1. Verify environment prerequisites (Python 3.11+, Git, network)
2. Download the latest scaffold template from GitHub
3. Create a new project directory with all files configured
4. Initialize a git repository
5. Set up the agent structure and configuration files

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

### 3. Run Tests

```bash
python tests/test_agents.py --test your_agent_name
```

### 4. Run Service

```bash
poetry run uvicorn app.core.main:app --reload --port 8080
```

Access the API documentation at: http://localhost:8080/docs

## Development Documentation

For comprehensive development documentation including:
- MCP Tool Configuration
- Agent Development Guide
- Testing Instructions
- Deployment Guide

See [docs/DEVELOPMENT_GUIDE.md](docs/DEVELOPMENT_GUIDE.md)

## License

© 2025 OxSci.AI. All rights reserved.
