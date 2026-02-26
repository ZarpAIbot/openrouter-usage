#!/usr/bin/env python3
"""OpenRouter usage tracker for OpenClaw agents.

Queries OpenRouter API for credit balance and parses OpenClaw session logs
to provide per-model cost breakdowns.
"""

import argparse
import json
import os
import sys
import glob
import urllib.request
import urllib.error
from datetime import datetime, timezone
from collections import defaultdict
from pathlib import Path


OPENROUTER_API_BASE = "https://openrouter.ai/api/v1"


def get_api_key():
    """Resolve OpenRouter API key from environment or OpenClaw auth store."""
    key = os.environ.get("OPENROUTER_API_KEY")
    if key:
        return key

    # Try OpenClaw agent auth store
    openclaw_dir = Path.home() / ".openclaw"
    auth_files = sorted(openclaw_dir.glob("agents/*/agent/auth.json"))
    for auth_file in auth_files:
        try:
            with open(auth_file) as f:
                auth = json.load(f)
            if "openrouter" in auth and "key" in auth["openrouter"]:
                return auth["openrouter"]["key"]
        except (json.JSONDecodeError, KeyError, OSError):
            continue

    return None


def api_get(endpoint, api_key):
    """Make authenticated GET request to OpenRouter API."""
    url = f"{OPENROUTER_API_BASE}/{endpoint}"
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {api_key}")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        return {"error": f"HTTP {e.code}: {body[:200]}"}
    except Exception as e:
        return {"error": str(e)}


def cmd_credits(api_key, fmt="text"):
    """Show OpenRouter credit balance."""
    data = api_get("credits", api_key)
    if "error" in data:
        # Fallback to legacy endpoint
        data = api_get("auth/key", api_key)

    if "error" in data:
        print(f"Error: {data['error']}", file=sys.stderr)
        sys.exit(1)

    if fmt == "json":
        print(json.dumps(data, indent=2))
        return

    # Handle both API formats
    if "data" in data:
        d = data["data"]
        total = d.get("total_credits", d.get("limit", 0))
        used = d.get("total_usage", d.get("usage", 0))
    else:
        total = data.get("limit", data.get("total_credits", 0))
        used = data.get("usage", data.get("total_usage", 0))

    remaining = total - used if total else "unlimited"

    print("═══ OpenRouter Credits ═══")
    print(f"  Total purchased:  ${total:.4f}" if isinstance(total, (int, float)) else f"  Limit: {total}")
    print(f"  Used:             ${used:.4f}" if isinstance(used, (int, float)) else f"  Used: {used}")
    if isinstance(remaining, (int, float)):
        print(f"  Remaining:        ${remaining:.4f}")
    else:
        print(f"  Remaining:        {remaining}")


def find_session_logs(openclaw_dir=None):
    """Find all OpenClaw session JSONL files."""
    if openclaw_dir is None:
        openclaw_dir = Path.home() / ".openclaw"
    else:
        openclaw_dir = Path(openclaw_dir)

    pattern = str(openclaw_dir / "agents" / "*" / "sessions" / "*.jsonl")
    return sorted(glob.glob(pattern))


def parse_session_costs(session_files, date_filter=None):
    """Parse OpenClaw session JSONL files for cost data per model."""
    model_stats = defaultdict(lambda: {
        "cost": 0.0,
        "input_tokens": 0,
        "output_tokens": 0,
        "requests": 0,
        "cache_read_tokens": 0,
        "cache_write_tokens": 0,
    })

    for fpath in session_files:
        try:
            with open(fpath) as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    # Filter by date if specified
                    ts = entry.get("timestamp") or entry.get("ts")
                    if date_filter and ts:
                        try:
                            entry_date = ts[:10]  # YYYY-MM-DD
                            if entry_date != date_filter:
                                continue
                        except (TypeError, IndexError):
                            pass

                    # Extract cost/usage from message entries
                    msg = entry.get("message", {})
                    usage = msg.get("usage", {})
                    cost_data = usage.get("cost", {})
                    model = msg.get("model") or entry.get("model") or "unknown"

                    total_cost = cost_data.get("total", 0) or 0
                    if total_cost > 0:
                        stats = model_stats[model]
                        stats["cost"] += total_cost
                        stats["input_tokens"] += usage.get("input", usage.get("inputTokens", usage.get("prompt_tokens", 0))) or 0
                        stats["output_tokens"] += usage.get("output", usage.get("outputTokens", usage.get("completion_tokens", 0))) or 0
                        stats["cache_read_tokens"] += usage.get("cacheRead", cost_data.get("cacheRead", 0)) or 0
                        stats["cache_write_tokens"] += usage.get("cacheWrite", cost_data.get("cacheWrite", 0)) or 0
                        stats["requests"] += 1

        except OSError:
            continue

    return dict(model_stats)


def cmd_sessions(openclaw_dir, date_filter, fmt="text"):
    """Show per-model cost breakdown from OpenClaw session logs."""
    files = find_session_logs(openclaw_dir)
    if not files:
        print("No session logs found.", file=sys.stderr)
        sys.exit(1)

    stats = parse_session_costs(files, date_filter)

    if not stats:
        label = f" for {date_filter}" if date_filter else ""
        print(f"No cost data found{label}.")
        return

    if fmt == "json":
        print(json.dumps(stats, indent=2))
        return

    # Sort by cost descending
    sorted_models = sorted(stats.items(), key=lambda x: x[1]["cost"], reverse=True)
    total_cost = sum(s["cost"] for _, s in sorted_models)
    total_reqs = sum(s["requests"] for _, s in sorted_models)
    total_in = sum(s["input_tokens"] for _, s in sorted_models)
    total_out = sum(s["output_tokens"] for _, s in sorted_models)

    label = f" ({date_filter})" if date_filter else " (all sessions)"
    print(f"═══ OpenRouter Usage by Model{label} ═══\n")

    for model, s in sorted_models:
        pct = (s["cost"] / total_cost * 100) if total_cost > 0 else 0
        print(f"  {model}")
        print(f"    Cost: ${s['cost']:.4f} ({pct:.1f}%)  |  Requests: {s['requests']}")
        print(f"    Tokens: {s['input_tokens']:,} in / {s['output_tokens']:,} out")
        if s["cache_read_tokens"] > 0 or s["cache_write_tokens"] > 0:
            print(f"    Cache: {s['cache_read_tokens']:,} read / {s['cache_write_tokens']:,} write")
        print()

    print(f"  ──────────────────────────────")
    print(f"  TOTAL: ${total_cost:.4f}  |  {total_reqs} requests  |  {total_in + total_out:,} tokens")


def main():
    parser = argparse.ArgumentParser(
        description="OpenRouter usage tracker for OpenClaw",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Examples:\n"
               "  %(prog)s credits              Show credit balance\n"
               "  %(prog)s sessions             Per-model breakdown (all time)\n"
               "  %(prog)s sessions --today     Today's usage only\n"
               "  %(prog)s sessions --date 2026-02-25\n"
               "  %(prog)s sessions --format json\n"
    )
    sub = parser.add_subparsers(dest="command")

    # credits
    cr = sub.add_parser("credits", help="Show OpenRouter credit balance")
    cr.add_argument("--format", choices=["text", "json"], default="text")

    # sessions
    se = sub.add_parser("sessions", help="Per-model cost breakdown from session logs")
    se.add_argument("--today", action="store_true", help="Filter to today only")
    se.add_argument("--date", type=str, help="Filter to specific date (YYYY-MM-DD)")
    se.add_argument("--openclaw-dir", type=str, default=None, help="OpenClaw config dir")
    se.add_argument("--format", choices=["text", "json"], default="text")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    if args.command == "credits":
        api_key = get_api_key()
        if not api_key:
            print("Error: No OpenRouter API key found. Set OPENROUTER_API_KEY or configure OpenClaw auth.", file=sys.stderr)
            sys.exit(1)
        cmd_credits(api_key, args.format)

    elif args.command == "sessions":
        date_filter = None
        if args.today:
            date_filter = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        elif args.date:
            date_filter = args.date
        cmd_sessions(args.openclaw_dir, date_filter, args.format)


if __name__ == "__main__":
    main()
