from langchain_community.chat_models import ChatTongyi
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
from src.config import Config
from src.core.tools import get_instrument_data, search_standard_knowledge


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
                    """你是一名资深的工程检测数据分析师。
            你的任务是自动化处理检测数据并生成合规性报告。
            
            请遵循以下工作流：
            1. 首先，使用 `get_instrument_data` 工具获取最新的仪器原始数据。
            2. 分析获取到的数据（关注回弹值、碳化深度、设计强度）。
            3. 接着，使用 `search_standard_knowledge` 工具去标准库中查找对应的强度换算表。
            4. 结合原始数据和标准条文，进行强度推算和合规性判定（实际强度是否 >= 设计强度）。
            5. 最后输出完整的分析结论。
            """,
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
