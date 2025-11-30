#!/usr/bin/env python3
"""
Simple Read Crew - 步骤1: 下载PDF并解析提取前3页
演示: 文件处理 -> 创建structured content -> 输出overview_id到context
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
class SampleParserCrew(ITaskExecutor):
    """步骤1: 下载PDF并解析，创建structured content overview"""

    agent_role: str = "simple_read_test"

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
        - get_pdf_pages: 从MCP服务器获取PDF页面内容
        - create_content_overview: 创建content overview
        - create_content_section: 创建content section (前3页)
        - complete_content_overview: 完成overview

        数据流:
        - Input: file_id (用户上传的文件ID)
        - Output: overview_id (自动记录到context，供下游使用)
        """

        return AgentConfig(
            agent_id=cls.agent_role,
            name="PDF Reader & Parser",
            description="demo agent of reading and parsing PDF to create structured content overview",
            # url, service_name, enabled are auto-managed by framework, no need to set
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

    def pdf_processor(self) -> Agent:
        """PDF处理Agent: 使用MCP工具获取PDF内容并创建structured content"""

        # 使用MCP工具
        # MCP工具通过工具名称列表获取
        all_tools = self.adapter.get_tools(
            [
                "get_pdf_pages",  # 获取PDF页面
                "create_content_overview",  # 创建概览
                "create_content_section",  # 创建章节
                "complete_content_overview",  # 完成概览
            ]
        )

        return Agent(
            role="PDF Processor",
            goal="Get PDF pages via tools and create structured content",
            backstory="""You process PDFs efficiently using tools. Your workflow:
            1. Use get_pdf_pages tool to fetch content and identify sections.
            2. Use create_content_overview tool to create an overview before adding section.
            3. Use create_content_section tool to add sections with extracted content.
            4. Use complete_content_overview tool to finalize.
            """,
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            max_iter=20,
            tools=all_tools,
        )

    def process_pdf_task(self) -> Task:
        """处理PDF并创建structured content"""
        return Task(
            description="""Process PDF file and create abstract section only, then finalize the structured content overview.""",
            agent=self.pdf_processor(),
            expected_output="section name",
        )

    def crew(self) -> Crew:
        """创建PDF处理crew"""
        return Crew(
            agents=[self.pdf_processor()],
            tasks=[self.process_pdf_task()],
            process=Process.sequential,
            verbose=True,
        )
