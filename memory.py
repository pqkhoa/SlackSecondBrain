import os
from datetime import datetime
import config

def _topic_path(topic: str) -> str:
    os.makedirs(config.VAULT_DIR, exist_ok=True)
    return os.path.join(config.VAULT_DIR, f"{topic}.md")


def append_to_memory(topic: str, content: str, source_user: str = ""):
    """Append a new entry to the topic's memory file."""
    if topic not in config.TOPICS:
        topic = "ideas"  # fallback

    path = _topic_path(topic)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    source_label = f" (from @{source_user})" if source_user else ""

    entry = f"\n## {timestamp}{source_label}\n{content.strip()}\n"

    with open(path, "a", encoding="utf-8") as f:
        # Write header if file is new
        if os.path.getsize(path) == 0 if os.path.exists(path) else True:
            pass
        f.write(entry)

    print(f"  💾 Saved to memory: [{topic}] {content[:60]}...")


def read_memory(topic: str) -> str:
    """Read a single topic memory file."""
    path = _topic_path(topic)
    if not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def get_all_memory() -> str:
    """
    Return all memory files concatenated.
    Used to give Claude full context when drafting replies.
    """
    parts = []
    for topic in config.TOPICS:
        content = read_memory(topic)
        if content.strip():
            parts.append(f"# [{topic.upper()}]\n{content}")
    return "\n\n---\n\n".join(parts) if parts else "No memory yet."


def list_topics_with_size() -> dict:
    """Return topics and their entry counts (useful for debugging)."""
    result = {}
    for topic in config.TOPICS:
        path = _topic_path(topic)
        if os.path.exists(path):
            with open(path, "r") as f:
                lines = f.readlines()
            entries = sum(1 for l in lines if l.startswith("## "))
            result[topic] = entries
        else:
            result[topic] = 0
    return result
