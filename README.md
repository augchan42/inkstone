# Inkstone 硯台

**Composition rules and agent skills for generating Chinese ink paintings from classical verse using diffusion models.**

Inkstone is the methodology behind [SixLines.online](https://sixlines.online)'s image pipeline — 4,096 unique ink paintings generated from Han dynasty oracular poetry (the Jiaoshi Yilin, 焦氏易林, ~40 BCE). These rules and skills were developed iteratively across four rounds of testing and refined through generating the full corpus.

The name comes from the inkstone (硯台), one of the Four Treasures of the Study (文房四寶) — the tool you grind ink on before painting. This repo grinds classical Chinese verses into painterly prompts.

## What's Inside

```
skills/
├── verse-to-prompt.md      # The image generation skill (7 composition rules,
│                            # 5 style categories, content safety patterns)
└── create-explanation.md    # Bilingual scholarly explanation skill

examples/
└── prompt-examples.md       # 8 validated reference prompts, one per style
```

## The 7 Composition Rules

The core of Inkstone. Every prompt must follow all 7:

1. **Frame the scene** — gorges, gates, doorways, walls, tree canopies. Never a subject floating in open space.
2. **Force depth** — foreground, midground, and background elements in every prompt.
3. **Demand contrast** — at least one strong light source against darkness, or dark subject against light.
4. **Include a warm accent** — even in monochrome scenes, one element carries amber, vermillion, pink, or gold.
5. **Favor diagonals and verticals** — avoid flat horizontal compositions.
6. **Pack in discoverable detail** — the best images reward a second look.
7. **Use painterly scene language** — embed painterly metaphors throughout ("like ink drops", "pale threads", "like shattered porcelain"). NEVER use photographic language.

## Key Insight: Style Is Not a Suffix

The fundamental discovery: appending "Chinese ink painting style" to a prompt doesn't work. Diffusion models ignore trailing style directives. Instead, write prompts that *read like the caption under an ink painting*:

```
# Bad — style as suffix
"A tree on a hill. Chinese ink painting style."

# Good — painterly language embedded in the scene
"A gnarled pine leans from a cliff face like a brushstroke frozen mid-sweep,
its roots gripping stone above a gorge filled with morning mist. A single
vermillion leaf clings to the lowest branch. Far below, a river catches
the first light like spilled mercury. Chinese ink painting."
```

## Content Safety Patterns

52 of 4,096 images failed generation due to content filters. Ancient Chinese texts contain violence — the Yilin has verses about warfare, predation, and suffering. We developed a substitution table for depicting these themes through atmosphere and metaphor:

| Blocked concept | Safe alternative |
|----------------|-----------------|
| Blood on surfaces | "dark stains like spilled ink", "vermillion streaks on stone" |
| Fallen bodies | "abandoned armor on bare ground", "crows settling on a silent field" |
| Restraint / captivity | "a narrow gorge with no exit", "walls closing to a slit of sky" |

The full substitution table is in `skills/verse-to-prompt.md`.

**The principle:** Show the weight of violence through atmosphere, aftermath, and metaphor — never through the act itself.

## Usage

These skills are designed as agent skills (tested with Claude Code). You can use them:

1. **As Claude Code skills** — drop the `skills/` folder into your `.claude/skills/` directory
2. **As prompt engineering reference** — the composition rules and anti-patterns apply to any text-to-image workflow
3. **As a starting point** — adapt the style categories and rules for your own domain

The skills were validated with `fal-ai/z-image/turbo` but the composition principles are model-agnostic.

## Anti-Patterns

Things we tried that produced bad results:

- **Style-as-suffix** — appending "ink wash style" after a scene description (model ignores it)
- **Over-instruction** — 70+ word prompts with competing directives (model gets confused)
- **Flat composition** — horizontal scenes, even lighting, no framing elements
- **Sparse scenes** — too few elements, too much empty space
- **Photographic language** — "medium format", "film grain", "shallow depth of field" (model goes photorealistic)

## Background

- Blog post: [Teaching Taste to an Agent](https://augustinchan.dev/posts/teaching-taste-to-agents-yilin-image-pipeline)
- See sample output: [SixLines.online — Hexagram 14](https://sixlines.online/en/hexagrams/14) — ink paintings from the Jiaoshi Yilin
- Product: [SixLines.online](https://sixlines.online) — I-Ching reference and Chinese almanac for iOS
- The Jiaoshi Yilin is a ~40 BCE divination text by Jiao Yanshou (焦延壽), containing 4,096 oracular verses organized as 64×64 hexagram transformations

## License

MIT
