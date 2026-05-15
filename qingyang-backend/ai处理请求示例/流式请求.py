import uuid
from openai import OpenAI

from 同步请求 import request_id

AppKey = "YOUR_API_KEY_HERE"
BASE_URL = "https://api-ai.vivo.com.cn/v1"
MODEL_NAME = "Doubao-Seed-2.0-pro"


client = OpenAI(
    api_key=AppKey,
    base_url=BASE_URL,
    default_headers={
        "Content-Type": "application/json; charset=utf-8"
    },
    default_query={"request_id": request_id}
)

def stream_chat():
    request_id = str(uuid.uuid4())
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "user", "content": "你好，请介绍下你自己"}
            ],
            temperature=0.7,
            max_tokens=1024,
            stream=True,
            stream_options={"include_usage": True}
        )

        full_content = ""
        usage = None
        print("流式输出：\n")
        for chunk in response:
            if hasattr(chunk, 'usage') and chunk.usage:
                usage = chunk.usage
                continue
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta.content
            if delta:
                full_content += delta
                print(delta, end="", flush=True)
        print(f"\n\n===== 完整回复 =====\n{full_content}")
        if usage:
            print(f"\n===== Token消耗 =====\n输入：{usage.prompt_tokens}\n输出：{usage.completion_tokens}\n总计：{usage.total_tokens}")
        return full_content

    except Exception as e:
        print(f"请求出错，request_id={request_id}，错误信息：{str(e)}")


if __name__ == "__main__":
    stream_chat()