import os
import re
from dotenv import load_dotenv

load_dotenv()

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from claude import classify_and_save, draft_reply, draft_reply_to_target
from memory import get_all_memory
import config

app = App(token=os.environ["SLACK_BOT_TOKEN"])

# Cache bot user ID on startup
BOT_USER_ID = None

def get_bot_user_id():
    global BOT_USER_ID
    if not BOT_USER_ID:
        BOT_USER_ID = app.client.auth_test()["user_id"]
    return BOT_USER_ID


# ─────────────────────────────────────────────
# EVENT: Message received
# ─────────────────────────────────────────────
@app.event("message")
def handle_message(event, say, client):
    bot_id = get_bot_user_id()
    text = event.get("text", "")
    user = event.get("user", "")
    channel = event.get("channel", "")
    thread_ts = event.get("thread_ts") or event.get("ts")

    # Ignore bot's own messages
    if user == bot_id or event.get("bot_id"):
        return

    # ── /reply command (you → bot) ──────────────
    # Usage: /reply @username <instruction>
    # Example: /reply @john Tell him I'll join at 3pm
    if text.strip().startswith("/reply"):
        handle_reply_command(text, channel, thread_ts, say, client)
        return

    # ── @mention or DM → auto-reply ─────────────
    is_dm = channel.startswith("D")
    is_mentioned = f"<@{bot_id}>" in text

    if is_dm or is_mentioned:
        memory_context = get_all_memory()
        clean_text = re.sub(r"<@\w+>", "", text).strip()
        reply = draft_reply(clean_text, memory_context, user)
        say(text=reply, thread_ts=thread_ts)

        # Also save to memory
        classify_and_save(text, user)
        return

    # ── Everything else → silent memory save ────
    classify_and_save(text, user)


def handle_reply_command(text, channel, thread_ts, say, client):
    """
    Parse /reply command and send a reply to the target user or thread.
    Syntax: /reply @username <your instruction>
    """
    # Extract target user and instruction
    match = re.match(r"/reply\s+<@(\w+)>\s+(.*)", text, re.DOTALL)
    if not match:
        say(
            text="Usage: `/reply @username <instruction>`\nExample: `/reply @john Tell him I'll join at 3pm`",
            thread_ts=thread_ts,
        )
        return

    target_user_id = match.group(1)
    instruction = match.group(2).strip()

    memory_context = get_all_memory()
    reply = draft_reply_to_target(instruction, memory_context, target_user_id)

    # Open DM with target user and send
    dm = client.conversations_open(users=target_user_id)
    dm_channel = dm["channel"]["id"]
    client.chat_postMessage(
        channel=dm_channel,
        text=reply,
        username=f"{config.BOT_DISPLAY_NAME} (via AI)",
    )
    say(text=f"✅ Replied to <@{target_user_id}>:\n> {reply}", thread_ts=thread_ts)


# ─────────────────────────────────────────────
# START
# ─────────────────────────────────────────────
if __name__ == "__main__":
    print("🧠 Slack Second Brain is running...")
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()
