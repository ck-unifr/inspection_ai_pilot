# src/app.py
"""
uv run streamlit run src/app.py
"""

import streamlit as st
import os
import subprocess  # 用于执行重建脚本
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

st.markdown(
    """
<style>
    .block-container {padding-top: 2rem; padding-bottom: 2rem;}
    .stAlert {margin-top: 1rem;}
    .stChatMessage {padding: 0.5rem;}
    /* 让文本域不仅显示更清晰，还带有代码字体 */
    textarea {font-family: monospace;}
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

    # --- API Key 配置 ---
    if not os.getenv("DASHSCOPE_API_KEY"):
        st.warning("⚠️ 未检测到环境变量")
        api_key_input = st.text_input("请输入 DashScope API Key", type="password")
        if api_key_input:
            os.environ["DASHSCOPE_API_KEY"] = api_key_input
            st.success("Key 已加载")

    # --- 模拟 IoT 环境 ---
    st.markdown("### 📡 模拟 IoT 环境")
    selected_device = st.selectbox(
        "选择接入设备 (Mock)",
        ["DEV-2026-A (梁 KL-3-15)", "DEV-2026-B (柱 KZ-1-02)", "DEV-ERR-01 (故障设备)"],
        index=0,
    )
    device_id = selected_device.split(" ")[0]

    st.divider()

    # =========================================================================
    # [新增功能] 知识库文件管理与热更新
    # =========================================================================
    st.markdown("### 📝 知识库管理")
    with st.expander("查看/编辑 标准文件", expanded=False):
        st.caption(f"源文件: {Config.SOURCE_FILE.name}")

        # 1. 读取当前文件内容
        current_content = ""
        if Config.SOURCE_FILE.exists():
            with open(Config.SOURCE_FILE, "r", encoding="utf-8") as f:
                current_content = f.read()
        else:
            st.error("找不到源文件！")

        # 2. 编辑区域
        new_content = st.text_area(
            "Markdown 内容编辑器",
            value=current_content,
            height=300,
            help="在这里修改规范条文，点击下方按钮保存并生效。",
        )

        # 3. 保存并重建向量库
        if st.button("💾 保存并重建向量库", use_container_width=True):
            if new_content != current_content:
                # A. 保存文件
                with open(Config.SOURCE_FILE, "w", encoding="utf-8") as f:
                    f.write(new_content)
                st.toast("文件已保存", icon="💾")

                # B. 执行重建脚本 (调用 scripts/build_db.py)
                try:
                    with st.spinner("正在重新向量化 (Embedding)..."):
                        # 使用 subprocess 调用之前的脚本，确保环境隔离
                        # 假设当前在项目根目录运行
                        result = subprocess.run(
                            ["python", "scripts/build_db.py"],
                            capture_output=True,
                            text=True,
                            check=True,
                        )
                    st.success("✅ 知识库更新完成！Agent 现已掌握最新标准。")
                    time.sleep(1)
                    st.rerun()  # 刷新页面
                except subprocess.CalledProcessError as e:
                    st.error(f"构建失败: {e.stderr}")
            else:
                st.info("内容未发生变化，无需更新。")

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

# 初始化消息记录
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
# 4. 交互逻辑
# -----------------------------------------------------------------------------
preset_prompt = f"请拉取设备 {device_id} 的数据，并根据 JGJ/T 23 标准判断构件是否合格？如果不合格请说明原因。"

# 输入区域
col1, col2 = st.columns([5, 1])
with col1:
    user_input = st.chat_input("请输入指令...")
with col2:
    # 放置在底部的快捷按钮逻辑稍作调整，为了布局好看，通常 chat_input 独占一行
    # 这里我们只保留 chat_input，或者把快捷按钮放在上面。
    pass

# 为了方便，我们在上方显示快捷按钮
if st.button(
    f"🚀 一键执行: {preset_prompt}", type="secondary", use_container_width=True
):
    user_input = preset_prompt

if user_input:
    if not os.getenv("DASHSCOPE_API_KEY"):
        st.error("请先在侧边栏配置阿里云 API Key！")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": user_input})
    st.chat_message("user").write(user_input)

    with st.chat_message("assistant"):
        try:
            # 每次请求都重新实例化 Agent，确保它能读取到（可能刚刚更新过的）向量库
            agent_instance = InspectionAgent()
        except Exception as e:
            st.error(f"Agent 初始化失败: {str(e)}")
            st.stop()

        st_callback = StreamlitCallbackHandler(st.container(), expand_new_thoughts=True)

        try:
            response = agent_instance.agent_executor.invoke(
                {"input": user_input}, config={"callbacks": [st_callback]}
            )
            output_text = response["output"]
            st.write(output_text)
            st.session_state.messages.append(
                {"role": "assistant", "content": output_text}
            )
        except Exception as e:
            st.error(f"分析过程中发生错误: {str(e)}")

# -----------------------------------------------------------------------------
# 5. Debug 区域
# -----------------------------------------------------------------------------
with st.expander("🔍 Debug: 查看后台真实数据流"):
    st.caption("这是 AI 实际上通过 Tool 拿到的 JSON 数据。")
    mock_data = InstrumentMockAPI.fetch_latest_record(device_id)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("设备编号", mock_data["device_id"])
    with col2:
        st.metric("平均回弹值 (Rm)", mock_data["data"]["avg_rebound_value"])
    with col3:
        st.metric("碳化深度 (dm)", mock_data["data"]["carbonation_depth"])
    st.json(mock_data)
