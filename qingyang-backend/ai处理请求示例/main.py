import subprocess
import json
import base64
import uuid
from openai import OpenAI
import os

# --- Configuration ---
SPEECH_RECOGNITION_SCRIPT = 'ai_speech_input_client.py'
AUDIO_CONFIG = 'audio.conf'
IMAGE_PATH = '图片/img.png'

# --- Image Understanding Configuration ---
AppKey = "YOUR_API_KEY_HERE"
BASE_URL = "https://api-ai.vivo.com.cn/v1"
MODEL_NAME = "Doubao-Seed-2.0-pro"


def run_speech_recognition():
    """
    Runs the speech recognition script and returns the recognized text.
    """
    command = ['python', SPEECH_RECOGNITION_SCRIPT, AUDIO_CONFIG]
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True, encoding='utf-8')
        output_lines = result.stdout.strip().split('\n')
        for line in output_lines:
            if '#' in line and line.startswith('./test.wav'):
                parts = line.split('#')
                if len(parts) > 1:
                    print(f"Recognized text: {parts[1]}")
                    return parts[1]
        print("Error: Could not find recognized text in the output.")
        return None
    except subprocess.CalledProcessError as e:
        print(f"Error running speech recognition script: {e}")
        print(f"Stderr: {e.stderr}")
        return None
    except FileNotFoundError:
        print(f"Error: The script '{SPEECH_RECOGNITION_SCRIPT}' was not found.")
        return None


def image_to_base64(image_path):
    """
    Converts a local image file to a base64 encoded string.
    """
    try:
        with open(image_path, "rb") as f:
            base64_str = base64.b64encode(f.read()).decode("utf-8")
            # Determine image format from file extension
            image_format = os.path.splitext(image_path)[1][1:].lower()
            if image_format == 'jpg':
                image_format = 'jpeg'
            return f"data:image/{image_format};base64,{base64_str}"
    except FileNotFoundError:
        print(f"Error: Image file not found at {image_path}")
        return None


def get_ai_response(text_prompt, image_path):
    """
    Gets a response from the AI based on a text prompt and an image.
    """
    if not text_prompt:
        print("Error: No text prompt provided.")
        return

    base64_image = image_to_base64(image_path)
    if not base64_image:
        return

    client = OpenAI(
        api_key=AppKey,
        base_url=BASE_URL,
        default_headers={"Content-Type": "application/json; charset=utf-8"},
        default_query={"request_id": str(uuid.uuid4())}
    )

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": text_prompt},
                        {"type": "image_url", "image_url": {"url": base64_image}}
                    ]
                }
            ],
            temperature=0.3,
            max_tokens=2048,
            stream=False,
        )
        content = response.choices[0].message.content
        usage = response.usage

        print(f"\n===== AI Response =====\n{content}")
        print(
            f"\n===== Token Usage =====\nInput: {usage.prompt_tokens}\nOutput: {usage.completion_tokens}\nTotal: {usage.total_tokens}")

    except Exception as e:
        print(f"Error during AI request: {str(e)}")


def main():
    """
    Main function to orchestrate speech recognition and image understanding.
    """
    # Step 1: Get text from speech
    recognized_text = run_speech_recognition()

    if recognized_text:
        # Step 2: Get AI response based on text and image
        get_ai_response(recognized_text, IMAGE_PATH)


if __name__ == "__main__":
    main()

