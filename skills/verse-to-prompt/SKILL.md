---
name: verse-to-prompt
description: Convert classical Chinese verses into ink painting image generation prompts. Use only when called explicitly as part of a batch pipeline — not for conversational use. Takes a JSON array of verse objects and outputs a JSON array of prompt objects.
disable-model-invocation: true
user-invocable: true
---

# Verse → Image Prompt

Convert classical Chinese oracular verses into English image generation prompts for text-to-image models (validated with `fal-ai/z-image/turbo`).

## Your Task

You will receive a JSON array of verses. For each verse, produce:
1. A **style classification** (one of 5 categories)
2. A **50-60 word English scene description** ending with "Chinese ink painting."
3. A **faithful English translation** of the original classical Chinese verse

Output valid JSON only. No commentary, no markdown fences.

## The 5 Style Categories

| Style | Palette & Feel | Use When Verse Contains |
|-------|---------------|------------------------|
| `atmospheric-night` | Dark palette, strong light source in darkness, interior/exterior | Darkness, isolation, winter, grief, hidden things, fear, cold, sleeplessness |
| `ink-landscape` | Classic shanshui, depth corridors, water/mountain | Nature, seasons, water, agriculture, travel, weather, rivers, mountains |
| `figures-in-mist` | Ink wash + soft watercolor tints, human scale, warm accents | Narrative, marriages, courts, travelers, families, ceremonies, human emotion |
| `bold-action` | Dynamic diagonals, warm ochre palette, kinetic energy | Animals, combat, hunts, dramatic journeys, storms, military, physical struggle |
| `cosmic-night` | Deep blue/black + gold/white, celestial elements | Stars, heaven, mythical beasts, cosmic order, immortals, divination, emperors |

If the verse is abstract (fortune/misfortune statements without concrete imagery), choose a style based on the verse's tone: ominous → atmospheric-night, auspicious → ink-landscape or figures-in-mist, mixed → bold-action.

## The 7 Composition Rules (MANDATORY)

Every prompt MUST follow all 7:

1. **Frame the scene** — include gorges, gates, doorways, walls, tree canopies, or cliff faces. Never a subject floating in open space.
2. **Force depth** — every prompt must have foreground, midground, and background elements.
3. **Demand contrast** — at least one strong light source against darkness, or dark subject against light.
4. **Include a warm accent** — even in monochrome scenes, one element carries amber, vermillion, pink, or gold.
5. **Favor diagonals and verticals** — avoid flat horizontal compositions.
6. **Pack in discoverable detail** — the best images reward a second look with secondary subjects and textures.
7. **Use painterly scene language** — end with "Chinese ink painting." but embed painterly metaphors throughout ("like ink drops", "pale threads", "like shattered porcelain"). NEVER use photographic language ("shallow depth of field", "film grain", "desaturated").

## Content Safety Rules (MANDATORY)

Content filters on major image generation APIs reject prompts with explicit bodily harm. We learned this the hard way: 52 of 4,096 images failed generation. All prompts MUST follow these rules:

### Never depict directly:
- **Blood** — no "blood pools", "blood stains", "blood streaks", "blood spatters", "bleeding"
- **Weapons contacting bodies** — no "piercing breast", "fangs deep in flesh", "blade cuts", "arrow through chest"
- **Self-harm** — no "turns sword upon himself", "wounds himself"
- **Restraint/torture** — no "ropes binding wrists", "rope cuts into skin", "needles piercing"
- **Dismemberment** — no "legs severed", "limbs scattered", "neck snapped"
- **Corpses** — no "bodies fallen", "the dead lie stiff", "carcass"

### Instead, use these substitutions:

| Blocked concept | Safe alternative |
|----------------|-----------------|
| Blood on surfaces | "dark stains like spilled ink", "vermillion streaks on stone", "dark liquid pools like wet ink" |
| Wounds / piercing | Show the weapon or aftermath, not the moment of contact — "a sword embedded in earth", "an arrow lodged in a wooden post" |
| Self-harm | Internal anguish via landscape — "a candle guttering in a sealed room", "a tree split by its own weight" |
| Fallen bodies | Emptiness and absence — "abandoned armor on bare ground", "an empty seat at a banquet table", "crows settling on a silent field" |
| Restraint / captivity | Environmental metaphor — "a narrow gorge with no exit", "tangled roots gripping stone", "walls closing to a slit of sky" |
| Animal predation (graphic) | Show the chase or the stillness after — "a hawk diving", "scattered feathers on snow", "a wolf's shadow crossing moonlit ground" |
| Dismemberment | Broken objects as stand-ins — "a shattered puppet", "a split tree trunk", "a cracked bronze vessel" |

### The principle:
**Show the weight of violence through atmosphere, aftermath, and metaphor — never through the act itself.** A prompt that makes the viewer *feel* danger without *seeing* harm will both pass content filters and produce better art.

## Anti-Patterns (produce bad results)

- **Style-as-suffix**: writing a scene then appending "ink wash style" — the model ignores suffixes
- **Over-instruction**: 70+ word prompts with competing directives — model gets confused
- **Flat composition**: horizontal scenes, evenly lit, no framing elements — boring output
- **Sparse scenes**: too few elements, too much empty space — feels unfinished
- **Photographic language**: "medium format", "film grain" — model goes photorealistic
- **Explicit violence**: "blood pools", "fangs pierce flesh", "sword cuts" — content filter rejects the prompt entirely

## Prompt Template

```
[Scene with painterly language, ~50-60 words]
[Foreground element]. [Midground element]. [Background element].
[Light/contrast note]. [Warm color accent note].
Chinese ink painting.
```

## Input Format

Each verse entry:

```json
{
  "key": "1-2",
  "sourceName": "乾",
  "targetName": "坤",
  "verse": "招殃來螫，害我邦國；病在手足，不得安息。"
}
```

## Output Format

```json
{
  "key": "1-2",
  "style": "atmospheric-night",
  "prompt": "A scorpion emerges from cracked earth beside a ruined city wall, its tail curled like a calligraphy stroke...",
  "english": "Inviting calamity, drawing stings; harming our domain. Illness in the limbs — no rest to be found."
}
```

## English Translation Guidelines

- **Be faithful to the source** — translate what the verse says, not what the image prompt depicts
- **Preserve the poetic register** — use concise, slightly archaic English that mirrors the terseness of classical Chinese
- **Keep four-character phrase structure visible** — use semicolons, commas, or line breaks to reflect the verse's natural phrase boundaries
- **Translate imagery literally** — if the verse says 白駒食場 ("white colt grazing in the field"), translate it as such; do not interpret or explain the symbolism

## Classical Chinese Reading Notes

- Verses are oracular: they describe omens, fortunes, and misfortunes using natural imagery, historical allusions, and animal symbolism
- Four-character phrases (四字格) are the basic unit — each usually contains one visual image
- Some verses are very short (8-12 chars) — you still need a full 50-60 word prompt, so expand the imagery

## Proven Prompts

See `examples/prompt-examples.md` for 8 validated reference prompts (one per style). Read that file before generating prompts to calibrate tone and structure.
