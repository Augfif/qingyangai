import uuid
import base64
from openai import OpenAI

from 同步请求 import request_id

# 配置参数
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


# 本地图片转base64工具函数，传本地图时使用
def image_to_base64(image_path):
    with open(image_path, "rb") as f:
        base64_str = base64.b64encode(f.read()).decode("utf-8")
        return f"data:image/jpeg;base64,{base64_str}"


def sync_image_chat():
    request_id = str(uuid.uuid4())
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "请描述这张图片里的内容，越详细越好"},
                        {"type": "image_url", "image_url": {
                            # 方式1：在线公共图片URL
                            "url": "https://userglobal-vivofs.vivo.com.cn/useravatar/20210715141352/cabdc22b094447d79cd1c0be2664af66.jpg"
                            # 方式2：本地图片转base64（需要取消下行注释并注释掉上方URL）
                            # 需注意：传入Base64编码遵循格式 data:image/<IMAGE_FORMAT>;base64,{base64_image}：
                            # PNG图片："url":  f"data:image/png;base64,{base64_image}"
                            # JPEG图片："url":  f"data:image/jpeg;base64,{base64_image}"
                            # WEBP图片："url":  f"data:image/webp;base64,{base64_image}"
                            # "url":  f"data:image/<IMAGE_FORMAT>;base64,{base64_image}"
                            # "url": image_to_base64("./test.jpg")
                        }}
                    ]
                }
            ],
            temperature=0.3,
            max_tokens=2048,
            stream=False,

        )
        content = response.choices[0].message.content
        usage = response.usage

        print(f"===== 图片解析结果 =====\n{content}")
        print(
            f"\n===== Token消耗 =====\n输入：{usage.prompt_tokens}\n输出：{usage.completion_tokens}\n总计：{usage.total_tokens}")
        return content

    except Exception as e:
        print(f"请求出错，request_id={request_id}，错误信息：{str(e)}")


if __name__ == "__main__":
    sync_image_chat()
