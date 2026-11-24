---
name: deepseek-balance
description: Check the remaining DeepSeek API credit balance in CNY (yuan) using DEEPSEEK_API_KEY from the environment. Use when the user asks how much money/credit is left on their DeepSeek account, asks to verify their DeepSeek API key works, or mentions DeepSeek billing, top-up, or usage balance (e.g. "сколько осталось на балансе DeepSeek", "проверь остаток средств DeepSeek", "DeepSeek 余额").
---

# DeepSeek Balance

Print the remaining DeepSeek API balance in CNY.

## Endpoint

`GET https://api.deepseek.com/user/balance` with `Authorization: Bearer $DEEPSEEK_API_KEY`.

`https://deepseek.com` is the marketing site — it returns HTML and has no balance API. Do not use it.

## Run

```bash
DEEPSEEK_API_KEY=sk-... python3 scripts/get_balance.py
```

The key is read from `os.environ["DEEPSEEK_API_KEY"]`; never pass it as a CLI argument, log it, or echo it back to the user.

If the environment variable is missing, ask the user to set it themselves (or to provide it through the credentials tool when available). Do not ask them to paste the key into the chat.

## Output

```
110.00 CNY
  topped up: 100.00 CNY | granted: 10.00 CNY
```

- `--json` prints the raw API response instead (useful for debugging or when the currency is not CNY).
- Only the CNY record is reported. If the account has no CNY record, the script lists the available currencies — report those values as-is with their own currency code.
- `is_available: false` means the balance is insufficient for API calls; surface that warning to the user.

## Exit codes

| Code | Meaning |
| --- | --- |
| 0 | Success |
| 1 | Network failure, non-200 HTTP status (e.g. 401 = invalid/revoked key), or malformed JSON |
| 2 | `DEEPSEEK_API_KEY` is not set |

## Notes

- Uses only the standard library (`urllib.request`) — no `pip install` needed.
- Response fields are strings, not numbers (`"110.00"`). Do not reformat beyond what the script prints.
- A 401 usually means a wrong key, a revoked key, or a key from a different platform.
