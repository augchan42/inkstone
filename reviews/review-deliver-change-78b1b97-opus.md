# Review: inkstone c3f5070..78b1b97 (deliver-change visual critics)

## Scope

- **Diff command:** `git diff c3f5070d34598387940ecce29eaa1a9f73ea9f49..78b1b97899ca0492a96a163d97eb5bbf812a47df`
- **Range:** c3f5070..78b1b97. Seven files changed, 190 lines.
- **Changed files:** `.claude-plugin/plugin.json`, `AGENTS.md`, `README.md`, `docs/adr/0001-separate-verification-from-adversarial-review.md`, `skills/critic-loop/SKILL.md`, `skills/critic-loop/references/claude-code.md` (new), `skills/deliver-change/SKILL.md`
- **Direct references read:** `skills/codex-review/reviewer-backends.md`, `skills/critic-loop/critic-prompt.md`

## Reviewer identity

- **Backend:** Claude Agent SDK (Claude Code), working directly in this session. No Codex, opencode, subagent or other reviewer was run.
- **Model:** `claude-opus-5-5` (Opus 5.5).
- **Independence:** This is the same model family as the Claude critic this diff configures. I don't know which model wrote the change, so I make no cross-model claim.

## Findings

### 1. The Claude critic is not actually limited to its packet, so the blind read can be broken — **Medium-High** · Security / Contracts

**Where:** `skills/critic-loop/references/claude-code.md:19-23`, `:31-33`, `:57`

**What's wrong:**
- The reference says `--restricted`, the tool list and the empty MCP config "limit the critic to reading/searching the packet".
- But the script passes unscoped `--allowedTools "Read,Glob,Grep"`. Those rules pre-approve the three tools for **any** path.
- Claude Code's read-only tools are also not limited to the working directory by default.
- So the only path boundary is `--restricted`, a flag nothing in this change shows does path confinement. The doc only asks the user to check `--help`.
- As written, the critic can read or search outside the packet by absolute path. That includes:
  - the target repo's `reviews/critic/<id>/rubric.md`, which holds the brief;
  - the other critic's round output;
  - producer notes;
  - unrelated private files such as credentials.

**Why it matters:**
- The blind read is the main thing critic-loop protects (SKILL.md:16-18, 234-235). Line 32 of the reference even requires that "Part A must not be able to read part B's brief". Nothing enforces that.
- The critic's text is saved into the repo's `reviews/`. A prompt-injected image or rubric could get a sensitive file read and its contents written into a committed review record.

**Fix:**
- Remove the blanket `--allowedTools`, or scope it to the packet (for example `Read(./**)`, `Glob(./**)`, `Grep(./**)`).
- Make the script itself audit the stream: collect every `tool_use` input path (`file_path`, `path`, `pattern` roots) and compare its `realpath` to the packet's `realpath`.
- Treat any access outside the packet as invalidating that phase.
- Change the prose so it no longer claims the flags alone confine the critic.

### 2. The dispatch script saves a "successful" result before the checks that make it valid — **Medium** · Correctness

**Where:** `skills/critic-loop/references/claude-code.md:67-74` versus `:77-83`

**What's wrong:**
- The prose requires four things before the result counts:
  - the actual model was recorded and is Opus 5.5 or later (not just the alias that was passed in);
  - the provider/auth route was recorded;
  - successful `Read` calls opened every assigned image;
  - otherwise the review is incomplete.
- The script checks only the exit code and that there is exactly one successful `result` event. It then writes `result_file` with exclusive create (`"x"`).
- It never checks the init or assistant events' `model`, the auth route, or the `Read` tool results.

**Why it matters:**
- critic-loop accepts a round file once it "exists, is non-empty and names the critic" (SKILL.md:155-156).
- A non-empty `result_file` now exists even for a critic that never opened the images, or that ran on an older model through an alias.
- Because of the `"x"` mode, the slot is also used up. A later "incomplete" decision has to deal with a leftover artifact that looks valid.
- This is easy to miss because the script is presented as the reference implementation.

**Fix:**
- Inside the script, before opening `result_file`:
  - pull the model from the `system`/`init` event and assistant `message.model`, and fail unless it matches the requested family/version;
  - collect the `Read` `tool_use` IDs whose `file_path` resolves to each assigned image and whose matching `tool_result` is not an error, and fail if any image is missing;
  - add the path audit from finding 1.
- Write `result_file` only after every check passes. Also write the extracted model and auth source next to it so the caller can record them.

### 3. The Codex Astra critic's two stages, and the two critics, all target `$ROUND_FILE` — **Medium** · Contracts

**Where:** `skills/critic-loop/SKILL.md:88-89`, `:121-122`, `:152-153`

**What's wrong:**
- The new line 89 tells the Astra critic to use "a fresh call for each blind-read and scored-verdict stage", reusing the line-88 command `--output-last-message "$ROUND_FILE"`.
- So part B overwrites part A's blind read in the same file. Part B also needs that blind read as input (critic-prompt.md:3-6).
- Writing Codex's raw final message to `round-<n>.md` also overwrites the round record. In two-critic mode, which deliver-change now always uses, that record has to hold each critic's scores separately, then the combined result and dispositions (SKILL.md:152-153, 160-162).
- It also breaks the shared contract that each output path is fresh and not yet existing (reviewer-backends.md:36-38).
- The new Claude reference gets this right with separate per-phase paths (claude-code.md:35-36). The Codex route doesn't.

**Fix:**
- In line 89, require separate fresh, caller-owned output paths for each critic and phase (for example `round-<n>.codex.blind.md` and `round-<n>.codex.verdict.md`).
- Have the host assemble `round-<n>.md` from those files.

### 4. Standalone install guidance leaves out a file the new visual route needs — **Low-Medium** · Contracts

**Where:** `README.md:117-119`, `skills/deliver-change/SKILL.md:29-31`

**What's wrong:**
- The new README text says to install `codex-review` only "for the optional code-review stage", and deliver-change reads `codex-review` "only when opted in".
- But the new Claude route requires "the shared backend supervisor" and "the shared backend source-integrity checks" (claude-code.md:77, 85). critic-loop Phase 2 also resolves its defaults from `../codex-review/reviewer-backends.md`.

**Why it matters:**
- A standalone install that follows the README has `critic-loop` but not `reviewer-backends.md`.
- The visual stage then can't follow its own supervision and integrity rules. It either silently skips them or stalls.

**Fix:**
- State that substantial visual work also needs `codex-review/reviewer-backends.md`, or the whole `codex-review` skill.
- Or move the shared backend mechanics into a location both skills ship with.

### 5. In rounds 2+, each critic sees the other critic's verdict — **Low** · Contracts

**Where:** `skills/critic-loop/SKILL.md:105-106` versus `:121-122` and `skills/critic-loop/references/claude-code.md:31-32`

**What's wrong:**
- From round 2, the packet includes "the previous round's artifact and verdict".
- In two-critic mode, that verdict is the round file, which contains both critics' scores and the combined result.
- The new text says to keep "the other critic's verdict out of both packets" and to keep the critics independent (deliver-change SKILL.md:93-94).
- The two rules conflict from round 2 onward, so each critic's later rounds are anchored by the other's earlier scores.

**Fix:** Say that, in two-critic mode, the round 2+ packet carries only that critic's own previous verdict plus the one-line change list. Optionally add the combined pass/fail, but not the other critic's scores or reasons.

### 6. The Claude critic's prompt isn't told to read the image paths — **Low** · Correctness

**Where:** `skills/critic-loop/references/claude-code.md:29-33`, `skills/critic-loop/critic-prompt.md:14`

**What's wrong:**
- Part A says "Look at the attached [image(s)]". The Claude CLI route attaches nothing; images are only reachable through `Read`.
- The Claude reference doesn't say to list the neutral image paths in the prompt and tell the critic to open them, as the subagent route does (SKILL.md:92).
- Combined with finding 2, a critic that answers without reading the images produces a result that the script accepts.

**Fix:** In the Claude reference, require the prompt to list each packet-relative image path and tell the critic to open every one with `Read` before answering.

### 7. The prompt is passed as a command-line argument — **Low** · Security

**Where:** `skills/critic-loop/references/claude-code.md:55`

**What's wrong:**
- The prompt text goes into argv via `"claude", "-p", Path(prompt_file).read_text()`.
- Anyone on the machine who can run `ps` while the job runs can see the part B brief, rubric and references.
- Large prompts can also hit the per-argument size limit (`MAX_ARG_STRLEN` is about 128 KiB on Linux) and fail with E2BIG.

**Fix:**
- Send the prompt on stdin instead: `subprocess.run(..., input=prompt_text, text=True)`, dropping `stdin=DEVNULL`. stdin still reaches EOF, so the `< /dev/null` deadlock concern doesn't apply.
- Or confirm that `claude -p` with no prompt argument reads stdin in the pinned version.

### 8. The model pair is written out in five places — **Advisory** · Simplification

**Where:** `AGENTS.md:70`, `README.md:59`, `README.md:102-106`, `docs/adr/0001-…md:52-55`, `skills/critic-loop/SKILL.md:82-83`, `skills/deliver-change/SKILL.md:83-85`

- The literal pair (`claude-opus-5-5` / `gpt-6-astra` / `ultra`) appears in all of these.
- critic-loop also now names a specific caller's choice (`deliver-change selects…`), which ties the generic skill to one caller.
- Suggestion: keep the pair defined only in deliver-change. critic-loop can just say "honor a caller-selected route", and the other docs can link to deliver-change.

## Verification limitations

- I couldn't confirm that Claude Code 2.1.312 supports `--safe-mode`, `--restricted`, `--effort`, `--tools` or `dontAsk`, or what they do. In particular I couldn't check whether `--restricted` limits file access to the working directory. If it does, finding 1 drops to "unverified claim plus missing audit".
- I couldn't confirm that `gpt-6-astra` and `model_reasoning_effort="ultra"` are valid for the installed Codex CLI.
- I ran nothing: no CLI, no Python snippet, no tests, no linters. The new Python dispatch has no test or fixture. A recorded stream-json sample would let the parsing and validation logic in findings 1, 2 and 6 be tested.
- Not in the packet, so not checked: marketplace/manifest files beyond `plugin.json`, `agents/`, `rubrics.md`, `scripts/`, and any repo version policy for per-skill `metadata.version` (critic-loop stays at 1.1.0 despite the behaviour change).
- I made no edits, staged nothing and committed nothing.

## Verdict

**Needs revision.** Findings 1–3 should be fixed before the two-critic visual stage becomes the default in deliver-change:
1. The Claude critic isn't confined to its packet, so the blind read isn't protected.
2. The reference script saves a result before the model-identity and image-read checks it depends on.
3. The Codex stages and critics overwrite each other's output and the round record.


## Host execution record

Actual backend: Claude Code CLI 2.1.312, model `claude-opus-5-5`, firstParty provider. The model’s self-description above does not replace CLI metadata. Review exit 0; the final stream event was successful. The reviewed source remained unchanged.

## Disposition

- Finding 1 — DECLINED as an unconfined-read defect: the installed CLI help explicitly documents restricted file confinement, and an actual outside-packet Read was denied with `is_error: true`. Added a boundary recheck and access-audit requirement for changed versions/permissions.
- Finding 2 — ACCEPTED: removed the premature result-writing example. The command now captures raw events only; identity, provider, tools, image reads, packet access and source integrity must pass before a verdict file is created.
- Finding 3 — ACCEPTED: fresh per-critic/per-phase/per-round outputs; the host assembles the combined round record.
- Finding 4 — ACCEPTED: the standalone route explicitly requires the shared reviewer-backends reference even without code-review opt-in.
- Finding 5 — ACCEPTED: later-round packets carry only the same critic’s earlier verdict; no other critic or combined scores.
- Finding 6 — ACCEPTED: each prompt must list every neutral image path and request Read of each.
- Finding 7 — ACCEPTED: prompts go through stdin; the actual stdin image/denial/scored checks completed successfully.
- Finding 8 — DECLINED as a blanket removal of user-facing defaults: README and AGENTS inventory must explain the workflow. Removed the caller-specific default pair from the generic critic-loop entrypoint to avoid a second operational definition.

Accepted repairs are in `e46ca49`. A focused review of that increment is recorded separately.
