# Voice Cloning Guide: ElevenLabs to Retell AI

## Overview

Voice cloning lets you replicate a specific person's voice for use in a Retell AI agent. ElevenLabs offers the highest quality cloning and is the recommended provider. MiniMax also supports cloning but with lower English quality.

This guide covers the full workflow: recording audio, cloning via ElevenLabs, and importing the cloned voice into Retell.

## Requirements

### ElevenLabs Account
- **Minimum plan:** Creator ($22/month) for instant voice cloning
- **Recommended plan:** Professional ($99/month) for professional voice cloning (higher quality, more samples)
- Instant cloning: Quick, lower quality, 1-5 minutes of audio
- Professional cloning: Higher quality, requires 30+ minutes of audio

### Audio Recording Requirements

| Requirement | Instant Clone | Professional Clone |
|-------------|--------------|-------------------|
| Duration | 1-5 minutes | 30 minutes minimum |
| Format | MP3, WAV, M4A, FLAC | WAV preferred (16-bit, 44.1kHz+) |
| Sample rate | 16kHz minimum | 44.1kHz or 48kHz recommended |
| Channels | Mono preferred | Mono required |
| Background noise | Minimal | None (studio quality) |
| Speakers | Single speaker only | Single speaker only |
| Content | Natural speech, varied sentences | Diverse phonemes, emotions, pacing |

### Audio Quality Tips

- Record in a quiet room with soft furnishings (reduces echo)
- Use a decent USB microphone -- built-in laptop mics produce poor results
- Maintain consistent distance from the microphone (6-12 inches)
- Speak naturally -- do not read in a flat monotone
- Include a variety of sentence types: questions, statements, lists, exclamations
- Avoid long pauses, coughs, throat clearing, or filler words
- Do not post-process with compression, EQ, or noise gates -- ElevenLabs handles this

## Step 1: Record or Collect Audio Samples

Option A -- Record new audio:
```bash
# Example: record using ffmpeg (if available)
ffmpeg -f alsa -i default -t 300 -ar 44100 -ac 1 voice_sample.wav
```

Option B -- Use existing audio (podcast, interview, voicemail, etc.). Ensure single-speaker segments only.

## Step 2: Clone via ElevenLabs API

### Instant Voice Clone

```bash
curl -X POST "https://api.elevenlabs.io/v1/voices/add" \
  -H "xi-api-key: YOUR_ELEVENLABS_API_KEY" \
  -F "name=Client Voice Clone" \
  -F "description=Cloned voice for Retell agent" \
  -F "files=@voice_sample.wav" \
  -F "labels={\"accent\":\"american\",\"gender\":\"female\",\"use_case\":\"sales\"}"
```

Response:
```json
{
  "voice_id": "cloned_voice_id_here"
}
```

### Professional Voice Clone

Professional cloning requires multiple audio files. Upload via the ElevenLabs dashboard or API:

```bash
curl -X POST "https://api.elevenlabs.io/v1/voices/add" \
  -H "xi-api-key: YOUR_ELEVENLABS_API_KEY" \
  -F "name=Client Professional Clone" \
  -F "description=Professional clone for production agent" \
  -F "files=@sample_part1.wav" \
  -F "files=@sample_part2.wav" \
  -F "files=@sample_part3.wav" \
  -F "labels={\"accent\":\"american\",\"gender\":\"male\",\"use_case\":\"receptionist\"}"
```

## Step 3: Verify the Cloned Voice

Test the cloned voice before importing to Retell:

```bash
curl -X POST "https://api.elevenlabs.io/v1/text-to-speech/CLONED_VOICE_ID" \
  -H "xi-api-key: YOUR_ELEVENLABS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, thank you for calling. How can I help you today?",
    "model_id": "eleven_turbo_v2",
    "voice_settings": {
      "stability": 0.5,
      "similarity_boost": 0.75,
      "style": 0.0,
      "use_speaker_boost": true
    }
  }' \
  --output test_clone.mp3
```

Listen to `test_clone.mp3` and verify it sounds like the original speaker.

## Step 4: Import to Retell

Add the cloned voice to your Retell account:

```bash
curl -X POST "https://api.retellai.com/v2/add-voice" \
  -H "Authorization: Bearer YOUR_RETELL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "voice_name": "Client Custom Voice",
    "provider": "elevenlabs",
    "provider_voice_id": "CLONED_VOICE_ID",
    "voice_model": "eleven_turbo_v2"
  }'
```

The response returns a Retell `voice_id` that you use in your agent configuration.

## Step 5: Configure in Agent

Use the Retell voice_id in your agent config:

```json
{
  "voice_id": "retell_voice_id_from_step_4",
  "voice_temperature": 0.7,
  "voice_speed": 1.0
}
```

### Recommended Settings for Cloned Voices

- **voice_temperature:** 0.5-0.7 (lower than default to maintain consistency with the original voice)
- **voice_speed:** 1.0 (match the natural speaking pace of the cloned source)
- **stability:** 0.6-0.8 (higher stability preserves the cloned voice characteristics)
- **similarity_boost:** 0.8-0.9 (higher similarity keeps it sounding like the original)

## Legal and Compliance

Voice cloning carries legal obligations. Non-compliance can result in lawsuits, fines, and platform bans.

### Required
- **Written consent** from the voice owner before cloning
- **Disclosure** to callers that they are speaking with an AI (required by law in many jurisdictions)
- **Consent form** should specify: how the voice will be used, duration of use, who controls the cloned voice

### Prohibited
- Cloning a voice without the owner's explicit, informed consent
- Using a cloned voice to impersonate someone for fraud or deception
- Cloning public figures, celebrities, or politicians without authorization
- Using cloned voices for robocalls or spam

### Best Practices
- Keep a signed consent form on file for every cloned voice
- Include a clause allowing the voice owner to revoke consent
- Document the date, scope, and purpose of each cloning operation
- Delete cloned voices when they are no longer needed or consent is revoked

## Troubleshooting

### Clone Sounds Robotic or Flat
- **Cause:** Insufficient audio variety. The source sample may be too monotone.
- **Fix:** Record new samples with varied pitch, emotion, and sentence structure.

### Clone Does Not Sound Like the Original
- **Cause:** Low similarity_boost or audio quality issues.
- **Fix:** Increase similarity_boost to 0.85-0.95. Re-record in a quieter environment.

### Clone Produces Artifacts or Glitches
- **Cause:** Background noise or multiple speakers in source audio.
- **Fix:** Clean the source audio. Ensure single-speaker segments only.

### Clone Works in ElevenLabs but Not in Retell
- **Cause:** Voice not imported to Retell, or wrong voice_id used.
- **Fix:** Verify the import via Retell's Add Voice API. Use the Retell voice_id, not the ElevenLabs voice_id.

### Latency Is Higher with Cloned Voice
- **Cause:** Professional clones can have higher processing overhead.
- **Fix:** Use `eleven_turbo_v2` model. Ensure `use_speaker_boost` is set to true.

## Cost Considerations

| Item | Cost |
|------|------|
| ElevenLabs Creator plan | $22/month (includes instant cloning) |
| ElevenLabs Professional plan | $99/month (includes professional cloning) |
| Additional character usage | Per-character overage fees apply |
| Retell voice import | No additional cost |
| Retell per-minute usage | Standard per-minute rate applies |

Professional cloning produces noticeably better results and is recommended for production agents. Instant cloning is suitable for prototyping and testing.
