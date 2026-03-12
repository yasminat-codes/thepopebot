# YouTube Skill — API Setup Reference

AI provider configuration for `fetch_and_learn.py`.

---

## Provider Chain (in order)

```
1. OpenRouter  →  5 cheap models, tried in sequence
2. ZAI (GLM)   →  glm-4-plus
3. Anthropic   →  claude-haiku-4-5-20251001
4. OpenAI      →  gpt-4o-mini
```

---

## OpenRouter — Primary Provider

OpenRouter routes to many models via a single API key. The script tries 5 free/cheap models in sequence — if one is unavailable or quota-exceeded, it falls through to the next.

### Cheap Model Fallback Chain

| # | Model | Cost | Notes |
|---|-------|------|-------|
| 1 | `meta-llama/llama-3.3-70b-instruct:free` | Free | Strongest free model — best note quality |
| 2 | `google/gemma-3-27b-it:free` | Free | Large Gemma 3 — reliable structured output |
| 3 | `mistralai/mistral-small-3.1-24b-instruct:free` | Free | Mistral 3.1 — consistent fallback |
| 4 | `qwen/qwen3-4b:free` | Free | Fast smaller model |
| 5 | `google/gemma-3-12b-it:free` | Free | Medium Gemma 3 — final OpenRouter fallback |

> **Note:** OpenRouter model IDs change as providers update their offerings. If you see 404 errors, run `curl https://openrouter.ai/api/v1/models -H "Authorization: Bearer $OPENROUTER_API_KEY" | python3 -m json.tool | grep '"id"' | grep ':free'` to list current free models.

Free tier models may have rate limits. If all 5 fail, script continues to ZAI → Anthropic → OpenAI.

### Environment Variable
```bash
OPENROUTER_API_KEY=sk-or-v1-...
```

Get key at: openrouter.ai → API Keys

### Validate Key
```bash
curl -s -X POST "https://openrouter.ai/api/v1/chat/completions" \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"google/gemma-2-9b-it:free","messages":[{"role":"user","content":"ping"}],"max_tokens":5}' \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print('OK' if d.get('choices') else d)"
```

---

## Other Providers (fallbacks)

### ZAI (GLM)
```bash
ZAI_API_KEY=your-key
```
One-liner test:
```bash
curl -s -X POST "https://open.bigmodel.cn/api/paas/v4/chat/completions" \
  -H "Authorization: Bearer $ZAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"glm-4-plus","messages":[{"role":"user","content":"ping"}],"max_tokens":5}' \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print('OK' if d.get('choices') else d)"
```

### Anthropic
```bash
ANTHROPIC_API_KEY=sk-ant-...
```
One-liner test:
```bash
curl -s -X POST "https://api.anthropic.com/v1/messages" \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "Content-Type: application/json" \
  -d '{"model":"claude-haiku-4-5-20251001","max_tokens":5,"messages":[{"role":"user","content":"ping"}]}' \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print('OK' if d.get('content') else d)"
```

### OpenAI
```bash
OPENAI_API_KEY=sk-...
```
One-liner test:
```bash
curl -s -X POST "https://api.openai.com/v1/chat/completions" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-4o-mini","messages":[{"role":"user","content":"ping"}],"max_tokens":5}' \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print('OK' if d.get('choices') else d)"
```

---

## Force a Specific Provider

Skip OpenRouter (force ZAI or later):
```bash
OPENROUTER_API_KEY="" uv run fetch_and_learn.py --url "..."
```

Skip OpenRouter + ZAI (force Anthropic or OpenAI):
```bash
OPENROUTER_API_KEY="" ZAI_API_KEY="" uv run fetch_and_learn.py --url "..."
```

---

## Cost Notes

OpenRouter free models are $0. If rate-limited, paid alternatives on OpenRouter are ~$0.05–0.15 per million tokens (~$0.0001 per note). ZAI and OpenAI fallbacks are also very cheap at typical usage volumes.
