# src/app.py
"""
uv run streamlit run app.pyDocstring for app
"""

import streamlit as st
import os
import time
from dotenv import load_dotenv
from langchain_community.callbacks.streamlit import StreamlitCallbackHandler

# 导入自定义模块
from src.core.agent import InspectionAgent
from src.services.mock_api import InstrumentMockAPI
from src.config import Config

# 加载环境变量
load_dotenv()

# -----------------------------------------------------------------------------
# 1. 页面基础配置
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="工程检测智能领航员 | Inspection AI Pilot",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 自定义一些 CSS 让界面更紧凑专业
st.markdown(
    """
<style>
    .block-container {padding-top: 2rem; padding-bottom: 2rem;}
    .stAlert {margin-top: 1rem;}
    /* 调整思考过程的容器样式 */
    .stChatMessage {padding: 0.5rem;}
</style>
""",
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# 2. 侧边栏：控制台与环境模拟
# -----------------------------------------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/color/96/engineer.png", width=80)
    st.title("🔧 领航员控制台")
    st.caption(f"Model: {Config.MODEL_NAME}")

    st.divider()

    # API Key 配置 (防止 .env 没配好时的备用方案)
    if not os.getenv("DASHSCOPE_API_KEY"):
        st.warning("⚠️ 未检测到环境变量")
        api_key_input = st.text_input("请输入 DashScope API Key", type="password")
        if api_key_input:
            os.environ["DASHSCOPE_API_KEY"] = api_key_input
            st.success("Key 已加载")

    st.markdown("### 📡 模拟 IoT 环境")
    # 模拟选择不同的设备/构件
    selected_device = st.selectbox(
        "选择接入设备 (Mock)",
        ["DEV-2026-A (梁 KL-3-15)", "DEV-2026-B (柱 KZ-1-02)", "DEV-ERR-01 (故障设备)"],
        index=0,
    )

    # 提取设备ID
    device_id = selected_device.split(" ")[0]

    st.markdown("### 📚 标准库状态")
    st.info("✅ JGJ/T 23-2011 (已向量化)")

    st.divider()
    if st.button("🔄 重置会话"):
        st.session_state.messages = []
        st.rerun()

# -----------------------------------------------------------------------------
# 3. 主界面区域
# -----------------------------------------------------------------------------
st.title("🏗️ 工程检测智能领航员 (Agent Demo)")
st.markdown(
    f"""
**当前任务场景**：检测员在现场完成了对构件的**回弹法检测**，数据已上传至 IoT 云端。
你需要指挥 AI 智能体拉取数据，并依据 **JGJ/T 23-2011** 规范自动进行合规性判定。
"""
)

# 用于展示对话历史
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "你好！我是检测智能助手。请告诉我设备编号，我将为您自动生成合规性报告。",
        }
    ]

# 展示历史消息
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# -----------------------------------------------------------------------------
# 4. 交互逻辑 (核心)
# -----------------------------------------------------------------------------
# 定义预设指令（方便演示，不用每次都打字）
preset_prompt = f"请拉取设备 {device_id} 的数据，并根据 JGJ/T 23 标准判断构件是否合格？如果不合格请说明原因。"

# 获取用户输入 (可以是点击按钮，也可以是手动输入)
if st.button("🚀 一键执行自动化分析", type="primary", use_container_width=True):
    user_input = preset_prompt
else:
    user_input = st.chat_input("请输入指令，例如：查询设备 DEV-2026-A 的数据...")

if user_input:
    # 1. 检查 API Key
    if not os.getenv("DASHSCOPE_API_KEY"):
        st.error("请先在侧边栏配置阿里云 API Key！")
        st.stop()

    # 2. 显示用户消息
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.chat_message("user").write(user_input)

    # 3. AI 执行过程
    with st.chat_message("assistant"):
        # 实例化 Agent
        try:
            agent_instance = InspectionAgent()
        except Exception as e:
            st.error(f"Agent 初始化失败: {str(e)}")
            st.stop()

        # --- 关键点：可视化 Agent 的思考过程 ---
        st_callback = StreamlitCallbackHandler(st.container(), expand_new_thoughts=True)

        try:
            # 执行 Agent，并将回调传给 run 方法
            # 注意：langchain 的 invoke 方法支持 config 参数传入 callbacks
            response = agent_instance.agent_executor.invoke(
                {"input": user_input}, config={"callbacks": [st_callback]}
            )

            output_text = response["output"]
            st.write(output_text)

            # 保存助手回复
            st.session_state.messages.append(
                {"role": "assistant", "content": output_text}
            )

        except Exception as e:
            st.error(f"分析过程中发生错误: {str(e)}")

    # -------------------------------------------------------------------------
    # 5. "底牌"展示 (向面试官证明真实性)
    # -------------------------------------------------------------------------
    with st.expander("🔍 Debug: 查看后台真实数据流 (Mock API Response)"):
        st.caption("这是 AI 实际上通过 Tool 拿到的 JSON 数据，证明它没有瞎编数字。")

        # 模拟调用一下 API 展示给用户看
        mock_data = InstrumentMockAPI.fetch_latest_record(device_id)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("设备编号", mock_data["device_id"])
        with col2:
            st.metric("平均回弹值 (Rm)", mock_data["data"]["avg_rebound_value"])
        with col3:
            st.metric("碳化深度 (dm)", mock_data["data"]["carbonation_depth"])

        st.json(mock_data)
