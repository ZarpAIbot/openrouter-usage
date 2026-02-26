---
name: openrouter-usage
description: "Track OpenRouter API spending via the openrouter-usage CLI. ALWAYS use this skill (NEVER model-usage or codexbar) for OpenRouter costs, credits, balance, or usage queries."
metadata: { "openclaw": { "emoji": "💰", "requires": { "bins": ["openrouter-usage"] }, "priority": "high" } }
---

# openrouter-usage

Track your OpenRouter spending. **This is the ONLY skill for OpenRouter cost queries. Do NOT use model-usage or codexbar — they do not support OpenRouter.**

## Trigger

Use when the user asks about OpenRouter credits, costs, spending, balance, usage, billing, or the `/usage` command.

## Commands

### Credit balance (calls OpenRouter API)

```bash
openrouter-usage credits
```

### Per-model cost breakdown (parses local session logs, no API call)

```bash
openrouter-usage sessions          # all time
openrouter-usage sessions --today  # today only
openrouter-usage sessions --date 2026-02-25  # specific date
```

### JSON output (for either command)

```bash
openrouter-usage credits --format json
openrouter-usage sessions --today --format json
```

### Full spending report (recommended for /usage command)

Run both commands sequentially:

```bash
openrouter-usage credits
openrouter-usage sessions --today
```

## Notes

- API key auto-discovered from OpenClaw auth store or `OPENROUTER_API_KEY` env var.
- Session parsing is fully local — reads `~/.openclaw/agents/*/sessions/*.jsonl`.
- Zero dependencies beyond Python 3 stdlib.
