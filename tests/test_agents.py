#!/usr/bin/env python3
"""
Sample Test File - Demonstrates Simplified Test Writing

This file shows how to use the new decorator-based testing approach
"""

import sys
from oxsci_oma_core.test_module import agent_test, integration_test, run_tests_from_cli

# ============================================================================
# Single Crew Tests
# ============================================================================
FILE_ID = (
    "c3c25b7f-20c4-41e7-bfe0-12543a0479cb"  # Real file ID from database for MCP server
)
STRUCTURED_CONTENT_OVERVIEW_ID = "725e6776-1fdc-4cbf-a615-90b72b78c548"  # Real overview ID from database for MCP server


@agent_test(
    verbose="stdout",
    framework="crew_ai",
    task_input={
        "file_id": FILE_ID,  # Real file ID from database for MCP server
        "user_id": "659c930a-a1a2-4752-bc55-0c2da52bb8a7",  # Test user ID
        "model": "openrouter/openai/gpt-4o-mini",
    },
)
def test_sample_parser():
    """Test SimpleReadCrew - PDF processing with MCP server"""
    from app.agents.sample_pdf_parser_agent import SampleParserCrew

    return SampleParserCrew


@agent_test(
    verbose="stdout",
    framework="langgraph",
    task_input={
        "file_id": FILE_ID,  # Real file ID from database for MCP server
        "model": "openrouter/openai/gpt-4o-mini",
    },
)
def test_sample_parser_langgraph():
    """Test LangGraph agent - PDF processing with MCP server"""
    from app.agents.sample_parser_langgraph import SampleParserLangGraph

    return SampleParserLangGraph


# ============================================================================
# Custom Input Context Example
# ============================================================================


@agent_test(
    verbose="stdout",
    framework="crew_ai",
    task_input={
        "structured_content_overview_id": STRUCTURED_CONTENT_OVERVIEW_ID,
    },
)
def test_sample_analysis():
    """Test with custom task input"""
    from app.agents.sample_analysis_agent import SampleAnalysisCrew

    return SampleAnalysisCrew


@agent_test(
    verbose="stdout",
    framework="claude",
    task_input={
        "file_id": FILE_ID,  # Same file as simple_read_crew
        "user_id": "659c930a-a1a2-4752-bc55-0c2da52bb8a7",  # Test user ID
        "model": "openrouter/openai/gpt-4o-mini",
    },
)
def test_claude_code_agent():
    """Test PDF processing with enhanced agent (Claude Code backend)"""
    from app.agents.sample_claude_code_agent import SampleClaudeCodeAgent

    return SampleClaudeCodeAgent


@agent_test(
    verbose="stdout",
    framework="claude",
    task_input={
        "structured_content_overview_id": STRUCTURED_CONTENT_OVERVIEW_ID,
    },
)
def test_cca_analysis():
    """Test PDF processing with enhanced agent (Claude Code backend)"""
    from app.agents.sample_cca_analysis import SampleCCAAnalysis

    return SampleCCAAnalysis


# ============================================================================
# CLI Entry Point
# ============================================================================


def main():
    """CLI entry point for running tests

    Usage:
        # Run specific test
        python tests/test_sample.py --test read
        python tests/test_sample.py --test search
        python tests/test_sample.py --test write

        # Run integration test
        python tests/test_sample.py --integration pipeline

        # Run all tests
        python tests/test_sample.py --all

        # Enable verbose logging
        python tests/test_sample.py --test read -v
    """
    # Define test map
    test_map = {
        "parser": test_sample_parser,
        "analysis": test_sample_analysis,
        "cca": test_claude_code_agent,
        "cca_analysis": test_cca_analysis,
        "langgraph_parser": test_sample_parser_langgraph,
    }

    # Run tests from CLI
    sys.exit(run_tests_from_cli(test_map))


if __name__ == "__main__":
    main()
