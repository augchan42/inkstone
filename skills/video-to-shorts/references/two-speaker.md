# Two speakers, one camera

Most podcast footage is one static wide shot of two people. A 9:16 crop holds one face at a
time. The short is built from two (or more) crops of the same frame, and it cuts between
them the way a multi-camera edit would. This file covers how to decide **who is speaking
when** and how to frame each person.

## Framing

- Crop width = source height x 9/16, rounded to an even number (1216 on 4K, 608 on 1080p).
- Give each person a base crop, e.g. `C` and `A`. Also give each a punch-in about 1.2x
  tighter, e.g. `C+` = 1012x1800 on 4K. Anchor the punch-in to the bottom of the base crop
  (y = 2160 - 1800 = 360) so the face gets bigger without moving up out of frame. Keep
  every number even.
- Test each crop at 4-6 times across the clip, in one frame strip (`hstack` of crops with
  white `pad` separators). People lean. A crop that is right at one moment can cut off a
  head ten seconds later. Move the offset until every sample works.
- Never guess the offset. Show the strip and let the owner pick.

## Who is speaking: use the mic channels, not the picture

A frame shows who is on screen, not who is talking. Sampled stills land in pauses and prove
nothing. Take attribution from the audio.

**Two lavalier mics recorded to L and R** (the usual two-mic podcast kit): each speaker is
2-7 dB louder on their own channel. Measure it:

```python
# per word (start, end from the word-timestamp JSON), on the UN-normalised stereo master
l = 10*log10(mean(L**2)+1); r = 10*log10(mean(R**2)+1)
who = "L-speaker" if l - r > 1.5 else "R-speaker" if r - l > 1.5 else "?"
```

Calibrate the sign and the size on a known monologue first. On our rig the difference was
+4 to +7 dB for the left speaker and -2.5 to -5 dB for the right speaker. A `?` means
overlap, a laugh or a very short word. For those, check 100 ms windows:

```
1246.5 L 67.2 R 60.9 +6.2 C   <- a word from C that the transcript does not have
1247.5 L 65.6 R 69.1 -3.5 A
```

Keep the **un-normalised** master for this. A mono or summed delivery master has lost the
difference.

## Recover words the transcript missed or misplaced

Whisper on a mixed track merges an overlap into one speaker or drops a short reply.
Transcribe each channel on its own over the few seconds in question:

```bash
ffmpeg -ss T -t 5 -i master.mp4 -af "pan=mono|c0=c0" -ar 16000 snipL.wav   # c1 for R
```

Then run faster-whisper with `word_timestamps=True` on each file. The result from 2026-09-15:
- The mixed transcript had "What part of France are you from? … Normandy." as one block.
- The per-channel pass showed the guest answering "Normandy" at 1246.6 s.
- The host repeated "Normandy" at 1247.4 s, as the lead-in to the joke.

Two speakers and two shots, where the mixed transcript had one. Put the corrected words
into the edit list as a patch, so the captions use them.

If faster-whisper on CUDA fails with `libcublas.so.12 not found`, run it with
`device="cpu", compute_type="int8"` for a clip this short.

## Cut plan

1. List the words with start, end and speaker label for the whole moment.
2. Put a cut in the gap before each change of speaker, including one-word interjections.
3. Add reaction shots and punch-ins (see `retention-edit.md`), and trim the long pauses.
4. Write the plan as an edit list: shots in output order, each a source in/out plus a crop
   name. Shots that continue each other in the source join without a fade. Every other
   join gets 30 ms audio fades.

The audio always follows the source continuously inside a run of shots. Changing the crop
never touches the sound.
