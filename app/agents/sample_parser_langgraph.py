#!/usr/bin/env python3
"""
Sample Parser LangGraph - PDF Parser using LangGraph framework

Demonstrates:
- LangGraph adapter integration with OMA framework
- Tool calling with langgraph.prebuilt.create_react_agent
- Async agent execution
"""

from typing import Dict, Any

from langgraph.prebuilt import create_react_agent

from oxsci_oma_core import OMAContext
from oxsci_oma_core.adapter.langgraph import LangGraphAdapter, LangGraphLoggingHandler
from oxsci_oma_core.models.adapter import ITaskExecutor
from oxsci_oma_core.models.agent_config import AgentConfig
from oxsci_shared_core.logging import logger


class SampleParserLangGraph(ITaskExecutor):
    """PDF Parser using LangGraph framework"""

    agent_role: str = "sample_parser_langgraph"

    def __init__(self, context: OMAContext, adapter: LangGraphAdapter):
        """Initialize with context and LangGraph adapter"""
        self.context = context
        self.adapter = adapter
        self.llm = self.adapter.create_llm(
            model=context.get_shared_data("model", "openrouter/openai/gpt-4o-mini"),
            temperature=0.1,
        )
        self.logger = logger

    @classmethod
    def get_agent_config(cls) -> AgentConfig:
        """
        Get Agent configuration

        Tools (all MCP tools):
        - get_pdf_pages: Get PDF page content from MCP server
        - create_content_overview: Create content overview
        - create_content_section: Create content section
        - complete_content_overview: Complete overview

        Data flow:
        - Input: file_id (user uploaded file ID)
        - Output: overview_id (auto-saved to context for downstream use)
        """
        return AgentConfig(
            agent_id=cls.agent_role,
            name="PDF Parser (LangGraph)",
            description="Demo agent using LangGraph to parse PDF and create structured content",
            timeout=300,
            retry_count=3,
            input={
                "file_id": "string - manuscript file ID to process",
                "model": "string - LLM model to use (default: openrouter/openai/gpt-4o-mini)",
            },
            output={
                "structured_content_overview_id": "string - structured content overview ID (auto-saved to context)",
            },
            estimated_tools_cnt=5,
            estimated_total_time=600,
        )

    async def execute(self) -> Dict[str, Any]:
        """Execute task and return result"""
        # try:
        self.logger.info(f"Starting {self.agent_role} execution (LangGraph)")

        # Get tools from adapter
        tools = self.adapter.get_tools(
            [
                "get_pdf_pages",
                "create_content_overview",
                "create_content_section",
                "complete_content_overview",
            ]
        )

        # System prompt for the agent
        system_prompt = """You are a PDF processor that efficiently processes PDFs using tools.

Your workflow:
1. Use get_pdf_pages tool to fetch content and identify sections.
2. Use create_content_overview tool to create an overview before adding sections.
3. Use create_content_section tool to add sections with extracted content.
4. Use complete_content_overview tool to finalize.

Process the PDF file and create the abstract section only, then finalize."""

        # Create react agent with LangGraph
        agent = create_react_agent(
            model=self.llm,
            tools=tools,
            prompt=system_prompt,
        )

        # Create logging handler for execution visibility
        logging_handler = LangGraphLoggingHandler(
            verbose=True, agent_name=self.agent_role
        )

        # Execute agent with recursion limit and logging
        result = await agent.ainvoke(
            {
                "messages": [
                    (
                        "user",
                        "Process the PDF file and create structured content overview.",
                    )
                ]
            },
            config={
                "recursion_limit": 50,  # Default is 25, increase for complex tasks
                "callbacks": [logging_handler],
            },
        )

        # Log execution summary
        summary = logging_handler.get_summary()
        self.logger.info(
            f"Execution summary: {summary['llm_calls']} LLM calls, "
            f"{summary['tool_calls']} tool calls"
        )

        # Extract final message
        final_output = ""
        if result.get("messages"):
            final_message = result["messages"][-1]
            if hasattr(final_message, "content"):
                final_output = final_message.content

        self.logger.info(f"{self.agent_role} execution completed")

        return {
            "status": "success",
            "result": {
                "raw_output": str(final_output),
                "agent_role": self.agent_role,
            },
        }

        # except Exception as e:
        #     self.logger.error(f"{self.agent_role} execution failed: {e}")
        #     return {
        #         "status": "error",
        #         "result": {
        #             "error": str(e),
        #             "agent_role": self.agent_role,
        #         },
        #     }
