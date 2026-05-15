import uuid

import requests
from openai import OpenAI

AppKey = "YOUR_API_KEY_HERE"
BASE_URL = "https://api-ai.vivo.com.cn/v1"
MODEL_NAME = "Doubao-Seed-2.0-pro"

request_id = str(uuid.uuid4())
client = OpenAI(
    api_key=AppKey,
    base_url=BASE_URL,
    default_headers={
        "Content-Type": "application/json; charset=utf-8"
    },
    default_query={"request_id": request_id}
)


def sync_chat():
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "user", "content": "你好，请介绍下你自己"}
            ],
            temperature=0.7,
            max_tokens=1024,
            stream=False,
        )
        content = response.choices[0].message.content
        print(f"回复内容：{content}")
        return content
    except Exception as e:
        print(f"请求出错，request_id={request_id}，错误信息：{str(e)}")


if __name__ == "__main__":
    sync_chat()