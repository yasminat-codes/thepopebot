# Ambient Sound Guide

## Overview

Retell AI supports background ambient sounds that make the agent sound like it exists
in a real physical environment. This is one of the most effective humanization levers
because it subconsciously signals to the caller that they are talking to someone in
a real place.

## Available Ambient Sounds

| Sound | Retell Value | Description |
|-------|-------------|-------------|
| Coffee Shop | `coffee-shop` | Light chatter, cups clinking, casual atmosphere |
| Call Center | `call-center` | Keyboards, muted phone conversations, professional |
| Convention Hall | `convention-hall` | Crowd noise, busy atmosphere, energetic |
| Summer Outdoor | `summer-outdoor` | Birds, light breeze, relaxed and open |
| Mountain Outdoor | `mountain-outdoor` | Wind, nature sounds, calm and serene |
| Static Noise | `static-noise` | Light phone-line static, simulates phone call |

## Retell API Parameters

### ambient_sound
- **Type:** enum string or null
- **Values:** `coffee-shop`, `convention-hall`, `summer-outdoor`, `mountain-outdoor`, `static-noise`, `call-center`
- **Default:** null (no ambient sound)

### ambient_sound_volume
- **Type:** float, range [0, 2]
- **Default:** 1
- **Recommendation:** Keep between 0.3-1.0 for most use cases

## Sound Selection by Use Case

### coffee-shop
**Best for:** Sales calls, personal assistants, casual conversations
**Mood:** Warm, informal, friendly
**Volume range:** 0.3-0.7 (too loud = distracting)
**Template match:** Sales, Personal Assistant, Real Estate

### call-center
**Best for:** Support agents, receptionists, professional services
**Mood:** Professional, busy, competent
**Volume range:** 0.3-0.6 (subtle backdrop)
**Template match:** Support, Receptionist, Debt Collection

### convention-hall
**Best for:** Energetic environments, event-related calls
**Mood:** Busy, exciting, dynamic
**Volume range:** 0.2-0.5 (can be overwhelming)
**Template match:** Sales (high energy), Lead Qualifier

### summer-outdoor
**Best for:** Relaxed conversations, lifestyle brands
**Mood:** Relaxed, open, pleasant
**Volume range:** 0.3-0.6
**Template match:** Personal Assistant, Real Estate

### mountain-outdoor
**Best for:** Calm environments, wellness, meditation
**Mood:** Serene, peaceful, natural
**Volume range:** 0.3-0.5
**Template match:** Wellness, calm support scenarios

### static-noise
**Best for:** Simulating a real phone call
**Mood:** Authentic, telephonic
**Volume range:** 0.2-0.4 (very subtle)
**Template match:** Any template where "phone call feel" is desired

## Volume Recommendations by Humanization Level

| Level | Volume | Notes |
|-------|--------|-------|
| 1-3 | N/A | No ambient sound |
| 4-5 | 0.3-0.5 | Barely perceptible, subliminal |
| 6-7 | 0.5-0.8 | Noticeable but not distracting |
| 8-9 | 0.8-1.2 | Clearly audible, part of the experience |
| 10 | 1.2-1.5 | Loud, immersive, very casual feel |

## Tips

- Start with low volume and increase gradually during testing
- Coffee-shop is the safest default for most use cases
- Call-center adds professionalism without being distracting
- Static-noise is great for making the call feel like a real phone conversation
- Never use convention-hall at high volume -- it overwhelms the voice
- Test with the actual voice to make sure ambient does not interfere with clarity
