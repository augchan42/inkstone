---
name: verse-to-prompt
description: Generate a Chinese ink painting image prompt from a classical Chinese verse
argument-hint: [paste your verse here]
---

# Verse → Ink Painting Prompt

Invokes the **verse-to-prompt** skill to convert a classical Chinese verse into a 50–60 word English image generation prompt.

## Output

- **Style**: one of five categories (atmospheric-night, ink-landscape, figures-in-mist, bold-action, cosmic-night) with rationale
- **Prompt**: 50–60 word scene following 7 composition rules, ending with "Chinese ink painting."
- **Translation**: faithful English rendering of the verse

## Usage

```
/inkstone:verse-to-prompt 道生一，一生二，二生三，三生万物
```

Or paste any classical Chinese verse as the argument.
