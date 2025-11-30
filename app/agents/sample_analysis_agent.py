#!/usr/bin/env python3
"""
Simple Search Crew - 步骤2: 读取section并搜索相关论文
演示: 从context读取overview_id -> 提取section -> 搜索论文 -> 创建analysis result
"""


from typing import Dict, Any

from crewai import Agent, Task, Crew, Process
from crewai.project import CrewBase

from oxsci_oma_core import OMAContext
from oxsci_oma_core.adapter.crew_ai import CrewAIToolAdapter
from oxsci_oma_core.models.adapter import ITaskExecutor
from oxsci_oma_core.models.agent_config import AgentConfig

from oxsci_shared_core.logging import logger


@CrewBase
class SampleAnalysisCrew(ITaskExecutor):
    """步骤2: 读取content section，搜索相关论文并写入analysis"""

    agent_role: str = "simple_search_test"

    def __init__(self, context: OMAContext, adapter: CrewAIToolAdapter):
        """Initialize the crew with context and adapters"""
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
        获取Agent配置

        工具链 (全部使用MCP工具):
        - get_content_section_list: List content sections
        - get_content_section_detail: Get section details
        - search_articles: Search for academic articles with keyword filtering
        - get_article: Get complete article details by DOI
        - create_analysis_overview: Create analysis overview
        - create_analysis_section: Create analysis section
        - complete_analysis_overview: Complete analysis

        数据流:
        - Input: structured_content_overview_id (从步骤1的output自动传入)
        - Output: comparative_analysis_id (搜索结果分析的ID, 通过analysis_type="comparative_analysis"生成)
        """

        return AgentConfig(
            agent_id=cls.agent_role,
            name="Content Analyzer & Searcher",
            description="Read content section, search related article, and create analysis result",
            # url, service_name, enabled are auto-managed by framework, no need to set
            timeout=300,
            retry_count=3,
            input={
                "structured_content_overview_id": "string - structured content overview ID from step 1",
            },
            output={
                "comparative_analysis_id": "string - analysis result ID with search findings",
            },
            estimated_tools_cnt=7,
            estimated_total_time=600,
        )

    async def execute(self) -> Dict[str, Any]:
        """执行任务并返回结果"""
        try:
            self.logger.info(f"Starting {self.agent_role} execution")
            crew_instance = self.crew()
            result = await crew_instance.kickoff_async()
            self.logger.info(f"{self.agent_role} execution completed")

            return {
                "status": "success",
                "result": {
                    "raw_output": str(result),
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

    def comparative_analyzer(self) -> Agent:
        """内容分析与搜索Agent: 使用MCP工具读取section，搜索论文，创建analysis"""

        # 使用MCP工具
        all_tools = self.adapter.get_tools(
            [
                "get_content_section_list",  # 列出content sections
                "get_content_section_detail",  # 读取section详情
                "search_articles",  # 搜索学术文章
                "get_article",  # 获取完整文章详情
                "create_analysis_overview",  # 创建分析概览
                "create_analysis_section",  # 创建分析章节
                "complete_analysis_overview",  # 完成分析
            ]
        )

        return Agent(
            role="Comparative Analysis Agent",
            goal="Read content sections via tools, search related articles or reference articles if available and get abstracts, create Comparative analysis between source content and articles",
            backstory="""You are an academic researcher specializing in comparative analysis of scholarly articles. 
            Your task is to read specific sections of a given paper, search for related academic articles, and create a comprehensive comparative analysis.
            - Analyze how the paper's approach differs from existing literature
            - Identify methodological similarities and differences
            - Compare findings and conclusions with related work
            - Evaluate the paper's novelty in relation to existing research
            - Assess how the paper extends or challenges current knowledge
            Your workflow:
            1. Use get_content_section_list to get available sections.
            2. Use get_content_section_detail to read section detail.
            3. Use search_articles with related keyword parameter to search for academic articles.
            4. Use get_article to get Abstract detail for selected articles by DOI. if failed or no abstract, try another article.(max 20 tries)
            5. Use create_analysis_overview ONCE to create analysis with analysis_type='comparative_analysis'.
            6. Use create_analysis_section to add Comparative analysis analysis_type='comparative_analysis' and define section_type according to your analysis,
            use section type:title of compared article as section title, compare 5-10 articles if possible.
            7. Use complete_analysis_overview to finalize with analysis_type='comparative_analysis'.
            """,
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            max_iter=60,
            tools=all_tools,
        )

    def search_and_analyze_task(self) -> Task:
        """搜索并分析任务"""
        return Task(
            description="""use content reader tools to read abstract, introduction or summary section, and reference section of current paper, do a quick comparative analysis""",
            agent=self.comparative_analyzer(),
            expected_output="summary of successful compared articles and section statistics",
        )

    def crew(self) -> Crew:
        """创建搜索分析crew"""
        return Crew(
            agents=[self.comparative_analyzer()],
            tasks=[self.search_and_analyze_task()],
            process=Process.sequential,
            verbose=True,
        )
