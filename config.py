# ─────────────────────────────────────────────
# config.py — Edit this file to customize your bot
# ─────────────────────────────────────────────

# Model hosted on inference.nvidia.com — change to any available model
# Examples: "meta/llama-3.1-405b-instruct", "mistralai/mistral-large-2-instruct"
MODEL = "anthropic/claude-opus-4-5"

# Your name (used in reply drafts)
YOUR_NAME = "Darren"

# How the bot signs off in Slack
BOT_DISPLAY_NAME = "Darren"

# Memory topics — the bot will classify messages into these
# Add or remove topics freely. Each becomes a .md file in your vault.
TOPICS = [
    "ai",
    "work",
    "ideas",
    "productivity",
    "nvidia",
    "personal",
]

# Vault directory — where memory .md files are stored
# Change this to your actual Obsidian vault path if you want
VAULT_DIR = "vault"

# Minimum message length to bother saving (ignore noise)
MIN_MESSAGE_LENGTH = 20

# Reply style instruction fed to Claude
REPLY_STYLE = (
    f"You are drafting a Slack reply on behalf of {YOUR_NAME}. "
    "Write in a concise, direct, friendly tone. "
    "Sound like a real person, not an AI. "
    "Use the memory context provided to make the reply relevant and personal. "
    "Never say you are an AI. Keep it short — 1 to 3 sentences unless more is needed."
)
