#!/usr/bin/env python3
"""Print the remaining DeepSeek API balance in CNY.

Reads DEEPSEEK_API_KEY from the environment and calls
GET https://api.deepseek.com/user/balance
"""

import json
import os
import sys
import urllib.error
import urllib.request

BALANCE_URL = "https://api.deepseek.com/user/balance"
CURRENCY = "CNY"


def fetch_balance(api_key: str, timeout: int = 30) -> dict:
    request = urllib.request.Request(
        BALANCE_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
        },
        method="GET",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> int:
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        print("ERROR: DEEPSEEK_API_KEY is not set", file=sys.stderr)
        print("Set it with: export DEEPSEEK_API_KEY=sk-...", file=sys.stderr)
        return 2

    try:
        data = fetch_balance(api_key)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", "replace")
        if exc.code == 401:
            print("ERROR: 401 Unauthorized — invalid or revoked API key", file=sys.stderr)
        else:
            print(f"ERROR: HTTP {exc.code} from {BALANCE_URL}", file=sys.stderr)
        if body:
            print(body[:500], file=sys.stderr)
        return 1
    except urllib.error.URLError as exc:
        print(f"ERROR: network failure — {exc.reason}", file=sys.stderr)
        return 1
    except json.JSONDecodeError:
        print("ERROR: response is not valid JSON", file=sys.stderr)
        return 1

    if "--json" in sys.argv[1:]:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 0

    infos = data.get("balance_infos") or []
    if not infos:
        print("No balance records returned (balance_infos is empty).")
        return 0

    match = next((i for i in infos if i.get("currency") == CURRENCY), None)
    if match is None:
        available = ", ".join(i.get("currency", "?") for i in infos)
        print(f"No {CURRENCY} balance record; available: {available}")
        return 0

    available = data.get("is_available")
    if available is False:
        print("WARNING: balance is not sufficient for API calls", file=sys.stderr)

    print(f"{match.get('total_balance')} {CURRENCY}")
    print(
        "  topped up: {t} {c} | granted: {g} {c}".format(
            t=match.get("topped_up_balance"),
            g=match.get("granted_balance"),
            c=CURRENCY,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
