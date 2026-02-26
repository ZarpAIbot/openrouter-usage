---
name: openrouter-usage
description: Track OpenRouter API credit balance and per-model cost breakdown from OpenClaw session logs. Use when the user asks about spending, costs, usage, or billing related to OpenRouter.
metadata: { "openclaw": { "emoji": "💰", "requires": { "bins": ["python3"] } } }
---

# openrouter-usage

Track your OpenRouter spending directly from OpenClaw.

## Trigger

Use this skill when the user asks about:
- OpenRouter credit balance or remaining credits
- Cost breakdown by model
- How much they've spent today / this week / total
- Token usage per model

## Commands

### Check credit balance

```bash
python3 {baseDir}/scripts/openrouter_usage.py credits
python3 {baseDir}/scripts/openrouter_usage.py credits --format json
```

The script auto-discovers the OpenRouter API key from:
1. `OPENROUTER_API_KEY` environment variable
2. OpenClaw agent auth store (`~/.openclaw/agents/*/agent/auth.json`)

### Per-model cost breakdown (from session logs)

```bash
# All sessions
python3 {baseDir}/scripts/openrouter_usage.py sessions

# Today only
python3 {baseDir}/scripts/openrouter_usage.py sessions --today

# Specific date
python3 {baseDir}/scripts/openrouter_usage.py sessions --date 2026-02-25

# JSON output
python3 {baseDir}/scripts/openrouter_usage.py sessions --format json
```

This parses OpenClaw's session JSONL files (`~/.openclaw/agents/*/sessions/*.jsonl`) and extracts cost data per model from the `usage.cost` fields that OpenRouter returns with each response.

## Output

Text mode shows a table with per-model cost, percentage, request count, and token breakdown (input/output/cache).

JSON mode returns structured data suitable for further processing.

## Notes

- The `credits` command queries OpenRouter's `/api/v1/credits` API (falls back to `/api/v1/auth/key`).
- The `sessions` command is fully local — no API calls needed. It reads OpenClaw's own logs.
- No external dependencies beyond Python 3 stdlib.
