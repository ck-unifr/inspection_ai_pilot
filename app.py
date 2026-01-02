# src/app.py
"""
uv run streamlit run src/app.py
"""

import streamlit as st
import os
import time
import subprocess
from dotenv import load_dotenv
from langchain_community.callbacks.streamlit import StreamlitCallbackHandler

from src.core.agent import InspectionAgent
from src.services.mock_api import InstrumentMockAPI
from src.config import Config

load_dotenv()

# -----------------------------------------------------------------------------
# 1. 页面配置
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="工程检测智能领航员",
    page_icon="🏗️",
    layout="wide",
)

st.markdown(
    """
<style>
    .block-container {padding-top: 2rem;}
    .stChatMessage {padding: 0.5rem;}
    textarea {font-family: monospace;} 
</style>
""",
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# 2. 侧边栏
# -----------------------------------------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/color/96/engineer.png", width=70)
    st.title("🔧 控制台")
    st.caption(f"Model: {Config.MODEL_NAME}")
    st.divider()

    # --- API Key ---
    if not os.getenv("DASHSCOPE_API_KEY"):
        st.warning("⚠️ 缺失 API Key")
        key = st.text_input("DashScope Key", type="password")
        if key:
            os.environ["DASHSCOPE_API_KEY"] = key

    # --- 设备选择 ---
    st.markdown("### 📡 设备接入")

    # 动态获取 Mock 数据中的 key 作为选项
    all_scenarios = InstrumentMockAPI.get_all_scenarios()
    # 格式化选项显示
    options = [f"{k} ({v['component_id']})" for k, v in all_scenarios.items()]
    options.append("DEV-ERR-01 (故障设备)")

    selected_device = st.selectbox("选择信号源", options)
    device_id = selected_device.split(" ")[0]

    st.divider()

    # --- 知识库管理 (优化版) ---
    st.markdown("### 📝 标准库管理")
    with st.expander("查看/编辑 JGJ/T 23", expanded=False):
        # 读取文件
        content = ""
        if Config.SOURCE_FILE.exists():
            with open(Config.SOURCE_FILE, "r", encoding="utf-8") as f:
                content = f.read()

        # 使用 Tabs 分离 预览 和 编辑
        tab_view, tab_edit = st.tabs(["👁️ 预览 (渲染)", "✏️ 编辑 (源码)"])

        with tab_view:
            st.caption("Markdown 渲染效果 (表格清晰可见)")
            # 这里会正确渲染表格
            st.markdown(content)

        with tab_edit:
            new_content = st.text_area("编辑器", value=content, height=400)
            if st.button("💾 保存并更新向量库", use_container_width=True):
                if new_content != content:
                    with open(Config.SOURCE_FILE, "w", encoding="utf-8") as f:
                        f.write(new_content)

                    try:
                        with st.spinner("正在重构知识库..."):
                            subprocess.run(
                                ["python", "scripts/build_db.py"], check=True
                            )
                        st.success("更新完成！")
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"更新失败: {e}")
                else:
                    st.info("内容未变更")

    st.divider()
    if st.button("🔄 重置会话"):
        st.session_state.messages = []
        st.rerun()

# -----------------------------------------------------------------------------
# 3. 主界面
# -----------------------------------------------------------------------------
st.title("🏗️ 工程检测智能领航员")
st.markdown("根据 **JGJ/T 23-2011** 规范，自动对回弹法检测数据进行合规性判定。")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "检测链路已连接。请下达指令。"}
    ]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# -----------------------------------------------------------------------------
# 4. 交互逻辑
# -----------------------------------------------------------------------------
preset_prompt = f"拉取设备 {device_id} 的数据，基于 JGJ/T 23 判断是否合格？"

# 快捷按钮
if st.button(f"🚀 一键分析: {device_id}", type="primary", use_container_width=True):
    user_input = preset_prompt
else:
    user_input = st.chat_input("请输入指令...")

if user_input:
    if not os.getenv("DASHSCOPE_API_KEY"):
        st.error("请配置 API Key")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": user_input})
    st.chat_message("user").write(user_input)

    with st.chat_message("assistant"):
        st_callback = StreamlitCallbackHandler(st.container())
        try:
            agent = InspectionAgent()
            response = agent.agent_executor.invoke(
                {"input": user_input}, config={"callbacks": [st_callback]}
            )
            st.write(response["output"])
            st.session_state.messages.append(
                {"role": "assistant", "content": response["output"]}
            )
        except Exception as e:
            st.error(f"Error: {e}")

# -----------------------------------------------------------------------------
# 5. Debug / 数据监控面板 (新增所有数据展示)
# -----------------------------------------------------------------------------
st.divider()
with st.expander("🔍 数据监控中心 (Data Monitor)", expanded=True):

    tab_current, tab_all = st.tabs(["📍 当前设备实时流", "📚 所有可用设备快照"])

    with tab_current:
        cols = st.columns(4)
        data = InstrumentMockAPI.fetch_latest_record(device_id)

        if data.get("status") == "success":
            d = data["data"]
            cols[0].metric("设备编号", data["device_id"])
            cols[1].metric("强度设计", d["design_strength"])
            cols[2].metric("回弹值 (Rm)", d["avg_rebound_value"])
            cols[3].metric("碳化深度 (dm)", d["carbonation_depth"])
            st.json(data)
        else:
            st.error("无法获取该设备数据")

    with tab_all:
        st.caption("Mock API 中预设的所有测试场景数据：")
        st.json(InstrumentMockAPI.get_all_scenarios())
