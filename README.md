# openrouter-usage

An [OpenClaw](https://github.com/openclaw/openclaw) skill to track your OpenRouter API spending.

## Features

- **Credit balance** — Query your OpenRouter credit balance via API
- **Per-model cost breakdown** — Parse OpenClaw session logs locally for detailed cost/token stats
- **Date filtering** — View usage for today, a specific date, or all time
- **JSON output** — Machine-readable output for automation
- **Zero dependencies** — Python 3 stdlib only
- **Auto key discovery** — Reads API key from env var or OpenClaw auth store

## Install

### As an OpenClaw skill

```bash
# Clone into your OpenClaw workspace skills directory
git clone https://github.com/luiscajigas/openrouter-usage ~/.openclaw/workspace/skills/openrouter-usage

# Or use ClawHub (if published)
clawhub install openrouter-usage
```

### Standalone

```bash
git clone https://github.com/luiscajigas/openrouter-usage
cd openrouter-usage
python3 scripts/openrouter_usage.py --help
```

## Usage

```bash
# Check credit balance
python3 scripts/openrouter_usage.py credits

# Per-model breakdown (all sessions)
python3 scripts/openrouter_usage.py sessions

# Today only
python3 scripts/openrouter_usage.py sessions --today

# Specific date
python3 scripts/openrouter_usage.py sessions --date 2026-02-25

# JSON output
python3 scripts/openrouter_usage.py sessions --format json
```

## API Key Resolution

The script looks for your OpenRouter API key in this order:
1. `OPENROUTER_API_KEY` environment variable
2. OpenClaw agent auth store (`~/.openclaw/agents/*/agent/auth.json`)

## How It Works

- **credits**: Calls OpenRouter's `/api/v1/credits` endpoint (falls back to `/api/v1/auth/key`)
- **sessions**: Parses OpenClaw's session JSONL files locally — no API calls. Extracts `usage.cost` data that OpenRouter includes in every response.

## License

MIT
