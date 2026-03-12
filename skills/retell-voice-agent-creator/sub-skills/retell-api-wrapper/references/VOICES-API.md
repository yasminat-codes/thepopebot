# Voices API Reference

Reference for the Retell AI Voices endpoint. Voices are read-only resources — you
list and select them but cannot create or modify them.

Base URL: `https://api.retellai.com`

---

## List Voices

**GET** `/list-voices`

Returns all available voices across all providers.

```bash
curl -s https://api.retellai.com/list-voices \
  -H "Authorization: Bearer $RETELL_API_KEY"
```

### Response Fields Per Voice

| Field | Type | Description |
|-------|------|-------------|
| `voice_id` | string | Unique identifier to use in agent config |
| `voice_name` | string | Human-readable voice name |
| `provider` | string | Voice provider |
| `gender` | string | "male" or "female" |
| `accent` | string | Accent description (e.g., "American", "British") |
| `age` | string | Age category (e.g., "young", "middle-aged") |
| `preview_audio_url` | string | URL to listen to a sample |

### Providers

| Provider | Description |
|----------|-------------|
| `elevenlabs` | ElevenLabs voices — high quality, wide variety |
| `openai` | OpenAI voices — fast, good quality |
| `deepgram` | Deepgram voices — low latency |
| `cartesia` | Cartesia voices — natural sounding |
| `minimax` | MiniMax voices |
| `fish_audio` | Fish Audio voices |
| `platform` | Retell platform voices |

### Filtering Voices

The API returns all voices in a single response. Use `jq` to filter client-side.

**By provider:**
```bash
curl -s https://api.retellai.com/list-voices \
  -H "Authorization: Bearer $RETELL_API_KEY" \
  | jq '[.[] | select(.provider == "elevenlabs")]'
```

**By gender:**
```bash
curl -s https://api.retellai.com/list-voices \
  -H "Authorization: Bearer $RETELL_API_KEY" \
  | jq '[.[] | select(.gender == "female")]'
```

**By accent:**
```bash
curl -s https://api.retellai.com/list-voices \
  -H "Authorization: Bearer $RETELL_API_KEY" \
  | jq '[.[] | select(.accent == "British")]'
```

**Combined filters (female, American, ElevenLabs):**
```bash
curl -s https://api.retellai.com/list-voices \
  -H "Authorization: Bearer $RETELL_API_KEY" \
  | jq '[.[] | select(.provider == "elevenlabs" and .gender == "female" and .accent == "American")]'
```

**Get just voice IDs and names:**
```bash
curl -s https://api.retellai.com/list-voices \
  -H "Authorization: Bearer $RETELL_API_KEY" \
  | jq '[.[] | {voice_id, voice_name, provider, gender, accent}]'
```

### Response Example

```json
[
  {
    "voice_id": "11labs-Adrian",
    "voice_name": "Adrian",
    "provider": "elevenlabs",
    "gender": "male",
    "accent": "American",
    "age": "young",
    "preview_audio_url": "https://retell-utils-public.s3.amazonaws.com/adrian.wav"
  },
  {
    "voice_id": "11labs-Myra",
    "voice_name": "Myra",
    "provider": "elevenlabs",
    "gender": "female",
    "accent": "American",
    "age": "young",
    "preview_audio_url": "https://retell-utils-public.s3.amazonaws.com/myra.wav"
  }
]
```

---

## Error Handling

| Status | Cause | Resolution |
|--------|-------|------------|
| 401 | Invalid API key | Verify `RETELL_API_KEY` |
| 500 | Server error | Retry with backoff |
