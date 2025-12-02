#!/usr/bin/env python3
"""
Sample Test File - Demonstrates Simplified Test Writing

This file shows how to use the new decorator-based testing approach
"""

import sys

from app.agents.sample_cca_analysis import SampleCCAAnalysis
from app.agents.sample_claude_code_agent import SampleClaudeCodeAgent

from oxsci_oma_core.test_module import agent_test, integration_test, run_tests_from_cli

# Import your crew classes
from app.agents.sample_pdf_parser_agent import SampleParserCrew
from app.agents.sample_analysis_agent import SampleAnalysisCrew


# ============================================================================
# Single Crew Tests
# ============================================================================


@agent_test(
    verbose="stdout",
    task_input={
        "file_id": "eef0e45a-29ba-47d5-b339-c73bb5d07789",  # Real file ID from database for MCP server
        "user_id": "659c930a-a1a2-4752-bc55-0c2da52bb8a7",  # Test user ID
        "model": "openrouter/openai/gpt-4o-mini",
    },
)
def test_sample_parser():
    """Test SimpleReadCrew - PDF processing with MCP server"""
    return SampleParserCrew


# ============================================================================
# Custom Input Context Example
# ============================================================================


@agent_test(
    verbose="stdout",
    task_input={
        "structured_content_overview_id": "725e6776-1fdc-4cbf-a615-90b72b78c548",
    },
)
def test_sample_analysis():
    """Test with custom task input"""
    return SampleAnalysisCrew


@agent_test(
    verbose="stdout",
    task_input={
        "file_id": "eef0e45a-29ba-47d5-b339-c73bb5d07789",  # Same file as simple_read_crew
        "user_id": "659c930a-a1a2-4752-bc55-0c2da52bb8a7",  # Test user ID
        "model": "openrouter/openai/gpt-4o-mini",
    },
)
def test_claude_code_agent():
    """Test PDF processing with enhanced agent (Claude Code backend)"""
    return SampleClaudeCodeAgent


@agent_test(
    verbose="stdout",
    task_input={
        "structured_content_overview_id": "725e6776-1fdc-4cbf-a615-90b72b78c548",
    },
)
def test_cca_analysis():
    """Test PDF processing with enhanced agent (Claude Code backend)"""
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
    }

    # Run tests from CLI
    sys.exit(run_tests_from_cli(test_map))


if __name__ == "__main__":
    main()
