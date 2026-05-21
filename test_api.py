import os
from dotenv import load_dotenv
from openai import OpenAI
import config

load_dotenv()

def test_nvidia():
    client = OpenAI(
        base_url="https://inference-api.nvidia.com/v1",
        api_key=os.environ.get("NVIDIA_API_KEY"),
    )
    response = client.chat.completions.create(
        model=config.MODEL,
        max_tokens=50,
        messages=[{"role": "user", "content": "Reply with just: API working"}],
    )
    print(f"✓ NVIDIA API: {response.choices[0].message.content.strip()}")

def test_slack():
    from slack_sdk import WebClient
    client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))
    result = client.auth_test()
    print(f"✓ Slack Bot Token: connected as @{result['user']} in workspace {result['team']}")

if __name__ == "__main__":
    print("Testing APIs...\n")
    try:
        test_nvidia()
    except Exception as e:
        print(f"✗ NVIDIA API: {e}")
    try:
        test_slack()
    except Exception as e:
        print(f"✗ Slack Bot Token: {e}")
