# 🧠 Slack Second Brain

A personal AI assistant that runs in Slack — silently capturing knowledge from conversations into a local Markdown vault, and replying on your behalf when triggered.

Built with [Slack Bolt](https://slack.dev/bolt-python/) and the [Anthropic Claude API](https://docs.anthropic.com).

---

## What It Does

| Trigger | Behavior |
|---|---|
| Any message in channels the bot is in | Claude classifies it — if relevant, saves a summary to your memory vault |
| Someone @mentions you or DMs you | Bot auto-replies using your memory context |
| You send `/reply @user <instruction>` | Bot drafts and sends a reply to that user on your behalf |

---

## Architecture

```
Slack Event
     │
     ▼
main.py (Slack Bolt / Socket Mode)
     │
     ├── classify_and_save() ──→ claude.py ──→ memory.py ──→ vault/<topic>.md
     │
     └── draft_reply() ────────→ claude.py (reads all memory) ──→ Slack reply
```

Memory is stored as plain Markdown files — one per topic — making it fully portable and ready for any AI/RAG pipeline.

---

## Project Structure

```
slack-second-brain/
├── main.py            # Slack bot, event handlers
├── claude.py          # Claude API: classify messages, draft replies
├── memory.py          # Read/write Markdown memory files
├── config.py          # Your topics, name, reply style — edit this
├── requirements.txt
├── .env.example
├── .gitignore
└── vault/             # Memory files live here (git-ignored)
    ├── ai.md
    ├── work.md
    └── ...
```

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/slack-second-brain.git
cd slack-second-brain
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Create your `.env` file

```bash
cp .env.example .env
```

Fill in your credentials:

```
SLACK_BOT_TOKEN=xoxb-...
SLACK_APP_TOKEN=xapp-...
ANTHROPIC_API_KEY=sk-ant-...
```

### 4. Configure your topics

Edit `config.py` to set your name and the topics you care about:

```python
YOUR_NAME = "Darren"

TOPICS = [
    "ai",
    "work",
    "ideas",
    "productivity",
    "nvidia",
    "personal",
]
```

Each topic becomes a `vault/<topic>.md` memory file.

### 5. Slack App Setup

In [api.slack.com/apps](https://api.slack.com/apps):

**Socket Mode** → Enable, create app-level token with `connections:write` scope → save as `SLACK_APP_TOKEN`

**OAuth & Permissions → Bot Token Scopes:**
- `channels:history`
- `groups:history`
- `im:history`
- `channels:read`
- `chat:write`
- `chat:write.customize`
- `im:write`
- `users:read`
- `reactions:write`

**Event Subscriptions → Subscribe to bot events:**
- `message.channels`
- `message.groups`
- `message.im`

**Install App** → Install to Workspace → save Bot Token as `SLACK_BOT_TOKEN`

### 6. Run the bot

```bash
python main.py
```

---

## Usage

### Auto-reply on @mention or DM
When someone messages you directly or @mentions you, the bot replies automatically using your memory.

### Reply on command
In any channel or DM with the bot:
```
/reply @john Tell him I'll join the meeting at 3pm
```

The bot will DM John with a reply drafted in your voice.

### Memory vault
All saved memories live in `vault/`. Each topic is a plain `.md` file you can open in Obsidian, grep, or feed into any AI tool.

---

## Connecting to Obsidian

Point `VAULT_DIR` in `config.py` to your Obsidian vault folder:

```python
VAULT_DIR = "/Users/darren/obsidian-vault/slack-memory"
```

Slack memories will appear alongside your journal notes automatically.

---

## License

MIT
