# src/core/agent.py
from langchain_community.chat_models import ChatTongyi
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
from src.config import Config
from src.core.tools import get_instrument_data, search_standard_knowledge
from src.core.prompts import SYSTEM_PROMPT


class InspectionAgent:
    def __init__(self):
        self.llm = ChatTongyi(
            model=Config.MODEL_NAME,  # qwen-turbo
            api_key=Config.DASHSCOPE_API_KEY,
            temperature=0.0,
        )

        # 定义工具集
        self.tools = [get_instrument_data, search_standard_knowledge]

        # 定义 Prompt
        # 关键：赋予 Agent 角色，让它知道如何串联两个工具
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    SYSTEM_PROMPT,
                ),
                ("human", "{input}"),
                ("placeholder", "{agent_scratchpad}"),
            ]
        )

        # 创建 Agent
        agent = create_tool_calling_agent(self.llm, self.tools, prompt)
        self.agent_executor = AgentExecutor(agent=agent, tools=self.tools, verbose=True)

    def run(self, user_input):
        return self.agent_executor.invoke({"input": user_input})
