# HKOSCon 2026 — Speaker Script

**Talk:** Teaching Taste to an Agent — Ink Painting Prompts from Classical Verse
**Speaker:** Augustin Chan
**Format:** 23 slides, ~25 min talk + 5 min Q&A
**Pacing:** ~65 sec/slide average. Slides 1-3 (intro) and 22-23 (close) go fast. Slides 11-13 (breakthrough) and 17 (mechanism) get the most time.

---

## Slide 1 — Title

> Hi everyone. I'm Augustin Chan. This talk is about teaching an AI to make Chinese ink paintings from ancient verse — and what that taught me about turning human judgment into reusable tools.

**Notes:** Keep it short. The subtitle does the work. ~15 sec.

---

## Slide 2 — Speaker Intro

> Quick intro — I run Digital Rain Technologies. The app behind this talk is SixLines.online, an I-Ching reference app. I also co-host the Hong Kong AI Podcast with friends, and I write about AI at augustinchan.dev. LinkedIn QR is on the right if you want to connect.

**Notes:** Don't linger. Point at the QR, move on. ~30 sec.

---

## Slide 3 — Podcast

> Quick plug — the Hong Kong AI Podcast. We talk with researchers, founders, engineers working in AI here in Hong Kong. Have a listen if you're interested. QR code is right there.

**Notes:** This is a 15-second slide. Smile, point at QR, advance.

---

## Slide 4 — I-Ching Primer

> For those who don't know the I-Ching — it's one of the oldest books in the world. It has 64 hexagrams. Each hexagram is six lines — solid or broken — stacked in two groups of three. Each group is called a trigram and represents something in nature. This one is Mountain over Water — Hexagram 4, "Youthful Folly." These hexagrams are the structure behind all the artwork I'll show you.

**Notes:** Gesture at the hexagram lines and trigram labels. Many in the HK audience will know the I-Ching (易經) already — this slide is for international attendees. ~45 sec.

---

## Slide 5 — The Challenge

> My app needed artwork. One painting for every verse in the Jiaoshi Yilin — a 2,000-year-old commentary on the I-Ching. That's 4,096 verses. 64 hexagrams times 64. Each verse is a short poem — four to eight lines of classical Chinese. I needed to turn every one of them into a unique ink painting. The question was: how?

**Notes:** Let the numbers land. Point at the app screenshot. ~45 sec.

---

## Slide 6 — What Is Taste? (Thesis)

> Which brings us to the real question. What is taste? Here's my working definition: taste is pattern recognition that you build up through practice — through looking at many examples and deciding what works and what doesn't. You can't write it down as a spec before you start. It only comes out through doing the work. So how do you teach that kind of judgment to a machine?

**Notes:** This is the thesis. Read the quote block. Let the question hang for a beat before advancing. ~50 sec.

---

## Slide 7 — The Iterative Loop

> Here's the process I ended up with. Four steps in a loop. First, the human looks at the output and says: "This one is good." Second, you show the AI the good ones. Third, the AI looks at them and figures out what made them work — what patterns they share. Fourth, the human decides which of those patterns to keep as rules. Then you repeat. The important thing is: the rules at the end are the *result* of this loop. I didn't start with them.

**Notes:** Walk through the four nodes left-to-right. Emphasise the last line — the rules are output, not input. ~60 sec.

---

## Slide 8 — Not All Verses Paint Pictures

> But there's a problem. Not all verses give you something to paint. Only about 19% have strong visual imagery — frost on mountains, phoenixes, rivers. Half of them give you a starting image but not enough for a full scene. And 31% are completely abstract — things like "Great fortune, no blame" — just good or bad luck with no picture at all. The skill has to handle all three kinds.

**Notes:** Gesture across the three columns. Read one example from each. The Chinese examples add authenticity — read them if comfortable, skip if not. ~60 sec.

---

## Slide 9 — Round 1: Style as Suffix

> So let's walk through how I got there. Round 1: I did what everyone tries first. I described the scene from the verse, then added "ink wash with soft watercolor tints" at the end. And I got this. It's flat. There's no life in it. The AI treated "ink wash" like an Instagram filter — it changed the colours but not the composition.

**Notes:** Let the bad image speak for itself. ~40 sec.

---

## Slide 10 — Round 2: Try a Different Style?

> Round 2: Maybe the style was wrong? I tried "wabi-sabi aesthetic, muted tones." And the AI gave me... a photograph. Not a painting at all. The style label at the end actually changed the whole medium.

**Notes:** Quick slide. The punchline is "not even an ink painting." ~30 sec.

---

## Slide 11 — Core Discovery: Style Is Not a Suffix

> That's when I understood. You can't bolt on style at the end. The whole prompt has to sound like it belongs under an ink painting. Instead of "a tree on a hill, Chinese ink painting style" — you write "a gnarled pine leans from a cliff face like a brushstroke frozen mid-sweep." The style is in the language, not in a label.

**Notes:** This is the key insight of the entire talk. Read both examples from the code block — bad vs. good. Slow down here. ~60 sec.

---

## Slide 12 — The Breakthrough Prompt

> Same verse about the overflowing well. But now I'm writing it like the caption under a painting. Three layers: foreground — the well mouth brims over, water on worn stone. Midground — streams spread out across dry ground. Background — brown hills fading into haze. Every one of the seven composition rules is woven in. Nothing is appended at the end.

**Notes:** Walk through the three bullet points. This is the "how" for the audience. ~50 sec.

---

## Slide 13 — Same Verse, All 7 Rules (Result)

> And here's what came out. Same verse, same AI model, same API. But the prompt reads like art direction. You can see the depth — foreground, middle, background. The warm amber accent. The framing. That's the full prompt on the right — 52 words ending with "Chinese ink painting."

**Notes:** Let the image breathe. Point at the prompt text. This is the payoff for slides 9-12. ~45 sec.

---

## Slide 14 — What the AI Analyzed

> So the human said "this works." Now the AI figured out why. Four observations. One: the style of language controls what kind of image you get — painterly words make paintings. Two: describing foreground, midground, background forces the AI to build depth. Three: a single warm colour in a grey scene gives the viewer's eye somewhere to land. Four: putting something at the edges — a gate, a cliff, a tree canopy — prevents the subject from floating in empty space.

**Notes:** Walk down the four items on the left. Point at the image on the right — "all four visible here." ~60 sec.

---

## Slide 15 — What the Human Kept

> From dozens of AI observations, I chose which ones to keep. On the left: seven mandatory composition rules — frame the scene, force depth, demand contrast, warm accent, favour diagonals, discoverable detail, and painterly language. On the right: five style categories — atmospheric-night, ink-landscape, figures-in-mist, bold-action, cosmic-night. Each style has a colour palette and a set of verse themes that map to it. I'll show you exactly how that mapping works in a moment — especially for the hard cases.

**Notes:** Quick overview — don't read every item. The forward reference sets up slide 18 (abstract verses). ~50 sec.

---

## Slide 16 — The Results (Gallery)

> Here's a sample across all five styles. Each image is from a different verse, generated by the same model with the same rules. The skill picked the style based on what the verse is about. You can see the range — night scenes, landscapes, figures, action, celestial.

**Notes:** Let the images do the talking. Brief narration. ~30 sec.

---

## Slide 17 — Four Rounds to a Skill (Timeline)

> Quick summary of the journey. Four rounds. Round 1: style as suffix — failed. Round 2: try different styles — wrong medium. Round 3: make the language itself painterly — breakthrough. Round 4: write everything down as rules and generate all 4,096 images. The final skill has 5 style categories, 7 composition rules, 8 reference prompts, and 7 safety patterns for the 52 verses that hit content filters — those are the violent ones where we show atmosphere and aftermath instead of the act.

**Notes:** This is a recap that wraps up the "build journey" arc. Move through briskly. The stats at the bottom are a nice visual — gesture at them. ~45 sec.

---

## Slide 18 — Abstract Verses: The Mechanism

> But what about the hard cases? Remember that 31% of verses with no imagery at all? Look at the left side. The verse: "Great fortune, no blame. Peace without peril." There's nothing to paint here. And below it — the painting the AI made anyway.
>
> How? Look at the right side. This is actual code from the skill file. There's a fallback rule: if the verse is abstract, look at the tone. Ominous goes to atmospheric-night. Auspicious goes to ink-landscape. And the composition rules still apply — frame the scene, force depth, include a warm accent. These rules force the AI to invent real visual elements even when the verse gives it nothing.
>
> Below the code — the AI's output. It reads "auspicious," picks ink-landscape, invents a temple gate for framing, puts worn stone steps in the foreground, a wanderer midground, hazy peaks in the background, and golden-hour light as the accent. The rules turned nothing into that painting on the left.

**Notes:** This is the most important teaching slide. Point left (verse + painting), then right (mechanism + output). The audience sees input and result together on one side, and the "how" on the other. ~90 sec.

---

## Slide 19 — What Is a Skill?

> So what does the final product look like? It's a file called SKILL.md. YAML header at the top — name, description, how to use it. Then instructions — the composition rules, the style table, the reference prompts, everything. No code. No dependencies. Just a document that tells the AI how to do this task well. A skill carries pre-tested expertise. The agent doesn't have to rediscover any of this — it inherits it.

**Notes:** Point at the code block. Emphasise "no code." ~50 sec.

---

## Slide 20 — Plugins vs Skills

> Quick distinction. A plugin is a package — a Git repository with a manifest file. It contains one or more skills. You install the plugin, and the skills become available. A skill is one SKILL.md file that defines one specific thing the agent can do. On the right you can see what it looks like when someone invokes the skill — they type the command, paste a verse, and get back a style classification and a prompt.

**Notes:** Two columns, simple distinction. Don't over-explain. ~40 sec.

---

## Slide 21 — The Inkstone Plugin

> The full collection is called Inkstone. Eight skills — verse-to-prompt is the one we've been talking about, but there's also image-to-scene for turning paintings into video prompts, create-explanation for bilingual scholarly text, blakean-scene for abstract concept visualisation, a UI/UX audit tool, and a media kit generator. It's open source on GitHub and works in Cursor too.

**Notes:** Gesture at the skill cards. Don't read every one. ~40 sec.

---

## Slide 22 — Beyond Claude Code

> And this approach isn't limited to one tool. GitHub Copilot already reads SKILL.md files. OpenCode supports the same format. Cursor can use them too. The broader point is: if you have domain expertise that you've refined through practice, you can encode it as a structured document and any AI agent can use it. What expertise could *you* turn into a skill?

**Notes:** The rhetorical question at the end is the real takeaway for the audience. Let it land. ~40 sec.

---

## Slide 23 — Takeaways

> Four things to take away. One: taste is iterative — you build it through loops, not by specifying it upfront. Two: show, don't tell — examples teach more than abstract rules. Three: the human judges, the AI explains — then the human decides which explanations to keep. Four: a skill is the output of that whole process — distilled taste in a file.

**Notes:** Walk through each takeaway. This is the last content slide before the close. ~40 sec.

---

## Slide 24 — Thank You / Questions

> That's the talk. Thank you all very much. The app is SixLines.online — iOS and Android. The plugin is open source on GitHub. QR codes for the slides and my LinkedIn are on screen. I'm happy to take questions, and I'll also be around after if you want to chat.

**Notes:** 5 minutes for Q&A per organiser guidance. If no questions come, have one or two you can ask yourself:
- "A question I often get is: does this approach work for other art styles, not just ink painting? The answer is yes — the same iterative loop works. The blakean-scene skill in the same plugin was built the same way for a completely different aesthetic."
- "Another common question: what happens when the AI model changes? The skill is model-agnostic — it's instructions, not code. When we switched image models during the project, the same skill worked with minor tuning."

---

## Timing Guide

| Section | Slides | Time |
|---------|--------|------|
| Intro & context | 1-5 | ~3 min |
| Thesis & method | 6-8 | ~3 min |
| The journey (failure to breakthrough) | 9-13 | ~4 min |
| Analysis & encoding | 14-16 | ~3 min |
| Journey recap (timeline) | 17 | ~45 sec |
| The mechanism (abstract verses) | 18 | ~1.5 min |
| What's a skill & plugin ecosystem | 19-22 | ~3 min |
| Takeaways & close | 23-24 | ~2 min |
| **Total talk** | | **~20 min** |
| Q&A | | **5 min** |

## Language Notes

- Avoid "LLM" in speech — say "the AI" or "the agent"
- Avoid "encode" when possible — say "write down" or "turn into rules"
- "Composition rules" is fine — it's an art term the audience will understand
- "Prompt" is understood broadly — no need to define it
- "SKILL.md" and "plugin" may need brief explanation for non-dev attendees — slides 20-21 handle this
- When reading Chinese verses, read naturally — the audience will appreciate it even if some don't follow every character
- For the code block on slide 18, say "this is actual code from the skill file" rather than "YAML frontmatter" — keep it concrete
