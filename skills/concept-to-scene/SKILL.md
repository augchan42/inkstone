---
name: concept-to-scene
description: Convert abstract symbolic concepts into embodied scene descriptions for image generation. Use when you have an abstract concept (chakra, sephirah, alchemical stage, rune, hexagram) and need to turn it into a scene with figures, gesture, and tension — not a diagram or symbol. Works across all mystical/esoteric traditions.
user-invocable: true
argument-hint: [tradition name] [concept name and brief description]
---

# Concept → Embodied Scene

Convert an abstract symbolic concept from any tradition into a **characters** + **action** scene description that slots into the 8-layer prophetic force prompt architecture.

## The Problem This Solves

Abstract concepts (lotus diagrams, geometric yantras, hexagram lines, sephiroth on a tree, alchemical symbols) produce flat, diagrammatic images when described literally. The prophetic force grammar works through **figures under tension** — bodies reaching, dissolving, hanging, kneeling, transforming. When a concept has no inherent figure, you must *create one* by finding the human experience the symbol encodes.

## Your Task

Given a concept (name + tradition + brief description), produce:

1. A **scene interpretation** — one sentence explaining what human experience this symbol encodes
2. A **characters block** (40-60 words) — who/what is in the scene, described physically
3. An **action block** (40-60 words) — what is happening in the scene, the moment of tension

## The Method: Symbol → Experience → Figure

Every abstract symbol encodes a felt experience. Find it:

| Symbol Type | Ask | Example |
|------------|-----|---------|
| Geometric (yantra, mandala, sigil) | What does it feel like to BE inside this geometry? | Anahata yantra → a figure whose chest is open, light pouring from the heart, caught between ascending and descending forces |
| Positional (sephirah on tree, chakra on spine) | What is the body doing at this threshold? | Da'at (the abyss) → a figure at the edge of a void, robes fraying into light above and nothing below |
| Process (alchemical stage, bardo state) | What is the figure becoming? Show the transformation mid-act. | Rubedo → two figures fusing into one form inside a vessel flooding with red fire |
| Elemental (Wu Xing phase, Greek element) | What is the element doing to/through a figure? | Water phase → a figure descending into dark water, the surface closing overhead |
| Relational (yin-yang, conjunction) | Show two figures or forces in the moment of meeting. | Coniunctio → a king and queen reaching toward each other, their outstretched hands beginning to merge |
| Cosmic (hexagram, odù) | What scene would make someone FEEL this hexagram's meaning? | Gé (Revolution) → a figure mid-molt, old skin splitting away, new form emerging raw |

## The 5 Constraints (MANDATORY)

Every scene MUST satisfy:

1. **At least one figure under tension** — a body reaching, dissolving, kneeling, hanging, transforming, resisting, yielding. Tension is non-negotiable. Static figures standing at rest are forbidden.
2. **The vertical axis encodes hierarchy** — what is above has authority over what is below. Use this. A figure reaching upward toward light, pressed downward by weight, caught between rising and falling.
3. **The symbol is implied, not depicted** — never describe the abstract symbol itself (no "a six-pointed star," no "the Tree of Life diagram," no "hexagram lines"). The scene must make the viewer FEEL the symbol without seeing it drawn.
4. **Specificity of body** — describe the figure's posture, gesture, clothing, expression. "A figure kneeling" is too vague. "A figure kneeling in absolute darkness, hands clasped, head bowed, body wracked with tension between agony and ecstasy" has presence.
5. **One moment, not a narrative** — freeze the scene at its point of maximum tension. Not "first this happened, then that." The image is a single instant.

## Content Safety (MANDATORY)

The same rules as verse-to-prompt apply. Show weight through atmosphere, aftermath, and metaphor — never through the act itself.

| Blocked concept | Safe alternative |
|----------------|-----------------|
| Blood / wounds | "dark stains like spilled ink", "vermillion streaks on stone" |
| Weapons contacting bodies | Aftermath — "sword embedded in earth", "arrow lodged in post" |
| Self-harm / self-sacrifice | Ordeal metaphor — "weathered by nine days", "body wracked with tension" |
| Dismemberment | Broken objects — "shattered vessel", "split tree trunk" |
| Graphic nudity | Cosmic forms — "luminous outline", "translucent figure" |

## Anti-Patterns

- **Describing the symbol literally** — "a twelve-petaled lotus with Sanskrit syllables" → flat diagram, not a scene
- **No figure** — pure landscape or pure geometry with no body → loses the prophetic force grammar
- **Multiple sequential moments** — "first he rises, then he falls, then he is reborn" → pick ONE moment
- **Tradition-as-costume** — don't just dress a generic figure in tradition-specific clothing. The scene itself must arise from the concept's meaning.
- **Over-specifying faces** — diffusion models struggle with specific facial expressions. Use body posture and gesture instead.

## Output Format

Present conversationally:

**Concept:** [tradition] — [concept name]

**Scene interpretation:** [One sentence: what human experience does this symbol encode?]

**Characters (for prompt layer):**
> [40-60 words describing who/what is physically present]

**Action (for prompt layer):**
> [40-60 words describing the moment of tension]

These slot directly into the 8-layer prompt architecture:
```
background → medium → composition → [characters] → [action] → palette → anti → closer
```

The style layers (background, medium, composition, palette, anti, closer) are handled separately — this skill produces only the two tradition-specific layers.

## Examples

### Input: Hinduism — Muladhara (Root Chakra)

**Scene interpretation:** The primal anchor — the body's first claim on existence, the weight that says "I am here."

**Characters:**
> A massive figure crouched at the base of a stone column that rises into darkness above — legs braced, hands pressed flat against the earth. The body is dense, heavy, made of the same stone as the ground. Four serpents coil around the figure's base, their heads raised and watchful.

**Action:**
> The figure presses downward with such force that cracks radiate through the stone floor — not destruction but rooting, the foundation driving itself deeper. The column above trembles with the energy transmitted upward. The serpents pulse with a slow, rhythmic glow. Everything above depends on this weight holding.

### Input: I-Ching — Hexagram 1, Qián (The Creative)

**Scene interpretation:** Pure creative force before it takes form — the dragon that rises through every stage of becoming.

**Characters:**
> A colossal figure ascending through layered clouds — arms reaching upward, body elongated and spiraling, robes trailing below into depths. The figure is neither young nor old, neither fully human nor fully dragon — scales flash along the forearms, the spine arches with serpentine grace.

**Action:**
> Six layers of cloud mark the ascent — the figure has already burst through five and strains toward the sixth, where blinding light awaits. Below, the earth is impossibly distant. The body stretches between ground and heaven, every muscle engaged in the act of rising. The moment before the final threshold.
