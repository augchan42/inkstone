# ADR-001: Conference Slide Typography Sizing

**Status:** Accepted
**Date:** 2026-05-17
**Context:** HKOSCon 2026 talk, 200+ person auditorium, 1920x1080 projection

## Decision

Override default viewport-base.css typography sizes with conference-appropriate minimums. The original sizes (body max 18px / ~13pt) are designed for browser viewing, not auditorium projection where the back row is 15-20 meters from the screen.

## Research (sources: BrightCarbon, Beautiful.ai, Superchart)

**Minimum font sizes for 200+ person rooms at 1920x1080:**

| Element | Minimum pt | Minimum px | Our CSS variable | Our max value |
|---------|-----------|-----------|-----------------|--------------|
| Title (h1) | 44-54pt | 59-72px | --title-size | 5rem (80px) |
| Heading (h2) | 36-44pt | 48-59px | --h2-size | 3.5rem (56px) |
| Sub-heading (h3) | 28-32pt | 37-43px | --h3-size | 2.5rem (40px) |
| Body text | 24-28pt | 32-37px | --body-size | 1.75rem (28px) |
| Captions/secondary | 20-24pt | 27-32px | --small-size | 1.35rem (21.6px) |
| Code | 18-22pt | 24-29px | --code-size | 1.2rem (19.2px) |

**Note:** Our body/small/code sizes are still below the strict minimums but represent a practical compromise — many slides have dense content (tables, pipeline diagrams, code blocks) that would overflow at 28pt+ body text. The priority is: if text can't be read from the back, it shouldn't be on the slide.

## Speaker Intro Slide Guidelines

- **40-60 words maximum** on a bio slide
- Include only: name, current role, one credential, one human detail
- Cut: year counts, degree details, exhaustive job history, contact info (save for closing slide)
- Audience cannot read and listen simultaneously — dense bio = they tune out the speaker

## QR Code Placement

- 40-60% scan rates at conferences when displayed during natural pauses
- Most effective on **closing slide** (not intro) — audience has context by then
- Minimum 150x150px on screen with one-line call to action
- LinkedIn preferred for professional conference networking

## Consequences

- Some content-heavy slides (tables, pipeline diagrams) may need content trimmed or split
- Code blocks limited to ~6-8 visible lines at these sizes
- Captions/metadata lines should be minimal (one line, key info only)
