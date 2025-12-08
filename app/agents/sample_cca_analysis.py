#!/usr/bin/env python3
"""
Sample Claude Code Analysis Agent - Comparative Analysis Demo

Demonstrates Claude Code execution with MCP tools for comparative analysis.
Reads content sections, searches related articles, and creates comparative analysis.
"""

from typing import Dict, Any

from crewai.project import CrewBase

from app.core.config import config

from oxsci_oma_core import OMAContext
from oxsci_oma_core.adapter.crew_ai import CrewAIToolAdapter
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


@CrewBase
class SampleCCAAnalysis(ITaskExecutor):
    """Claude Code Agent for comparative analysis - reads sections, searches articles, creates analysis"""

    agent_role: str = "cca_comparative_analysis"

    def __init__(self, context: OMAContext):
        """Initialize the agent with context and adapters"""
        self.context = context
        self.logger = logger

    @classmethod
    def get_agent_config(cls) -> AgentConfig:
        """
        Get agent configuration

        Tool chain (MCP tools):
        - get_content_section_list: List content sections
        - get_content_section_detail: Get section details
        - search_articles: Search for academic articles with keyword filtering
        - get_article: Get complete article details by DOI
        - create_analysis_overview: Create analysis overview
        - create_analysis_section: Create analysis section
        - complete_analysis_overview: Complete analysis

        Data flow:
        - Input: structured_content_overview_id (from step 1 output)
        - Output: comparative_analysis_id (analysis result ID via analysis_type="comparative_analysis")
        """
        return AgentConfig(
            agent_id=cls.agent_role,
            name="Claude Code Comparative Analysis Agent",
            description="Read content sections, search related articles, and create comparative analysis using Claude Code",
            timeout=600,
            retry_count=3,
            input={
                "structured_content_overview_id": "string - structured content overview ID from step 1",
            },
            output={
                "comparative_analysis_id": "string - analysis result ID with search findings",
            },
            estimated_tools_cnt=20,
            estimated_total_time=600,
        )

    async def execute(self) -> Dict[str, Any]:
        """Execute comparative analysis task using Claude Code"""
        try:
            self.logger.info(f"Starting {self.agent_role} execution")

            # Get structured_content_overview_id from context
            overview_id = self.context.get_shared_data("structured_content_overview_id")
            if not overview_id:
                raise ValueError(
                    "structured_content_overview_id is required in context"
                )

            self.logger.info(f"Processing overview: {overview_id}")

            # Build task prompt for Claude Code
            task_prompt = f"""You are an academic researcher specializing in comparative analysis of scholarly articles.
Your task is to read specific sections of a given paper, search for related academic articles, and create a comprehensive comparative analysis.

CONTEXT:
- structured_content_overview_id: {overview_id}

TASK WORKFLOW:
1. Use get_content_section_list tool to get available sections for the content overview.
2. Use get_content_section_detail to read the abstract, introduction or summary section, and reference section.
3. Use search_articles with related keyword parameter to search for academic articles related to the content.
4. Use get_article to get Abstract detail for selected articles by DOI. If failed or no abstract, try another article (max 20 tries).
5. Use create_analysis_overview ONCE to create analysis with analysis_type='comparative_analysis'.
6. Use create_analysis_section to add comparative analysis sections:
   - Use analysis_type='comparative_analysis'
   - Define section_type according to your analysis
   - Use "section type: title of compared article" as section title
   - Compare 5-10 articles if possible
7. Use complete_analysis_overview to finalize with analysis_type='comparative_analysis'.

ANALYSIS FOCUS:
- Analyze how the paper's approach differs from existing literature
- Identify methodological similarities and differences
- Compare findings and conclusions with related work
- Evaluate the paper's novelty in relation to existing research
- Assess how the paper extends or challenges current knowledge

OUTPUT:
Provide a summary of successfully compared articles and section statistics."""

            # Execute with Claude Code
            self.logger.info("Executing comparative analysis with Claude Code...")
            result = await execute_claude_code(
                prompt=task_prompt,
                context=self.context,
                timeout=600,
                use_mcp_tools=True,
                allowed_tools=["mcp__*"],
                disable_web_search=True,
            )

            self.logger.info(f"Execution completed: {result[:200]}...")
            analysis_id = self.context.get_shared_data("comparative_analysis_id")

            return {
                "status": "success",
                "result": {
                    "raw_output": result,
                    "comparative_analysis_id": analysis_id,
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
