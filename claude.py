import os
import json
import anthropic
from memory import append_to_memory
import config

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
MODEL = "claude-sonnet-4-20250514"


def classify_and_save(text: str, source_user: str = ""):
    """
    Ask Claude if a message is worth saving, and if so, which topic.
    Silently saves to memory if relevant.
    """
    if len(text.strip()) < config.MIN_MESSAGE_LENGTH:
        return

    topics_list = ", ".join(config.TOPICS)

    response = client.messages.create(
        model=MODEL,
        max_tokens=200,
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
        messages=[{"role": "user", "content": text}],
    )

    raw = response.content[0].text.strip()

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
    """
    Draft a reply to an @mention or DM using memory context.
    """
    from_label = f"from Slack user ID {from_user}" if from_user else "from a Slack user"

    response = client.messages.create(
        model=MODEL,
        max_tokens=300,
        system=config.REPLY_STYLE,
        messages=[
            {
                "role": "user",
                "content": (
                    f"Memory context about {config.YOUR_NAME}:\n{memory_context}\n\n"
                    f"---\n\n"
                    f"Incoming message {from_label}:\n{incoming_message}\n\n"
                    f"Draft a reply as {config.YOUR_NAME}."
                ),
            }
        ],
    )

    return response.content[0].text.strip()


def draft_reply_to_target(
    instruction: str, memory_context: str, target_user_id: str
) -> str:
    """
    Draft a reply based on an explicit instruction from the user.
    Example instruction: "Tell him I'll join at 3pm"
    """
    response = client.messages.create(
        model=MODEL,
        max_tokens=300,
        system=config.REPLY_STYLE,
        messages=[
            {
                "role": "user",
                "content": (
                    f"Memory context about {config.YOUR_NAME}:\n{memory_context}\n\n"
                    f"---\n\n"
                    f"{config.YOUR_NAME} wants to send a message to Slack user <@{target_user_id}>.\n"
                    f"Instruction from {config.YOUR_NAME}: {instruction}\n\n"
                    f"Draft the message as {config.YOUR_NAME}."
                ),
            }
        ],
    )

    return response.content[0].text.strip()
