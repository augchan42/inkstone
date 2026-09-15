# Editing a short for retention

Read this before you cut. A short that is only a trimmed, cropped copy of the source
plays as a flat locked-off shot. Viewers swipe away from that in the first seconds. The
rules below turn the same footage into a short that people watch to the end.

Sources:
- A professional reviewer's notes on our first podcast shorts (2026-09-15).
- The craft playbooks in [podcast-shorts-factory](https://github.com/krakonjac300-pixel/podcast-shorts-factory) (MIT, Kosta Rakonjac).
- The scoring rubric and caption presets in [claude-shorts](https://github.com/AgriciDaniel/claude-shorts) (MIT, Daniel Agrici).

We tested these rules on our own shorts and rewrote them here. Where a rule is theirs,
the idea is credited.

## 1. Choose moments that stand alone

Score each candidate on five dimensions from 0 to 100, then weight them (from claude-shorts):

| Dimension | Weight | High score | Low score |
|---|---|---|---|
| Hook strength | 0.30 | bold claim, curiosity gap, specific number, story cold-open | "So today I want to talk about…" |
| Standalone | 0.25 | a full setup → development → payoff | "as I said", "he" with no referent, ends mid-thought |
| Emotion | 0.20 | conviction, surprise, real laughter, honest failure | calm recital of facts |
| Value density | 0.15 | a method, a framework, a specific number | vague platitudes |
| Payoff | 0.10 | a punchline or a line people would quote | fades into the next topic |

Skip candidates that score below 60. Prefer 25-45 s. A moment does not need a full
back-and-forth. One person with a clear hook and payoff is enough.

The podcast-shorts-factory trainer measured this: pure-education moments score well on
paper but get few views unless a strong personality delivers them with heat. Prefer the
moment where somebody reacts, disagrees or laughs.

## 2. Put the hook first

- The first 1-3 seconds decide the swipe. Start on the first spoken word of the hook. Do
  not start on a breath, a glance away or "well, you know".
- If the strongest line comes 10 s into the moment, **move it to the front** as a cold open.
  Then play the story from its start. Cut the line from its original place, so it does
  not play twice.
- Do not spoil the payoff. The hook raises the question, and the payoff answers it last.
  In "past life in China", the hook is "I think I might have a past life… in China" and
  the payoff is the Jesuit joke that comes after it.

## 3. Cut to whoever speaks, and to reactions

- **Every line gets the speaker's shot, however short.** A two-word interjection such as
  "Déjà vu." or "Normandy." gets its own cut. A locked shot on one person during the
  other person's line looks flat. This was the reviewer's main note.
- **Reaction shots.** While one person tells the story, cut to the listener for 1.5-2 s at
  a moment when their face reacts (a smile, a laugh). Check the frames first. The listener
  must visibly react, or the cut reads as a mistake. A reaction shot keeps the speaker's
  audio. Who is *speaking* comes from the audio, never from a frame.
- **Punch-ins.** Alternate the normal crop with a tighter one (about 1.2x) on the same
  speaker at a sentence boundary. This changes the shot without changing the person. It
  also hides a jump cut where you trimmed a pause.
- **Rhythm.** Something changes on screen every 2-6 s: a cut, a punch-in or a new caption
  page. Use more cuts in the hook and longer holds in the story beats. Do not cut on a
  regular beat (from podcast-shorts-factory "editor-craft").
- **Restraint.** Each cut must either entertain more or explain better. Do not add
  decorative overlays, stock images or a different transition on every cut.

## 4. Tighten, but keep the voice

- Trim pauses longer than about 0.7 s down to 0.3-0.5 s. Keep a pause that sets up a
  punchline.
- Cut repetitions and false starts ("since I believe… since I believe"), but only at real
  word gaps, and only where the video jump is hidden by a cut or a punch-in.
- Cut only in audio valleys (SKILL.md step 6, "Cut in quiet"). Put a 30 ms fade
  on each side of every join that jumps in time. A join between two shots that are
  continuous in the source needs no fade.

## 5. Captions carry the short

About 85% of short-form video is watched muted (figure from podcast-shorts-factory).

- **Build captions from the word timings, not from cleaned sentences.** Captions that
  paraphrase or skip what is said look wrong on screen. Fix only misheard words
  ("infinity" → "affinity"), never the grammar.
- **One phrase at a time:** 1-4 words, one line, and a new page at every punctuation mark,
  every pause over 0.3 s and every cut. Never more than about 5 words on screen.
- **Highlight the active word** in an accent colour (karaoke style). This is the
  highest-retention default. Offer a plain-phrase version and a one-word version too, so
  the owner can pick.
- **Big and heavy:** a display font with capitals about 80 px high on a 1080x1920 frame.
  One line then fits about 18 characters. Use white fill, a 9 px black outline, no shadow,
  and a small pop-in scale on each page. libass sizes a font by its ascender plus
  descender, so Anton needs `Fontsize=170` to get 80 px capitals. Measure a rendered frame;
  do not trust the number.
- **Placement:** keep text out of the platform UI zones (top 12%, bottom 18%). If the faces
  sit low in the frame, put the captions near the top.
- Leave each page on screen for at least 0.45 s.

## 6. Name the guest

Show name and job title in a lower third for about 3.5 s the first time the guest
appears. Do not add a second text element that competes with the captions at the same
moment.

Check frames across the **whole** time the card is on screen, not one frame. A seated
guest in a 9:16 crop often has the mouth and chin at the height of a normal lower third.
If the card covers the face, move it into the empty space above the head (`"y": 520`
in the spec, under top captions), not further down: the bottom 18% is under the
platform UI. Take the title from the guest's own words or material, never invent it.

## 7. Let the end breathe, then brand it

- Do not cut on the last syllable. Hold 0.7-1.0 s after the payoff line, and end on a
  reaction if there is one. Then fade picture and sound to black over about 0.6 s.
- End card, about 2.8 s: the show logo on black, a call to action ("SUBSCRIBE"), the URL,
  and a short **ding** when the logo lands. The ding can be synthesized, so no stock
  sound file is needed (see the build script).
- This works against a seamless loop. Choose one per short. The reviewer asked for the end
  card on podcast shorts.

## 8. Speed

A speed-up of 1.1-1.25x with pitch kept (`atempo`) makes a slow talker sound lively.
Render 1.0x, 1.15x and 1.25x and let someone who has **not** heard the original choose.
Anyone who knows the speaker's voice will hear the speed-up first.

## 9. Loudness

Normalize to about -14 LUFS integrated, with a limiter at -1 dBFS. YouTube turns louder
clips down to its target but does not lift quieter ones, so a clip at -17 LUFS plays quieter
than the one before it.

## Final check

Watch the whole short as a stranger would. Check for:
- visible cut artifacts
- text that overflows or cannot be read
- more than one focal point at once
- uneven audio levels
- a hook that does not deliver what the title promises
- a payoff that comes too early
