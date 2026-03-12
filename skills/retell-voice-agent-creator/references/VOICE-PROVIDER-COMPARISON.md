# Voice Provider Comparison

Comparison of voice providers available on Retell AI.

## Provider Matrix

| Feature | ElevenLabs | OpenAI | Deepgram | Cartesia | PlayHT | MiniMax |
|---------|-----------|--------|----------|----------|--------|---------|
| **Supported Languages** | 29+ | 10+ | 8+ | 12+ | 20+ | 40+ |
| **Voice Count** | 100+ (plus cloning) | ~6 built-in | 10+ | 20+ | 50+ | 30+ |
| **Emotion Support** | Yes (advanced) | Limited | No | Yes (Sonic-3 emotion control) | Yes | Limited |
| **Pronunciation Dictionary** | Yes (Turbo v2+) | No | No | No | Limited | No |
| **Voice Cloning** | Yes (instant + pro) | No | No | No | Yes | Yes |
| **Best For** | Premium English quality | Fast reliable output | Low latency | Speed + expressiveness | Creative voices | Multilingual (40+ languages) |
| **Latency** | Medium (50-120ms) | Low (30-80ms) | Very low (20-60ms) | Low (30-70ms) | Medium (60-130ms) | Medium (50-100ms) |
| **TTFA (Time to First Audio)** | Flash v2.5: ~75ms, Turbo v2: ~150ms | ~200ms | ~60ms | Sonic-3: ~95ms | ~160ms | ~120ms |
| **Pricing Tier** | Premium | Moderate | Moderate | Budget-friendly | Moderate | Budget-friendly |
| **SSML Support** | Partial | No | No | No | Yes | No |

## Detailed Provider Profiles

### ElevenLabs

**Strengths:**
- Most natural-sounding voices in the market
- Advanced emotion and tone control
- Pronunciation dictionary support (critical for brand names)
- Voice cloning (instant from 30 seconds of audio, or professional)
- Wide language support including Arabic, Hindi, Japanese

**Weaknesses:**
- Higher latency than some competitors
- Premium pricing
- Pronunciation dictionaries only work with Turbo v2 and later models

**Best use cases:** Sales agents, executive assistants, any agent where
naturalness is the top priority. Essential when pronunciation dictionaries
are needed.

**Recommended models:** Flash v2.5 (multilingual + fast, ~75ms TTFA), Turbo v2 (premium English quality, ~150ms TTFA)

**Note:** ElevenLabs voices on Retell sound solid but flat compared to native
ElevenLabs v3. The "smile in the voice" expressiveness present in ElevenLabs'
own platform does not fully carry over to the Retell integration.

### OpenAI

**Strengths:**
- Very fast response times
- Consistent quality
- Simple integration (native Retell support)
- Good for straightforward conversational agents

**Weaknesses:**
- Limited voice selection (6 voices)
- No voice cloning
- No pronunciation dictionary support
- Limited emotion range

**Best use cases:** Support agents, appointment setters, any use case where
speed matters more than vocal variety. Good default for quick deployments.

### Deepgram

**Strengths:**
- Lowest latency of all providers
- Excellent speech recognition integration
- Cost-effective for high-volume use cases

**Weaknesses:**
- Smaller voice library
- No emotion support
- No pronunciation dictionaries
- Less natural than ElevenLabs

**Best use cases:** High-volume call centers where latency is critical.
Survey agents. Any use case where speed is the top priority.

### Cartesia

**Strengths:**
- Sonic-3 model with full emotion control — current best for expressiveness
- Efficient streaming architecture with ~95ms TTFA
- Low latency
- Budget-friendly pricing
- Good quality-to-cost ratio

**Weaknesses:**
- Smaller voice library than ElevenLabs
- No pronunciation dictionaries
- Newer provider, less battle-tested

**Best use cases:** Top recommendation for speed + emotion. Sales agents,
customer-facing roles where expressiveness and low latency both matter.
Cost-conscious deployments that still need emotional range.

### PlayHT

**Strengths:**
- Large voice library with creative options
- Voice cloning capability
- SSML support for fine-grained control
- Good emotion range

**Weaknesses:**
- Higher latency than OpenAI/Deepgram
- Pronunciation dictionary support is limited
- Can be inconsistent across voices

**Best use cases:** Creative applications, agents that need unique character
voices, entertainment or media use cases.

### MiniMax

**Strengths:**
- 40+ language support (strongest multilingual coverage)
- Voice cloning capability (added December 2025)
- Budget-friendly
- Strong for Asian language markets
- Decent voice variety

**Weaknesses:**
- Limited emotion support
- No pronunciation dictionaries
- Less natural for English compared to ElevenLabs
- Smaller Western market presence

**Best use cases:** Multilingual deployments especially targeting Asian markets.
Budget-conscious international agents. Projects requiring 40+ language coverage.

## Selection Decision Tree

```
Need pronunciation dictionaries?
  YES -> ElevenLabs (only provider with full dictionary support)
  NO  ->
    Need voice cloning?
      YES -> ElevenLabs or PlayHT (or MiniMax for 40+ languages)
      NO  ->
        Priority is speed + expressiveness?
          YES -> Cartesia Sonic-3 (top recommendation, ~95ms TTFA + emotion control)
          NO  ->
            Priority is multilingual + fast?
              YES -> ElevenLabs Flash v2.5 (~75ms TTFA, 29+ languages)
              NO  ->
                Priority is premium English quality?
                  YES -> ElevenLabs Turbo v2
                  NO  ->
                    Priority is lowest latency?
                      YES -> Deepgram
                      NO  ->
                        Priority is lowest cost?
                          YES -> Cartesia or MiniMax
                          NO  -> OpenAI (reliable default)
```

## Cross-Provider Notes

- `enable_dynamic_voice_speed` works with all voice providers — auto-matches
  the caller's speaking pace regardless of which TTS is selected.
- Cartesia Sonic-3 with emotion control is the current best option for
  expressiveness at low latency.
- ElevenLabs Flash v2.5 is the top recommendation for multilingual deployments
  that also need fast response times.

## Language Coverage Quick Reference

| Language | ElevenLabs | OpenAI | Deepgram | Cartesia | PlayHT | MiniMax |
|----------|-----------|--------|----------|----------|--------|---------|
| English | Yes | Yes | Yes | Yes | Yes | Yes |
| Spanish | Yes | Yes | Yes | Yes | Yes | Yes |
| French | Yes | Yes | Yes | Yes | Yes | Yes |
| German | Yes | Yes | Yes | Yes | Yes | Yes |
| Arabic | Yes | No | No | Limited | Yes | Limited |
| Mandarin | Yes | Yes | No | Yes | Yes | Yes |
| Japanese | Yes | Yes | No | Yes | Yes | Yes |
| Hindi | Yes | Limited | No | No | Yes | Yes |
| Portuguese | Yes | Yes | Yes | Yes | Yes | Yes |
| Korean | Yes | Limited | No | Yes | Yes | Yes |
