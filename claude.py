import os
import json
from openai import OpenAI
from memory import append_to_memory
import config

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.environ.get("NVIDIA_API_KEY"),
)


def _chat(system: str, user: str, max_tokens: int) -> str:
    response = client.chat.completions.create(
        model=config.MODEL,
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    return response.choices[0].message.content.strip()


def classify_and_save(text: str, source_user: str = ""):
    if len(text.strip()) < config.MIN_MESSAGE_LENGTH:
        return

    topics_list = ", ".join(config.TOPICS)

    raw = _chat(
        system=(
            "You are a memory classifier. Given a Slack message, decide:\n"
            "1. Is it worth saving as a memory? (ignore greetings, noise, trivial chat)\n"
            "2. If yes, which topic does it belong to?\n\n"
            f"Available topics: {topics_list}\n\n"
            "Respond ONLY with valid JSON in this exact format:\n"
            '{"save": true, "topic": "ai", "summary": "concise 1-sentence summary"}\n'
            "or\n"
            '{"save": false}\n'
            "No other text."
        ),
        user=text,
        max_tokens=200,
    )

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        print(f"  ⚠️  Could not parse classifier response: {raw}")
        return

    if result.get("save"):
        topic = result.get("topic", "ideas")
        summary = result.get("summary", text[:200])
        append_to_memory(topic, summary, source_user)


def draft_reply(incoming_message: str, memory_context: str, from_user: str = "") -> str:
    from_label = f"from Slack user ID {from_user}" if from_user else "from a Slack user"

    return _chat(
        system=config.REPLY_STYLE,
        user=(
            f"Memory context about {config.YOUR_NAME}:\n{memory_context}\n\n"
            f"---\n\n"
            f"Incoming message {from_label}:\n{incoming_message}\n\n"
            f"Draft a reply as {config.YOUR_NAME}."
        ),
        max_tokens=300,
    )


def draft_reply_to_target(
    instruction: str, memory_context: str, target_user_id: str
) -> str:
    return _chat(
        system=config.REPLY_STYLE,
        user=(
            f"Memory context about {config.YOUR_NAME}:\n{memory_context}\n\n"
            f"---\n\n"
            f"{config.YOUR_NAME} wants to send a message to Slack user <@{target_user_id}>.\n"
            f"Instruction from {config.YOUR_NAME}: {instruction}\n\n"
            f"Draft the message as {config.YOUR_NAME}."
        ),
        max_tokens=300,
    )
