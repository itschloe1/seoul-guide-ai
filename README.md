# Seoul Guide AI

AI chatbot that helps foreigners living in Korea with daily life questions. Telegram bot powered by Claude API.

## Features

- Text Q&A about Korean daily life (banking, housing, healthcare, visa, transportation, etc.)
- Photo interpretation: send a photo of a bill, menu, sign, or contract and get contextual explanation
- Conversation history per user (in-memory)

## Setup

```bash
# Clone and enter the project
git clone https://github.com/itschloe1/seoul-guide-ai.git
cd seoul-guide-ai

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your actual keys

# Run the bot
python bot.py
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | Telegram Bot API token from [@BotFather](https://t.me/BotFather) |
| `ANTHROPIC_API_KEY` | Anthropic API key |

## Project Structure

```
├── bot.py               # Telegram bot (main entry point)
├── system_prompt.md     # System prompt with Korea living knowledge
├── requirements.txt     # Python dependencies
├── context-library/     # Detailed knowledge base (Phase 2 RAG source)
└── .env.example         # Environment variable template
```

## Tech Stack

- Python + python-telegram-bot
- Claude API (Haiku for MVP)
- Pillow (image processing)
