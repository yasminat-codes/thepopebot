# Validation Rules Reference

Complete validation rules for llm-config.json and agent-config.json. Used by
[validate-config.py](../scripts/validate-config.py).

---

## Required Field Checks

### llm-config.json

| Field | Rule | Error Message |
|-------|------|---------------|
| `start_speaker` | Must be present | "start_speaker is required" |
| `start_speaker` | Must be "agent" or "user" | "start_speaker must be 'agent' or 'user'" |

### agent-config.json

| Field | Rule | Error Message |
|-------|------|---------------|
| `voice_id` | Must be present | "voice_id is required" |
| `voice_id` | Must be non-empty string | "voice_id cannot be empty" |

## Range Checks

| Field | Config File | Min | Max | Default | Error Message |
|-------|------------|-----|-----|---------|---------------|
| `voice_temperature` | agent | 0 | 2 | 1.0 | "voice_temperature must be 0-2" |
| `voice_speed` | agent | 0.5 | 2 | 1.0 | "voice_speed must be 0.5-2" |
| `volume` | agent | 0 | 2 | 1.0 | "volume must be 0-2" |
| `responsiveness` | agent | 0 | 1 | 0.8 | "responsiveness must be 0-1" |
| `interruption_sensitivity` | agent | 0 | 1 | 0.7 | "interruption_sensitivity must be 0-1" |
| `backchannel_frequency` | agent | 0 | 1 | 0.5 | "backchannel_frequency must be 0-1" |
| `ambient_sound_volume` | agent | 0 | 2 | 0.3 | "ambient_sound_volume must be 0-2" |
| `model_temperature` | llm | 0 | 2 | 0.4 | "model_temperature must be 0-2" |
| `end_call_after_silence_ms` | agent | 1000 | 600000 | 30000 | "end_call_after_silence_ms must be 1000-600000" |
| `max_call_duration_ms` | agent | 60000 | 7200000 | 900000 | "max_call_duration_ms must be 60000-7200000" |

## Enum Checks

| Field | Config File | Allowed Values |
|-------|------------|---------------|
| `voice_emotion` | agent | calm, sympathetic, happy, sad, angry, fearful, surprised |
| `ambient_sound` | agent | coffee-shop, convention-hall, summer-outdoor, mountain-outdoor, static-noise, call-center |
| `denoising_mode` | agent | no-denoise, noise-cancellation, noise-and-background-speech-cancellation |
| `data_storage_setting` | agent | everything, everything_except_pii, basic_attributes_only |
| `start_speaker` | llm | agent, user |

## Type Checks

| Field | Config File | Expected Type | Error Message |
|-------|------------|--------------|---------------|
| `fallback_voice_ids` | agent | array of strings | "fallback_voice_ids must be an array" |
| `backchannel_words` | agent | array of strings | "backchannel_words must be an array" |
| `pronunciation_dictionary` | agent | array of objects | "pronunciation_dictionary must be an array" |
| `post_call_analysis_data` | agent | array of objects | "post_call_analysis_data must be an array" |
| `webhook_events` | agent | array of strings | "webhook_events must be an array" |
| `boosted_keywords` | agent | array of strings | "boosted_keywords must be an array" |
| `states` | llm | array of objects | "states must be an array" |
| `general_tools` | llm | array of objects | "general_tools must be an array" |
| `knowledge_base_ids` | llm | array of strings | "knowledge_base_ids must be an array" |
| `enable_backchannel` | agent | boolean | "enable_backchannel must be boolean" |
| `enable_dynamic_voice_speed` | agent | boolean | "enable_dynamic_voice_speed must be boolean" |
| `normalize_for_speech` | agent | boolean | "normalize_for_speech must be boolean" |

## Structural Checks

### Pronunciation Dictionary Entries

Each entry in `pronunciation_dictionary` must have:
- `word` (string, non-empty)
- `alphabet` (string, typically "ipa")
- `phoneme` (string, non-empty)

### Post-Call Analysis Entries

Each entry in `post_call_analysis_data` must have:
- `name` (string, non-empty)
- `type` (string, one of: string, boolean, number, enum)
- `description` (string, non-empty)

### State Entries

Each entry in `states` must have:
- `name` (string, non-empty, unique across states)

Each edge must have:
- `description` (string)
- `destination_state_name` (string, must match a state name)

## Cross-Config Checks

| Check | Rule | Severity |
|-------|------|----------|
| States vs general_prompt | If `states` is non-empty, `general_prompt` may be ignored | Warning |
| begin_message vs start_speaker | If `start_speaker` = "user", `begin_message` is ignored | Warning |
| Edge targets | All `destination_state_name` values must match a state name | Error |
| Backchannel fields | If `enable_backchannel` = false, backchannel_frequency/words are ignored | Warning |
| Ambient sound fields | If `ambient_sound` is not set, `ambient_sound_volume` is ignored | Warning |

## Validation Output Format

```
PASS  [agent] voice_id is present
PASS  [agent] voice_temperature (1.2) is in range [0, 2]
PASS  [agent] responsiveness (0.85) is in range [0, 1]
WARN  [llm]   states defined — general_prompt may be ignored
FAIL  [llm]   state edge "booking" references non-existent state "book"
---
Results: 22 PASS, 1 WARN, 1 FAIL
```
