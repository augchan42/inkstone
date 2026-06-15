---
name: video-to-shorts
description: Use when turning a long video (interview, podcast, talk, lecture, webinar) into short vertical clips for YouTube Shorts / Reels / TikTok. Transcribes the source, auto-suggests the most engaging self-contained soundbites, then cuts, crops to 9:16, and burns in subtitles. Cross-platform (macOS / Linux / Windows-WSL). Stops at a finished, upload-ready vertical mp4 — no account or upload CLI required.
user-invocable: true
argument-hint: "[path or URL to the long video, optional: a topic/quote to clip]"
metadata:
  version: "1.0.0"
---

# Video → Shorts

Turn a long talking-head video into one or more polished vertical shorts (≤ 60s, 9:16, burned-in subtitles). The skill transcribes the source, **auto-suggests the best moments**, then cuts, crops, and subtitles a clip you approve.

The deliverable is a finished `*-en.mp4` ready to upload by hand. No YouTube account, API key, or upload CLI needed.

## When to use

- "Make shorts/reels/clips out of this podcast / interview / talk"
- "Find the best moments in this video and cut vertical clips"
- "Transcribe this and pull out quotable soundbites"
- Any long-form talking footage that needs to become short vertical content

Best for **static, single- or two-person talking footage**. Fast-cut montages, music videos, or heavy on-screen graphics need a human editor — flag that and stop.

## One-time setup (cross-platform)

You need three tools: **ffmpeg with libass** (cut/crop/burn-in), **Whisper** (transcription), and optionally **yt-dlp** (only if the source is a URL).

### ffmpeg — must include libass (for subtitle burn-in)

Check first: `ffmpeg -version | grep -o libass`. If it prints `libass`, you're done.

| OS | Install |
|----|---------|
| **Linux** | `sudo apt install ffmpeg` (Debian/Ubuntu builds include libass) — or `brew install ffmpeg` on Linuxbrew. |
| **Windows (WSL2)** | Inside Ubuntu-on-WSL: `sudo apt install ffmpeg`. Do everything from the WSL shell, not PowerShell. |
| **macOS** | ⚠️ Default Homebrew `ffmpeg` **omits libass** — the `subtitles` filter fails with a cryptic *"No option name near …"*. Install a libass static build to `~/.local/bin`: |

```bash
# macOS only — libass-enabled static ffmpeg
mkdir -p ~/.local/bin
curl -L https://evermeet.cx/ffmpeg/getrelease/ffmpeg/zip -o /tmp/ff.zip
unzip -o /tmp/ff.zip -d ~/.local/bin/
chmod +x ~/.local/bin/ffmpeg
~/.local/bin/ffmpeg -version | grep -E "libass|libfreetype"   # both must appear
```

On macOS, use `~/.local/bin/ffmpeg` for the **burn-in step only**; the system ffmpeg is fine for cut/crop.

### Whisper — transcription

| OS / hardware | Recommended | Install |
|---------------|-------------|---------|
| **macOS (Apple Silicon)** | `mlx-whisper` (GPU via MLX, fastest) | `pip install mlx-whisper` |
| **Linux + NVIDIA** | `faster-whisper` (CUDA) | `pip install faster-whisper` |
| **Any (CPU fallback)** | `openai-whisper` | `pip install -U openai-whisper` |

Models download lazily on first run (English `base` ≈ 140 MB; multilingual `large-v3` ≈ 3 GB). Use a venv to keep it clean.

### yt-dlp (only if source is a URL)

`pip install -U yt-dlp`. For unlisted/age-gated videos add `--cookies-from-browser chrome`.

## Workflow

### 1. Get the source video

- Local file → use directly.
- URL → download:
  ```bash
  yt-dlp -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]" \
    "<URL>" -o "/tmp/source.mp4"
  ```
- Note the source resolution (`ffprobe -v error -select_streams v -show_entries stream=width,height -of csv=p=0 source.mp4`) — you need it for the crop math.

### 2. Transcribe → SRT

Transcribe the **whole** source to an SRT with real timestamps. Pick the command for the platform:

```bash
# macOS (Apple Silicon)
mlx_whisper source.mp4 --model mlx-community/whisper-base-mlx \
  --language en --output-format srt --output-dir /tmp/transcript \
  --condition-on-previous-text False

# Linux + NVIDIA (faster-whisper via the CLI wrapper, or use the python API)
whisper-ctranslate2 source.mp4 --model base --language en \
  --output_format srt --output_dir /tmp/transcript --vad_filter True

# Any CPU (openai-whisper)
whisper source.mp4 --model base --language en \
  --output_format srt --output_dir /tmp/transcript
```

For non-English source, set `--language` accordingly (e.g. `zh`, `ja`, `es`). `--condition-on-previous-text False` (or `--condition_on_previous_text False`) reduces hallucination loops.

**Quick clean-up:** Whisper mangles proper nouns and often hallucinates text over intro music. Skim the SRT and fix names/products in any segment you plan to clip, and delete gibberish in the first block. A full proofread isn't needed yet — just enough to read the content.

### 3. Auto-suggest the best moments  ← the core value

Read the full SRT and propose the strongest short-worthy segments. A good short moment is:

- **Self-contained** — makes sense with zero setup; doesn't reference "what I just said."
- **A complete thought** — starts at a sentence start, ends at a sentence end.
- **Hooky** — a surprising claim, a strong opinion, a vivid story, a counterintuitive insight, a crisp how-to, or a quotable one-liner.
- **15–30s ideal, ≤ 60s hard max** (Shorts limit).

Present the top 5–8 candidates as a table the user can choose from:

| # | In–Out | Dur | Speaker | The hook (why it works) |
|---|--------|-----|---------|--------------------------|
| 1 | 12:04–12:31 | 27s | … | "…" — counterintuitive take on X |

**Never use chapter markers as cut points** — chapters mark a topic's start (with preamble), not the soundbite. Always anchor in/out to the actual SRT blocks where the line begins and ends.

If the user gave a topic/quote up front, find that segment instead (or in addition).

### 4. Confirm the segment & refine boundaries

Once the user picks a moment, confirm exact in/out from the SRT. For **static single-camera** footage, transcript timestamps are enough — skip ahead.

For footage with **camera cuts / slides / multi-cam**, keyframe-validate:

```bash
for t in START-2 START START+1 END-1 END END+2; do
  ffmpeg -y -ss <t> -i source.mp4 -frames:v 1 /tmp/kf_<t>.png
done
```
Read each frame: mid-blink? mouth frozen mid-word? slide changing? Shift the boundary ±0.5–2s for a clean in/out. Output the refined timestamps.

### 5. Determine the vertical crop — never guess

Decide the 9:16 crop **before** cutting. This is a **two-stage** decision: first *which side* the speaker is on, then *fine-tune the offset within that side*.

**a. Read the framing & pick the side.** Extract a frame from the middle of the segment and look at it:
   `ffmpeg -y -ss <MID> -i source.mp4 -frames:v 1 /tmp/mid.png`
   Decide which side of the frame the speaker occupies — **left, center, or right** — and confirm the camera is static (pull a second frame elsewhere in the segment; if it pans/cuts, a fixed crop may not work). This narrows the offset range you sample in step c — no point testing the empty half of the frame.

**b. Compute the crop size from the source height** (`ffprobe` it first). Both crop dimensions **and the x offset** must be **even** — libx264 (yuv420p) rejects odd values:
   - `crop_w` = `height × 9 ÷ 16`, rounded to the **nearest even** number.
   - `crop_h = height` (full height, so `y = 0`).
   - offset range: `x` runs from `0` (hard left) to `source_width − crop_w` (hard right); center is `(source_width − crop_w) ÷ 2`.

   | Source | crop_w × crop_h | left x | center x | right (max) x |
   |--------|-----------------|--------|----------|---------------|
   | 1920×1080 | **608×1080** | 0 | 656 | 1312 |
   | 1280×720  | **404×720**  | 0 | 438 | 876 |
   | 3840×2160 (4K) | **1216×2160** | 0 | 1312 | 2624 |

**c. Slice within the chosen side** — take **3–5 screenshots** at offsets spanning *only that side*, then present them and let the user pick. Composition depends on gaze direction (looking-room: leave space where they look), and what's in the background — an empty wall can be worse than a tighter, busier crop. The user decides.
   ```bash
   # Speaker on the LEFT of a 1920×1080 frame → sample left-half offsets:
   for x in 0 160 320 480 640; do
     ffmpeg -y -ss <MID> -i source.mp4 -frames:v 1 -vf "crop=608:1080:$x:0" /tmp/crop_$x.png
   done
   # Speaker on the RIGHT → sample right-half offsets up to max x (1312):
   #   for x in 704 856 1008 1160 1312; do ... done
   # Centered speaker → sample around center (e.g. 496 576 656 736 816).
   ```
   Keep all offsets even. Substitute your computed `crop_w`/max-x if the source isn't 1080p.

### 6. Cut & crop

Substitute your computed even `crop_w:crop_h` and `x` from step 2 (the `608:1080` below is the 1080p case):

```bash
ffmpeg -y -ss <IN> -to <OUT> -i source.mp4 \
  -vf "crop=608:1080:<X_OFFSET>:0" \
  -c:v libx264 -preset medium -crf 20 \
  -c:a aac -b:a 128k \
  /tmp/clip.mp4
```
Verify: extract a frame, confirm framing, confirm duration ≤ 60s, and **confirm the output is exactly your target dimensions** (`ffprobe -v error -select_streams v -show_entries stream=width,height -of csv=p=0 /tmp/clip.mp4`) — if ffmpeg silently shaved a pixel, your crop_w was odd.

*Optional — upscale to full 1080×1920 for max resolution:* append `,scale=1080:1920:flags=lanczos` to the `-vf` chain (a 608×1080 crop is true 9:16 but lower-res; platforms upscale it anyway, so this is optional).

### 7. Re-transcribe the CUT clip — don't offset the source SRT

⚠️ **Do not zero/offset the source SRT timestamps** — they drift and go out of sync by the end of the clip. Instead, run Whisper on the **cut clip itself** for accurate timings:

```bash
mlx_whisper /tmp/clip.mp4 --model mlx-community/whisper-base-mlx \
  --language en --output-format srt --output-dir /tmp/clip_srt \
  --condition-on-previous-text False
# (or the whisper / whisper-ctranslate2 equivalent for your platform)
```

Then write `clip.srt` using **Whisper's timestamps** but the **clean text** from the source SRT:

1. Read each Whisper block to identify *what* is said at that timestamp (its text may be garbled — use it as a phonetic guide, e.g. "a genetic engineering" = "agentic engineering").
2. Pull the matching clean wording from your reviewed source SRT.
3. Write clean text onto Whisper's timestamp boundaries; split/merge cues to read naturally.
4. **Keep cues short** — at the burn-in font size each line fits ~14–16 chars, so 2–4 short lines per cue, not long sentences.

### 8. Burn in subtitles

Shorts/Reels display caption tracks unreliably on mobile, so bake subs into the pixels. Keep the un-subtitled `clip.mp4` so you can burn other languages later.

```bash
# macOS: use ~/.local/bin/ffmpeg   |   Linux/WSL: use ffmpeg
ffmpeg -y -i /tmp/clip.mp4 \
  -vf "subtitles=/tmp/clip_srt/clip.srt:force_style='FontName=Arial,FontSize=16,Bold=1,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=2,Shadow=0,Alignment=2,MarginV=60'" \
  -c:v libx264 -preset medium -crf 20 -c:a copy \
  /tmp/clip-en.mp4
```

Style choices (don't change without reason):
- `FontSize=16` — mobile-legible (~44–48px on 1080; libass scales to its internal PlayResY of 288). Each line fits ~14–16 chars.
- `Bold=1`, `Outline=2`, `Shadow=0` — readable on any backdrop, no shadow noise.
- `Alignment=2`, `MarginV=60` — bottom-center, in the lower third, above the platform UI band. Bump `MarginV` to 80–100 if the bottom line gets clipped.
- `-c:a copy` — preserve speech audio, no re-encode.

### 9. Verify & deliver

- Extract frames at 3–5 timestamps and check subs are on-screen, in sync, not clipped:
  `ffmpeg -ss <N> -i /tmp/clip-en.mp4 -frames:v 1 /tmp/check_<N>.png`
- On macOS, `open /tmp/clip-en.mp4` for a real-time preview.
- Final output is `<slug>-en.mp4`. Report the path. Done — ready to upload by hand.

## Output conventions

For each short, keep:
- `<slug>.mp4` — cropped clip, no subs (reuse for other languages)
- `<slug>-en.mp4` — burned-in final ← the deliverable
- `<slug>.srt` — the clip's subtitle file
- `<slug>.md` — cut metadata (source, in/out, duration, crop offset)

`slug` = kebab-case summary of the moment, e.g. `capability-not-functionality`.

## Common mistakes

| Mistake | Do instead |
|---------|------------|
| Offsetting the source SRT to start at 0 | Re-transcribe the cut clip (step 7) — offsets drift |
| Using chapter timestamps as cut points | Anchor to the actual SRT block where the line starts |
| Guessing the crop position | First pick the speaker's side, then slice 3–5 offsets within that side; let the user pick |
| Odd crop width/height (e.g. 405) | Round to **even** — libx264 errors or silently shifts a pixel otherwise |
| Copy-pasting `608:1080` on a non-1080p source | Recompute crop_w from the source height (step 2 table) |
| Long sentences on one subtitle cue | Short phrases, ~14–16 chars/line, 2–4 lines |
| Burning subs with default macOS Homebrew ffmpeg | Use the libass static build (`~/.local/bin/ffmpeg`) |
| Clip over 60s | Trim to ≤ 60s (Shorts limit); 15–30s is ideal |
| Mapping source SRT blocks 1:1 onto Whisper timestamps | Read Whisper text to find what's actually said, then place clean text |
