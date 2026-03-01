---
name: verse-to-prompt
description: Generate a Chinese ink painting image prompt from a classical Chinese verse. Use when the user pastes a classical Chinese verse and asks for an image prompt, wants to visualize a verse, or asks "what would this look like as an ink painting." Works with Yilin verses, I Ching lines, Tang poetry, or any classical Chinese text.
user-invocable: true
argument-hint: [paste your verse here]
---

# Verse → Ink Painting Prompt

Convert a classical Chinese verse into an English image generation prompt, following validated composition rules developed across 4,096 ink paintings for [SixLines.online](https://sixlines.online).

## Your Task

Given a verse (raw text, any format), produce:
1. A **style classification** with a one-line rationale
2. A **50-60 word English prompt** ending with "Chinese ink painting."
3. A **faithful English translation** of the verse

## The 5 Style Categories

| Style | Palette & Feel | Use When Verse Contains |
|-------|---------------|------------------------|
| `atmospheric-night` | Dark palette, strong light source in darkness | Darkness, isolation, winter, grief, hidden things, fear, cold, sleeplessness |
| `ink-landscape` | Classic shanshui, depth corridors, water/mountain | Nature, seasons, water, agriculture, travel, weather, rivers, mountains |
| `figures-in-mist` | Ink wash + soft watercolor tints, human scale | Narrative, marriages, courts, travelers, families, ceremonies, human emotion |
| `bold-action` | Dynamic diagonals, warm ochre palette, kinetic energy | Animals, combat, hunts, dramatic journeys, storms, military, physical struggle |
| `cosmic-night` | Deep blue/black + gold/white, celestial elements | Stars, heaven, mythical beasts, cosmic order, immortals, divination, emperors |

If the verse is abstract (fortune/misfortune without concrete imagery), choose by tone: ominous → `atmospheric-night`, auspicious → `ink-landscape` or `figures-in-mist`, mixed → `bold-action`.

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

Content filters on image generation APIs reject explicit bodily harm. All prompts MUST follow these rules:

### Never depict directly:
- **Blood** — no "blood pools", "blood stains", "blood streaks", "bleeding"
- **Weapons contacting bodies** — no "piercing breast", "fangs deep in flesh", "blade cuts"
- **Self-harm** — no "turns sword upon himself", "wounds himself"
- **Restraint/torture** — no "ropes binding wrists", "needles piercing"
- **Dismemberment** — no "legs severed", "limbs scattered"
- **Corpses** — no "bodies fallen", "the dead lie stiff"

### Instead, use these substitutions:

| Blocked concept | Safe alternative |
|----------------|-----------------|
| Blood on surfaces | "dark stains like spilled ink", "vermillion streaks on stone" |
| Wounds / piercing | Show aftermath — "a sword embedded in earth", "an arrow lodged in a wooden post" |
| Self-harm | Landscape metaphor — "a candle guttering in a sealed room", "a tree split by its own weight" |
| Fallen bodies | Emptiness — "abandoned armor on bare ground", "crows settling on a silent field" |
| Restraint | Environmental — "a narrow gorge with no exit", "walls closing to a slit of sky" |
| Animal predation | Show the chase or stillness after — "scattered feathers on snow", "a wolf's shadow crossing moonlit ground" |
| Dismemberment | Broken objects — "a shattered puppet", "a split tree trunk", "a cracked bronze vessel" |

**The principle:** Show the weight of violence through atmosphere, aftermath, and metaphor — never through the act itself.

## Anti-Patterns (produce bad results)

- **Style-as-suffix**: writing a scene then appending "ink wash style" — models ignore suffixes
- **Over-instruction**: 70+ word prompts with competing directives — model gets confused
- **Flat composition**: horizontal scenes, evenly lit, no framing elements — boring output
- **Sparse scenes**: too few elements, too much empty space — feels unfinished
- **Photographic language**: "medium format", "film grain" — model goes photorealistic
- **Explicit violence**: "blood pools", "fangs pierce flesh" — content filter rejects the prompt

## Output Format

Present the result conversationally:

**Style:** `ink-landscape` — the verse's imagery of water and travel maps directly to shanshui

**Prompt:**
> A lone traveler descends a mountain path like a brushstroke mid-sweep, pine boughs framing the narrow trail above. Below, a river catches pale light like spilled mercury; a vermillion-cloaked figure crosses a stone bridge in the midground. Mist fills the valley behind, fading into distant peaks. Chinese ink painting.

**Translation:**
> The white colt grazes the courtyard field; it leaps and is gone in a flash.

---

## Reference Prompts

See `examples/prompt-examples.md` for 8 validated reference prompts (one per style) to calibrate tone and structure before generating.

## Classical Chinese Reading Notes

- Verses are oracular: they describe omens, fortunes, and misfortunes using natural imagery, historical allusions, and animal symbolism
- Four-character phrases (四字格) are the basic unit — each usually contains one visual image
- Some verses are very short (8-12 chars) — you still need a full 50-60 word prompt, so expand the imagery
