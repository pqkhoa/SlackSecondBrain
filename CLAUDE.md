# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

A personal Slack bot (~300 LOC, pure Python) that:
- Silently classifies and saves Slack messages into a Markdown vault using Claude
- Auto-replies to @mentions and DMs by drafting responses grounded in saved memory
- Exposes a `/reply @user instruction` slash command for explicit message drafting

## Running the Bot

```bash
pip install -r requirements.txt
cp .env.example .env   # then fill in secrets
python main.py
```

Required `.env` keys:
```
SLACK_BOT_TOKEN=xoxb-...
SLACK_APP_TOKEN=xapp-...
NVIDIA_API_KEY=nvapi-...
```

There is no build step, no test suite, and no linter config.

## Configuration

All user-facing configuration is in `config.py` — edit this file to change name, reply style, topic list, or vault path. Do not scatter config into other modules.

## Architecture

Four modules with a strict dependency chain:

```
main.py → claude.py → memory.py → vault/<topic>.md
```

**`main.py`** — Slack Bolt Socket Mode event handlers. Two handlers:
- `handle_message()` — catches all channel/DM messages, routes @mentions to `draft_reply()`, sends everything through `classify_and_save()`
- `handle_reply_command()` — parses `/reply @user instruction` via regex, calls `draft_reply_to_target()`

**`claude.py`** — All Claude API calls. Three functions:
- `classify_and_save(text, user)` — asks Claude if the message is worth remembering; expects JSON back: `{"save": bool, "topic": str, "summary": str}`; writes to vault on `save: true`
- `draft_reply(incoming_msg, memory_context, from_user)` — drafts a reply as the configured user, grounded in full memory context
- `draft_reply_to_target(instruction, memory, target_user_id)` — drafts an explicit message to a target user based on the slash command instruction

**`memory.py`** — Plain file I/O only. Reads/writes `vault/<topic>.md` files. Each entry is appended as `## YYYY-MM-DD HH:MM (from @user)\n<summary>`. `get_all_memory()` concatenates all topic files for use as Claude context.

**`vault/`** — Git-ignored directory of Markdown files, one per topic (ai, work, ideas, productivity, nvidia, personal). These are the only persistent state.

## Key Behaviors

- Every message in any channel the bot is in flows through `classify_and_save()` — Claude decides what gets stored
- Auto-replies on @mentions and DMs use the **full vault** as context (all topic files concatenated)
- The bot ignores its own messages (filtered by bot user ID fetched at startup via `auth_test()`)
- Memory is append-only, not deduplicated

## Slack App Requirements

Socket Mode must be enabled. Required bot token scopes: `channels:history`, `groups:history`, `im:history`, `channels:read`, `chat:write`, `chat:write.customize`, `im:write`, `users:read`, `reactions:write`. Event subscriptions: `message.channels`, `message.groups`, `message.im`.
