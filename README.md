# Inkstone 硯台

**Custom Claude Code skills by Augustin Chan.**

A collection of agent skills for creative and design workflows, built for [Claude Code](https://claude.ai/code).

## Install

```shell
/plugin marketplace add augchan42/inkstone
/plugin install inkstone@augchan42-inkstone
```

## Skills

### Creative

| Skill | Description |
|-------|-------------|
| **verse-to-prompt** | Generate Chinese ink painting prompts from classical verse — 7 composition rules, 5 style categories, content safety patterns |
| **create-explanation** | Produce bilingual scholarly explanations for Jiaoshi Yilin verses |

### Design / UX

| Skill | Description |
|-------|-------------|
| **ui-ux-architect** | Premium UI/UX audit with Jobs/Ive philosophy — visual hierarchy, spacing, typography, color, motion, accessibility, dark mode |

## Usage

### Generate an ink painting prompt

Paste any classical Chinese verse — Yilin, I Ching lines, Tang poetry, fortune slips:

```
/verse-to-prompt 白駒食場，一躍而去。
```

**Style:** `ink-landscape` — the white colt's flash of movement maps to shanshui's sense of transience

**Prompt:**
> A white colt grazes in a walled courtyard, its mane catching pale morning light like brushed silk. Stone walls frame the scene; a gnarled plum tree leans at a diagonal in the midground. Beyond the open gate, mist swallows a mountain path. A single amber lantern glows above the gate arch. The colt is mid-leap, already half-gone. Chinese ink painting.

**Translation:**
> The white colt grazes the courtyard field; it leaps and is gone in a flash.

### Generate a bilingual explanation

```
/create-explanation 白駒食場，一躍而去。
```

**English**
A white colt grazes quietly in an enclosed field — then in a single bound, it vanishes. The image comes from the *Book of Songs* (詩經), where the white colt symbolizes a worthy person or fleeting opportunity. The "field" (場) suggests a bounded, domestic space; the leap outward marks an irreversible crossing. The verse captures the hexagram transition's essential quality: something precious was here, present and visible, and now it is gone. The loss is not violent but absolute — the field remains, the colt does not.

**繁體中文**
白駒於場中悠然食草，忽一躍而去，無影無蹤。白駒典出《詩經》，象徵賢才或良機。「場」為有界之地，躍出意味著不可挽回之離去。此詩捕捉卦變之質：珍貴之物曾在眼前，轉瞬即逝，場地猶存，而駒已杳然。

**References:** 白駒 (詩經), 場

## Background

### Ink Painting Skills

The ink painting skills are the methodology behind [SixLines.online](https://sixlines.online)'s image pipeline — 4,096 unique ink paintings generated from Han dynasty oracular poetry (the Jiaoshi Yilin, 焦氏易林, ~40 BCE). These rules were developed iteratively across four rounds of testing and refined through generating the full corpus.

The name comes from the inkstone (硯台, yàntái), one of the Four Treasures of the Study (文房四寶, wénfáng sìbǎo) — the stone slab on which an ink stick is ground with water to produce ink before painting or writing. The other three treasures are the brush (筆), ink stick (墨), and paper (紙).

The inkstone is the preparatory tool — it transforms a raw material into something ready to make art. That felt like the right metaphor for a collection of skills that transform raw classical verse into image prompts and explanations: the grinding happens here, before anything is painted.

#### The 7 Composition Rules

Every prompt must follow all 7:

1. **Frame the scene** — gorges, gates, doorways, walls, tree canopies. Never a subject floating in open space.
2. **Force depth** — foreground, midground, and background elements in every prompt.
3. **Demand contrast** — at least one strong light source against darkness, or dark subject against light.
4. **Include a warm accent** — even in monochrome scenes, one element carries amber, vermillion, pink, or gold.
5. **Favor diagonals and verticals** — avoid flat horizontal compositions.
6. **Pack in discoverable detail** — the best images reward a second look.
7. **Use painterly scene language** — embed painterly metaphors throughout ("like ink drops", "pale threads", "like shattered porcelain"). NEVER use photographic language.

#### Key Insight: Style Is Not a Suffix

Appending "Chinese ink painting style" to a prompt doesn't work. Text-to-image models ignore trailing style directives. Instead, write prompts that *read like the caption under an ink painting*:

```
# Bad — style as suffix
"A tree on a hill. Chinese ink painting style."

# Good — painterly language embedded in the scene
"A gnarled pine leans from a cliff face like a brushstroke frozen mid-sweep,
its roots gripping stone above a gorge filled with morning mist. A single
vermillion leaf clings to the lowest branch. Far below, a river catches
the first light like spilled mercury. Chinese ink painting."
```

#### Content Safety Patterns

52 of 4,096 images failed generation due to content filters. Ancient Chinese texts contain violence — the Yilin has verses about warfare, predation, and suffering. We developed a substitution table for depicting these themes through atmosphere and metaphor:

| Blocked concept | Safe alternative |
|----------------|-----------------|
| Blood on surfaces | "dark stains like spilled ink", "vermillion streaks on stone" |
| Fallen bodies | "abandoned armor on bare ground", "crows settling on a silent field" |
| Restraint / captivity | "a narrow gorge with no exit", "walls closing to a slit of sky" |

**The principle:** Show the weight of violence through atmosphere, aftermath, and metaphor — never through the act itself.

#### Anti-Patterns

Things we tried that produced bad results:

- **Style-as-suffix** — appending "ink wash style" after a scene description (model ignores it)
- **Over-instruction** — 70+ word prompts with competing directives (model gets confused)
- **Flat composition** — horizontal scenes, even lighting, no framing elements
- **Sparse scenes** — too few elements, too much empty space
- **Photographic language** — "medium format", "film grain", "shallow depth of field" (model goes photorealistic)

The skills were validated with `fal-ai/z-image/turbo` but the composition principles are model-agnostic.

#### Links

- Blog post: [Teaching Taste to an Agent](https://augustinchan.dev/posts/teaching-taste-to-agents-yilin-image-pipeline)
- Sample output: [SixLines.online — Hexagram 14](https://sixlines.online/en/hexagrams/14)
- Product: [SixLines.online](https://sixlines.online) — I-Ching reference and Chinese almanac for iOS
- The Jiaoshi Yilin is a ~40 BCE divination text by Jiao Yanshou (焦延壽), containing 4,096 oracular verses organized as 64x64 hexagram transformations

### UI/UX Architect

A design audit skill that evaluates screens against 13 dimensions (visual hierarchy, spacing, typography, color, alignment, components, iconography, motion, states, dark mode, density, responsiveness, accessibility). Uses mobile-mcp for live device inspection.

## License

MIT
