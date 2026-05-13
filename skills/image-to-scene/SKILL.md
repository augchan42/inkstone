---
name: image-to-scene
description: Convert an ink painting's original image prompt into a video generation motion prompt for image-to-video APIs. Requires the original verse-to-prompt output as input — never guess from a description alone.
user-invocable: true
argument-hint: [paste the original image prompt from verse-to-prompt]
---

# Image → Scene Prompt

Convert a static ink painting into a motion prompt for image-to-video generation. The motion prompt tells the video model what CHANGES between frame 1 and the last frame — not what the image looks like.

## Required Input

The **original image prompt** from `verse-to-prompt` is **mandatory**. This is the source of truth for what exists in the painting.

Acceptable inputs:
- The full verse-to-prompt output (preferred — has style, prompt, and translation)
- The image prompt string alone (e.g., "A river god rises from churning rapids...")
- A hexagram key (e.g., `44-44`) — you look up the prompt from `data/yilin/prompts/`

**Never generate a motion prompt from a verbal description, screenshot, or memory of a painting.** If you don't have the original image prompt, stop and ask for it.

## The Correspondence Rule

Every element named in the motion prompt MUST exist in the original image prompt. Read the image prompt, identify its movable elements (water, wind, figures, light, particles), and build motion ONLY from those.

```
# Original image prompt (source of truth):
"A river god rises from churning rapids, mouth open in a great shout,
arms spread to bar the crossing. Foreground, waves crash against a stone
ferry landing, spray flying diagonally. Midground, a traveler reins in
his horse at the water's edge, startled."

# Movable elements: rapids, waves, spray, horse, storm clouds
# NOT movable: river god (static pose), stone landing (architecture)

# Good motion prompt — only references elements from the image:
"Water surges forward, spray rising. Horse steps back nervously.
Storm light breaks through clouds. Static camera."

# Bad — adds elements not in the image:
"Birds scatter from the riverbank as fish leap from the water."
```

## Your Task

Given the original image prompt, produce:
1. A **motion classification** with a one-line rationale
2. A **movable elements** list extracted from the image prompt
3. A **15-25 word motion prompt** — motion and change only, no scene description
4. A **duration recommendation** (5s or 10s) with cost estimate
5. Optional: **loop instruction** if the clip should seamlessly loop

## The 5 Motion Categories

| Motion | Feel | Maps to Style | Signature Movements |
|--------|------|--------------|---------------------|
| `slow-reveal` | Contemplative, emerging from darkness | atmospheric-night | Fog drift, snow falling, flickering lantern light, slow push-in |
| `living-landscape` | Nature in gentle motion, timeless | ink-landscape | Water flow, cloud drift, wind through branches, rain on stone |
| `figure-breath` | Human presence, subtle life | figures-in-mist | Fabric ripple, hair movement, incense smoke, candle flicker |
| `kinetic-burst` | Explosive energy, frozen moment unfreezing | bold-action | Sudden motion, dust rise, water splash, animal leap |
| `celestial-drift` | Cosmic slow motion, eternal rotation | cosmic-night | Star trails, ascending mist, light pulses, floating particles |

## The 7 Motion Rules (MANDATORY)

1. **Only describe what changes** — The image already shows the scene. Your prompt is NOT a scene description. It is a set of technical instructions for what moves and how. If the image shows it, do not write it. If the image cannot show it (motion, time passing, light shifting), that is your prompt.

2. **Derive from the image prompt** — Read the original image prompt. List every element that could plausibly move (water, wind, fabric, animals, smoke, light). Pick 1-2 as your motion sources. Never invent elements.

3. **One primary motion, one secondary** — Video models fragment with competing directives. Pick the dominant movement and one ambient layer. Never three simultaneous motions.

4. **15-25 words, literal structure** — A motion prompt is a technical instruction set, not poetry or prose. Subject → Action → Camera → Settling cue. Every word must earn its place.

5. **Speed is always slow** — Ink paintings don't move fast. Use "gradually", "gently", "slowly". Even `kinetic-burst` builds slowly then releases one quick moment.

6. **Camera is usually static** — For i2v, `static camera` produces the most stable results. Only use camera motion (slow push-in, gentle pull-back) when the painting has strong depth corridors. Never orbit or pan.

7. **End with a settling cue** — The last few words prevent abrupt endings: "settling into stillness", "light fading", "motion easing". For loops, replace with: "End frame matches start frame for a seamless loop."

## Prompt Structure

```
[Camera], [primary motion]. [Secondary motion]. [Settling cue].
```

Keep it this tight. The model performs best with literal, specific instructions.

## Anti-Patterns

| Bad | Why | Fix |
|-----|-----|-----|
| "A mountain with a river and a bridge" | Describes the scene — image already shows it | Only describe what MOVES |
| "birds scatter from the riverbank" | Element not in original image prompt | Check the correspondence rule |
| "rapidly swooping, quick pan, dramatic zoom" | Too fast, too many camera moves | One slow camera move max |
| "the ancient warrior stands tall against the storm, his resolve unshaken" | Prose, not instruction | "Wind pushes his robes. Static camera." |
| "water flows, wind blows, birds fly, clouds move, figure walks" | 5 competing motions | Pick 1 primary + 1 secondary |
| 50+ word prompt | Fragments model attention, degrades output | Cut to 15-25 words |
| Prompt written without reading the image prompt | Correspondence violation | STOP — get the original prompt first |

## Duration & Cost Guidance

### Recommended Platform: Replicate

| Model | 720p/sec | 1080p/sec | 5s clip (720p) | Max duration | Audio |
|-------|----------|-----------|----------------|-------------|-------|
| **alibaba/happyhorse-1.0** | **$0.14** | **$0.28** | **$0.70** | 15s | No |
| bytedance/seedance-2.0 | $0.18 | $0.45 | $0.90 | 15s | Yes (native) |

Default to **Happy Horse, 720p, 5s** ($0.70/clip).

**Budget planning (720p, 5s):**

| Batch | Happy Horse | Seedance 2.0 |
|-------|------------|-------------|
| 64 hexagram hero videos | **$44.80** | $57.60 |
| 8 trigram videos (10s) | **$11.20** | $14.40 |
| 100 Yilin highlights | **$70.00** | $90.00 |

### API Input Reference

```python
import replicate

output = replicate.run(
    "alibaba/happyhorse-1.0",
    input={
        "prompt": "Water surges forward, spray rising. Horse steps back. Static camera.",
        "image": "https://cdn.example.com/44-44.webp",
        "duration": 5,
        "resolution": "720p",
        "seed": 42,
    }
)
```

**Happy Horse parameters:**
- `image` — first-frame image (jpg/png/bmp/webp, ≤10MB, each side ≥300px)
- `duration` — 3-15s integer
- `resolution` — `720p` or `1080p`
- `seed` — 0-2,147,483,647

**Seedance 2.0 additional parameters:**
- `last_frame_image` — optional end frame (controlled transitions)
- `generate_audio` — native audio sync
- `reference_images` — up to 9 style/character references (cannot use with `image`)
- `duration` supports `-1` for intelligent duration

## Output Format

**Original image prompt:**
> A river god rises from churning rapids, mouth open in a great shout, arms spread to bar the crossing. Foreground, waves crash against a stone ferry landing, spray flying diagonally. Midground, a traveler reins in his horse at the water's edge, startled. Beyond, the far bank is barely visible through mist and foam. Amber light breaks through storm clouds above the raging torrent. Chinese ink painting.

**Motion:** `kinetic-burst` — churning rapids and rearing horse provide two strong motion anchors

**Movable elements:** rapids/waves, spray, horse, storm clouds, amber light

**Prompt (5s):**
> Water surges forward, spray rising diagonally. Horse steps back. Storm light breaks through clouds. Static camera.

**Duration:** 5s — single tension moment, no arc needed  
**Cost:** ~$0.70 (Happy Horse 720p)  
**Loop:** No — the scene has directional energy, not cyclical

---

## Reference Prompts

### slow-reveal

**From:** "A frozen river valley under a dark sky split by driving snow..."  
**Movable:** snow, willow branches, lantern light  
> Slow push-in. Snow thickens. Willow branches tremble. Lantern light pulses warmer. Settling into stillness.

### living-landscape

**From:** "An empty market square in a river town, rain falling in gray sheets..."  
**Movable:** rain, puddle reflections, paper lantern  
> Rain falls steadily. Puddle reflections ripple. Red lantern sways. Light dims toward dusk. Static camera.

### figure-breath

**From:** "A betrothal ceremony in a courtyard dusted with autumn frost..."  
**Movable:** incense smoke, red silk, lantern light, frost glitter  
> Incense smoke curls upward. Red silk stirs in faint breeze. Lantern light shifts slowly. Static camera.

### kinetic-burst

**From:** "A massive tiger crouches low at a rocky stream..."  
**Movable:** tiger muscles, stream water, spray  
> Tiger shifts weight forward. Stream surges against rocks, spray catching light. Static camera. Tension building.

### celestial-drift

**From:** "An immortal sage ascending from a dark mountain pool on the back of a celestial horse..."  
**Movable:** horse's mane, cloud wisps, starfield reflection, gold light  
> Slow crane up. Horse's mane streams upward. Gold stars pulse brighter. Cloud wisps trail behind.

### looping example

**From:** "A gnarled pine leans from a cliff face..."  
**Movable:** mist, river light, vermillion leaf  
> Mist drifts through gorge. River light ripples. Leaf trembles. End frame matches start frame for a seamless loop. Static camera.
