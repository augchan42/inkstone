#!/usr/bin/env python3
"""
Render a vertical short from an edit list. Part of the inkstone video-to-shorts skill;
the editing rules are in ../references/retention-edit.md and ../references/two-speaker.md.

What it makes: the shots in edit-list order (hook first if the list says so), each cropped
from the source and scaled to 1080x1920; captions one phrase at a time from the word
timings; a name lower third; a held ending that fades to black; an end card with the show
logo, a call to action and a synthesized ding; loudness at -14 LUFS. One render per
variant (speed x caption style), so the owner can pick.

Spec (JSON):
  slug         name of the short; output is <out_dir>/<slug>-<variant>.mp4
  raw          source video; crops are in its pixels
  audio        optional: audio on the same timeline (e.g. a normalised master); default raw
  lut          optional: .cube LUT, applied after crop and scale (log footage)
  words        word-timestamp JSON: {"segments": [{"words": [{"start", "end", "word"}]}]}
               (stable-ts save_as_json, or faster-whisper word_timestamps dumped the same way)
  fonts        folder with the caption fonts (default families: Anton, IBM Plex Mono Medium)
  workdir      cache for shot pieces and the end card (default shorts-work/<slug>)
  out_dir      where the variants go (default .)
  crops        {"C": [x, y, w, h], ...}: w:h must be 9:16 and every number even
  shots        [[src_in, src_out, crop], ...] in OUTPUT order. A shot that starts where the
               previous one ended in the source joins with no fade; any other join gets
               30 ms audio fades on both sides.
  replace      {"infinity": "affinity"}: misheard-word fixes (case-insensitive, punctuation kept)
  patch        [[t0, t1, [[start, end, "word"], ...]], ...]: replaces the transcript's words
               in t0..t1 (words Whisper missed or misplaced)
  lower_third  {"name", "sub", "at", "dur"}: output seconds before any speed-up
  endcard      {"logo", "cta", "url", "dur"}
  fade         seconds of fade to black at the end (default 0.6)
  lufs         loudness target (default -14)
  variants     {"hl-115": {"speed": 1.15, "captions": "highlight"|"phrase"|"word"}, ...}

Usage:
  build-short.py <spec.json> [variant ...]        # default: every variant

Needs ffmpeg with libass (and lut3d if you use a LUT). Set FFMPEG=<path> to choose the
binary. Text is drawn with libass, not drawtext, so a build without libfreetype works.
Shots render once and are cached by frame range and crop, so re-running after an edit to
captions, the lower third or the variants costs one 1080p pass per variant.
"""
import json, os, re, subprocess, sys

FF = os.environ.get("FFMPEG") or next((p for p in [os.path.expanduser("~/.local/bin/ffmpeg")] if os.path.exists(p)), "ffmpeg")
FPS = "30000/1001"
FR = 1001 / 30000
AMBER, CREAM, WHITE = "&H0000B8FF", "&H00B4DDF0", "&H00FFFFFF"   # ASS colours are &HAABBGGRR


def run(args, capture=False):
    r = subprocess.run(args, capture_output=True, text=True)
    if r.returncode:
        print(" ".join(args)[:600]); print(r.stderr[-2500:]); sys.exit(1)
    return r.stdout + r.stderr if capture else ""


def fidx(t): return round(t / FR)


def ts(x):
    x = max(0.0, x); cs = int(round(x * 100))
    return f"{cs // 360000}:{cs // 6000 % 60:02d}:{cs // 100 % 60:02d}.{cs % 100:02d}"


HEAD = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,{disp},{cap},&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,0,0,0,0,100,100,1,0,1,9,0,8,40,40,0,1
Style: Lower,{disp},100,{cream},{cream},&H00000000,&H90000000,0,0,0,0,100,100,1,0,3,16,0,1,0,0,0,1
Style: LowerSub,{mono},44,{cream},{cream},&H00000000,&H90000000,0,0,0,0,100,100,0,0,3,12,0,1,0,0,0,1
Style: Cta,{disp},190,{accent},{accent},&H00000000,&H00000000,0,0,0,0,100,100,3,0,1,0,0,5,0,0,0,1
Style: Url,{mono},60,{cream},{cream},&H00000000,&H00000000,0,0,0,0,100,100,1,0,1,0,0,5,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def head(spec):
    # libass fits a font's ascender+descender into Fontsize. Anton's are tall, so its capitals
    # come out at about 0.47 x the size: 170 gives ~80 px caps on a 1920-high frame.
    return HEAD.format(cap=spec.get("caption_size", 170), disp=spec.get("display_font", "Anton"),
                       mono=spec.get("mono_font", "IBM Plex Mono Medium"), cream=CREAM,
                       accent=spec.get("accent", AMBER))


def dia(a, b, style, text, layer=0):
    return f"Dialogue: {layer},{ts(a)},{ts(b)},{style},,0,0,0,,{text}\n"


# ---------------------------------------------------------------- words and captions

def load_words(spec):
    d = json.load(open(spec["words"]))
    W = [[w["start"], w["end"], w["word"].strip()] for s in d["segments"] for w in s.get("words") or []]
    for t0, t1, new in spec.get("patch", []):
        W = [w for w in W if not (t0 <= w[0] < t1)] + [list(x) for x in new]
    W.sort(key=lambda w: w[0])
    rep = {k.lower(): v for k, v in spec.get("replace", {}).items()}
    for w in W:
        m = re.match(r"^(\W*)(.*?)(\W*)$", w[2]); assert m
        if m.group(2).lower() in rep: w[2] = m.group(1) + rep[m.group(2).lower()] + m.group(3)
    return W


def timeline(spec):
    """Shots as frame ranges with their output start time (seconds, before any speed-up)."""
    out, T = [], 0.0
    for a, b, crop in spec["shots"]:
        fa, fb = fidx(a), fidx(b)
        out.append({"fa": fa, "fb": fb, "a": fa * FR, "b": fb * FR, "crop": crop, "T": T})
        T += (fb - fa) * FR
    for i, s in enumerate(out):
        s["join_prev"] = i > 0 and out[i - 1]["fb"] == s["fa"]
        s["join_next"] = i + 1 < len(out) and out[i + 1]["fa"] == s["fb"]
    return out, T


def pages(shots, W, style):
    """Caption pages in output time. A page breaks at punctuation, at a pause over 0.3 s, at
    4 words or 18 characters, and always at a cut."""
    maxw, maxch = {"word": (1, 99), "phrase": (4, 18), "highlight": (4, 18)}[style]
    P, E = [], []                          # pages, and the end of the shot each page is in
    for s in shots:
        n0 = len(P)
        ws =[(s["T"] + max(w[0], s["a"]) - s["a"], s["T"] + min(w[1], s["b"]) - s["a"], w[2])
              for w in W if s["a"] <= (w[0] + w[1]) / 2 < s["b"]]
        cur = []
        for w in ws:
            text = " ".join(x[2] for x in cur + [w])
            if cur and (w[0] - cur[-1][1] > 0.3 or len(cur) >= maxw or len(text) > maxch):
                P.append(cur); cur = []
            cur.append(w)
            if re.search(r"[.,?!;:…]$", w[2]) and style != "word": P.append(cur); cur = []
        if cur: P.append(cur)
        E += [s["T"] + s["b"] - s["a"]] * (len(P) - n0)
    out = []
    for i, p in enumerate(P):
        nxt = P[i + 1][0][0] if i + 1 < len(P) else 1e9
        # a page never outlives its shot: a caption left over after a cut reads as the
        # new speaker's words
        a = p[0][0]; b = min(max(p[-1][1] + 0.25, a + 0.45), nxt, E[i])
        out.append((a, b, p))
    return out


def caption_events(spec, pg, style, speed):
    ev = []
    accent = spec.get("accent", AMBER)
    pop = r"{\fscx86\fscy86\t(0,90,\fscx100\fscy100)}"
    pos = r"{\an8\pos(540,%d)}" % spec.get("caption_y", 250)   # top-centre, below the 12% UI band
    for a, b, p in pg:
        words = [w[2].upper() for w in p]
        if style != "highlight" or len(p) == 1:
            ev.append(dia(a / speed, b / speed, "Cap", pos + pop + " ".join(words)))
            continue
        for j, w in enumerate(p):
            s = a if j == 0 else w[0]
            e = p[j + 1][0] if j + 1 < len(p) else b
            txt = " ".join((f"{{\\c{accent}&}}{x}{{\\c{WHITE}&}}" if k == j else x) for k, x in enumerate(words))
            ev.append(dia(s / speed, e / speed, "Cap", pos + (pop if j == 0 else "") + txt))
    return ev


def srt(pg, speed, path):
    def t(x):
        ms = int(round(x / speed * 1000))
        return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"
    open(path, "w").write("".join(f"{i}\n{t(a)} --> {t(b)}\n{' '.join(w[2] for w in p)}\n\n"
                                  for i, (a, b, p) in enumerate(pg, 1)))


# ---------------------------------------------------------------- render

def render_shot(spec, s, W):
    x, y, w, h = spec["crops"][s["crop"]]
    p = f"{W}/shot-{s['fa']}-{s['fb']}-{s['crop'].replace('+', 'p')}-{int(s['join_prev'])}{int(s['join_next'])}.mov"
    if os.path.exists(p): return p
    n = s["fb"] - s["fa"]; d = n * FR; t = f"{s['a']:.6f}"
    vf = f"crop={w}:{h}:{x}:{y},scale=1080:1920:flags=lanczos"
    if spec.get("lut"): vf += f",lut3d=file={spec['lut']}"
    af = ["aformat=sample_rates=48000:channel_layouts=stereo", "apad", f"atrim=end={d:.6f}"]
    if not s["join_prev"]: af.append("afade=t=in:d=0.03")
    if not s["join_next"]: af.append(f"afade=t=out:st={d - 0.03:.6f}:d=0.03")
    run([FF, "-v", "error", "-y", "-ss", t, "-i", spec["raw"], "-ss", t, "-i", spec.get("audio", spec["raw"]),
         "-map", "0:v:0", "-map", "1:a:0", "-vf", vf + ",format=yuv420p", "-af", ",".join(af),
         "-frames:v", str(n), "-r", FPS,
         "-c:v", "libx264", "-preset", "fast", "-crf", "14", "-c:a", "pcm_s16le", p + ".tmp.mov"])
    os.replace(p + ".tmp.mov", p)
    return p


def render_endcard(spec, W, fonts):
    e = spec["endcard"]; d = e.get("dur", 2.8); p = f"{W}/endcard.mov"
    if os.path.exists(p): return p
    open(f"{W}/endcard.ass", "w").write(head(spec) + "".join([
        dia(0.35, d, "Cta", r"{\an5\pos(540,1350)\fad(250,0)}" + e.get("cta", "SUBSCRIBE")),
        dia(0.55, d, "Url", r"{\an5\pos(540,1490)\fad(250,0)}" + e.get("url", "")),
    ]))
    # a small bell, struck at 0.3 s as the logo lands: E6 plus two decaying partials
    k = "(t-0.3)"
    bell = (f"if(gte(t,0.3),0.30*sin(2*PI*1318.5*{k})*exp(-3.5*{k})+0.14*sin(2*PI*2637*{k})*exp(-5*{k})"
            f"+0.05*sin(2*PI*3638*{k})*exp(-8*{k}),0)")
    run([FF, "-v", "error", "-y", "-f", "lavfi", "-i", f"color=c=black:s=1080x1920:r={FPS}:d={d}",
         "-loop", "1", "-framerate", FPS, "-i", e["logo"],
         "-f", "lavfi", "-i", f"aevalsrc=exprs='{bell}|{bell}':s=48000:d={d}",
         "-filter_complex",
         f"[1:v]scale=760:760:force_original_aspect_ratio=decrease,format=rgba,fade=t=in:st=0:d=0.35:alpha=1[lg];"
         f"[0:v][lg]overlay=(W-w)/2:430:shortest=1,ass={W}/endcard.ass:fontsdir={fonts},format=yuv420p[v];"
         f"[2:a]afade=t=out:st={d - 0.4}:d=0.4[a]",
         "-map", "[v]", "-map", "[a]", "-t", str(d), "-r", FPS,
         "-c:v", "libx264", "-preset", "fast", "-crf", "14", "-c:a", "pcm_s16le", p])
    return p


def loudness(path):
    out = run([FF, "-nostats", "-i", path, "-af", "ebur128", "-f", "null", "-"], capture=True)
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", out)[-1])


def main():
    global FPS, FR
    spec = json.load(open(sys.argv[1]))
    FPS = spec.get("fps", FPS); num, den = (int(x) for x in FPS.split("/")); FR = den / num
    slug = spec["slug"]
    W = spec.get("workdir", f"shorts-work/{slug}"); os.makedirs(W, exist_ok=True)
    out_dir = spec.get("out_dir", "."); os.makedirs(out_dir, exist_ok=True)
    fonts = spec.get("fonts") or os.environ.get("SHORT_FONTS")
    if not fonts: sys.exit("set 'fonts' in the spec (a folder with Anton.ttf and IBMPlexMono-Medium.ttf)")
    shots, total = timeline(spec)
    print(f"{slug}: {len(shots)} shots, {total:.2f} s before speed-up")
    pieces = []
    for i, s in enumerate(shots):
        pieces.append(render_shot(spec, s, W)); print(f"  shot {i + 1}/{len(shots)}", flush=True)
    open(f"{W}/concat.txt", "w").write("".join(f"file '{os.path.abspath(p)}'\n" for p in pieces))
    base = f"{W}/base.mov"
    run([FF, "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{W}/concat.txt", "-c", "copy", base])
    gain = spec.get("lufs", -14.0) - loudness(base)
    card = render_endcard(spec, W, fonts)
    words = load_words(spec)
    for name in sys.argv[2:] or list(spec["variants"]):
        v = spec["variants"][name]; sp = v.get("speed", 1.0); style = v.get("captions", "highlight")
        pg = pages(shots, words, style)
        ev = caption_events(spec, pg, style, sp)
        lt = spec.get("lower_third")
        if lt:
            # y is the name's bottom edge. The default sits just above the bottom UI band
            # (y 1574); when the face sits low, move the card above the head (e.g. y 520).
            a, b = lt["at"] / sp, (lt["at"] + lt["dur"]) / sp; y = lt.get("y", 1488)
            ev += [dia(a, b, "Lower", r"{\an1\pos(56,%d)\fad(250,250)}" % y + lt["name"], 1),
                   dia(a + 0.15, b, "LowerSub", r"{\an1\pos(58,%d)\fad(250,250)}" % (y + 74) + lt["sub"], 1)]
        ass = f"{W}/{name}.ass"; open(ass, "w").write(head(spec) + "".join(ev))
        srt(pg, sp, f"{W}/{name}.srt")
        L = total / sp; fade = spec.get("fade", 0.6)
        out = f"{out_dir}/{slug}-{name}.mp4"
        run([FF, "-v", "error", "-y", "-i", base, "-i", card, "-filter_complex",
             f"[0:v]setpts=PTS/{sp},fps={FPS},ass={ass}:fontsdir={fonts},"
             f"fade=t=out:st={L - fade:.3f}:d={fade}[v0];"
             f"[0:a]atempo={sp},volume={gain:.2f}dB,alimiter=limit=0.79:level=disabled,"
             f"afade=t=out:st={L - fade:.3f}:d={fade}[a0];"
             f"[1:v]fps={FPS},format=yuv420p[v1];[1:a]aformat=sample_rates=48000:channel_layouts=stereo[a1];"
             f"[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a]",
             "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
             "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", out])
        print(f"  {name}: {L + spec['endcard'].get('dur', 2.8):.1f} s, gain {gain:+.1f} dB -> {out}")


if __name__ == "__main__":
    main()
