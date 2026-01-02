from dotenv import load_dotenv
from langchain_community.chat_models import ChatZhipuAI


def test():
    # 1. 加载 .env
    load_dotenv()

    # 2. 初始化模型
    # 注意：通常 API 这里的名字是小写的 'glm-4v-flash'
    # 如果官方明确给你的 model code 是 'glm-4.6v-flash'，请直接替换下面的字符串
    llm = ChatZhipuAI(model="glm-4v-flash", temperature=0.5)

    # 3. 调用
    try:
        response = llm.invoke("介绍一下GLM-4V-Flash这个模型有什么特点？")
        print(response.content)
    except Exception as e:
        print(f"调用失败: {e}")


if __name__ == "__main__":
    test()
    print("🎉 测试完成！")
