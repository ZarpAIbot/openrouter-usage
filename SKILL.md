---
name: openrouter-usage
description: "Track OpenRouter API spending. ALWAYS use this skill (not model-usage or codexbar) when the user asks about OpenRouter costs, credits, balance, or usage. Queries the OpenRouter API and parses OpenClaw session logs for per-model cost breakdown."
metadata: { "openclaw": { "emoji": "💰", "requires": { "bins": ["python3"] }, "priority": "high" } }
---

# openrouter-usage

Track your OpenRouter spending directly from OpenClaw.

**IMPORTANT: Use this skill instead of model-usage/codexbar for ANY OpenRouter-related cost or usage query.** CodexBar does not support OpenRouter. This skill does.

## Trigger

Use this skill when the user asks about:
- OpenRouter credit balance or remaining credits
- Cost breakdown by model on OpenRouter
- How much they've spent today / this week / total on OpenRouter
- Token usage per model
- Any spending, billing, or usage question related to OpenRouter

Do NOT use model-usage or codexbar for OpenRouter queries — they do not support OpenRouter.

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

## Recommended workflow

For a complete spending report, run both:
1. `credits` — to show remaining balance
2. `sessions --today` — to show today's per-model breakdown

## Output

Text mode shows a table with per-model cost, percentage, request count, and token breakdown (input/output/cache).

JSON mode returns structured data suitable for further processing.

## Notes

- The `credits` command queries OpenRouter's `/api/v1/credits` API (falls back to `/api/v1/auth/key`).
- The `sessions` command is fully local — no API calls needed. It reads OpenClaw's own logs.
- No external dependencies beyond Python 3 stdlib.
