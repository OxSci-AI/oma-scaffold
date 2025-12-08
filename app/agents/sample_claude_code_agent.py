#!/usr/bin/env python3
"""
Sample Claude Code Agent - Simple Demo

Demonstrates Claude Code execution with MCP tools.
Creates a single section to verify agent can run and call tools.
"""

from typing import Dict, Any


from app.core.config import config

from oxsci_oma_core import OMAContext
from oxsci_oma_core.models.adapter import ITaskExecutor
from oxsci_oma_core.models.agent_config import AgentConfig

from oxsci_shared_core.logging import logger

# Import execute_claude_code based on configuration
if config.CLAUDE_CODE_MODE == "sdk":
    from oxsci_oma_core.core.claude_code_agent_sdk import execute_claude_code

    logger.info("Using Claude Code SDK mode")
else:
    from oxsci_oma_core.core.claude_code_agent import execute_claude_code

    logger.info("Using Claude Code CLI mode (default)")


class SampleClaudeCodeAgent(ITaskExecutor):
    """Simple Claude Code Agent demo - creates one section"""

    agent_role: str = "claude_code_demo"

    def __init__(self, context: OMAContext):
        """Initialize the agent with context and adapters"""
        self.context = context
        self.logger = logger

    @classmethod
    def get_agent_config(cls) -> AgentConfig:
        """
        Get agent configuration

        Tool chain (MCP tools):
        - get_pdf_pages: Get PDF pages from MCP server
        - create_content_overview: Create structured content overview
        - create_content_section: Create content sections
        - complete_content_overview: Complete the overview

        Data flow:
        - Input: file_id (uploaded file ID)
        - Output: structured_content_overview_id (saved to context automatically)
        """
        return AgentConfig(
            agent_id=cls.agent_role,
            name="Claude Code Demo Agent",
            description="Simple demo agent using Claude Code to process PDF and create one section",
            timeout=300,
            retry_count=3,
            input={
                "file_id": "string - File ID of the PDF to process",
            },
            output={
                "structured_content_overview_id": "string - ID of the structured content overview created"
            },
            estimated_tools_cnt=5,
            estimated_total_time=300,
        )

    async def execute(self) -> Dict[str, Any]:
        """Execute PDF processing task - create one section only"""
        try:
            self.logger.info(f"Starting {self.agent_role} execution")

            # Get file_id from context
            file_id = self.context.get_shared_data("file_id")
            if not file_id:
                raise ValueError("file_id is required in context")

            self.logger.info(f"Processing file: {file_id}")

            # Build simple task prompt
            task_prompt = f"""You are a PDF processing assistant. Process PDF file and create ONE section only.

TASK:
1. Use get_pdf_pages tool to fetch PDF content (file_id: {file_id})
2. Use create_content_overview to create overview
3. Use create_content_section to create ONE abstract section from the PDF
4. Use complete_content_overview to finalize

Keep it simple - just create one section to verify tools work."""

            # Execute with Claude Code
            self.logger.info("Executing with Claude Code...")
            result = await execute_claude_code(
                prompt=task_prompt,
                context=self.context,
                timeout=300,
                use_mcp_tools=True,
                allowed_tools=["mcp__*"],
                disable_web_search=True,
            )

            self.logger.info(f"Execution completed: {result[:200]}...")
            overview_id = self.context.get_shared_data("structured_content_overview_id")

            return {
                "status": "success",
                "result": {
                    "processing_summary": result,
                    "structured_content_overview_id": overview_id,
                    "agent_role": self.agent_role,
                },
            }

        except Exception as e:
            self.logger.error(f"{self.agent_role} execution failed: {e}")
            return {
                "status": "error",
                "result": {
                    "error": str(e),
                    "agent_role": self.agent_role,
                },
            }
