# Focused review: inkstone 78b1b97..e46ca49 (repairs after the visual-critic review)

## Scope / diff

- **Diff:** `git diff 78b1b97899ca0492a96a163d97eb5bbf812a47df..e46ca490e322c20104d4916f9ee7c0f1e0cf0208`, read from `diff.patch`. The packet is not a git repository, so I did not regenerate the diff.
- **Changed files (4):** `README.md`, `skills/critic-loop/SKILL.md`, `skills/critic-loop/references/claude-code.md`, `skills/deliver-change/SKILL.md`.
- **Direct references read:** `skills/codex-review/reviewer-backends.md`, `skills/critic-loop/critic-prompt.md`, `claude-help.txt`, `previous-opus.md`. I did not read `previous-astra.md`.

## Reviewer identity

- **Backend:** Claude Agent SDK (Claude Code), reviewing directly in this session. I ran no CLI, subagent or external service.
- **Model:** `claude-opus-5-5` (Opus 5.5). This is self-reported; the host's metadata is the authoritative record. It is the same model family as the Claude critic this change configures.

## Previous findings: are they closed?

| # | Previous finding | Status | Evidence |
|---|---|---|---|
| 1 | Claude critic not confined to the packet | **Closed. I accept the decline.** | The supplied help text says `--restricted` "confines the file tools to the working directories (--add-dir included)" (`claude-help.txt:203-205`). `claude-code.md:17-22` now records the boundary test, requires a recheck when the CLI changes, and adds a post-run audit of every tool access (`:81-82`). |
| 2 | Result saved before validity checks | **Closed** | The Python writer is gone. The command only captures raw events (`claude-code.md:73`). A verdict and metadata are written only after every check in `:76-85` passes, and failed runs do not fill an accepted path (`:87-89`). |
| 3 | Codex stages and the two critics overwrite `$ROUND_FILE` | **Closed** | `$CRITIC_PHASE_FILE` (`critic-loop/SKILL.md:86`). Fresh output paths for each critic, phase and round, and the host builds `round-<n>.md` (`:98-101`). |
| 4 | Standalone install omits `reviewer-backends.md` | **Closed** (see the Advisory note on path layout) | `README.md:117-120`, `deliver-change/SKILL.md:32-33`, `claude-code.md:4-7`. |
| 5 | Round 2+ critics see each other's verdicts | **Closed** | `critic-loop/SKILL.md:109-111`, `claude-code.md:41-42`. |
| 6 | Prompt doesn't tell the critic to Read the images | **Closed** | `claude-code.md:36-37`. A Read result containing image content is now also required for every image (`:83-84`). |
| 7 | Prompt passed in argv | **Closed** | stdin redirect `< "$PROMPT_FILE"` (`claude-code.md:69`). |
| 8 | Model pair written in many places | **Partially addressed, acceptable** | The `deliver-change selects…` sentence is removed from critic-loop. One leftover reference, see Advisory below. |

## Findings

### 1. The Claude command lost its timeout and doesn't fit the shared supervisor template — **Low** · Execution

**Where:** `skills/critic-loop/references/claude-code.md:60-73`, compared with `skills/codex-review/reviewer-backends.md:271-307`

**The timeout:**
- The removed Python dispatch had a hard `timeout=900`.
- The new text hands liveness and timeout to "the shared backend supervisor" (`:72-73`).
- `reviewer-backends.md` only defines liveness probes and hard caps for Codex (rollout directory) and opencode (log growth). It gives none for Claude.
- So a hung Claude critic now has no defined probe or cap in the documents.

**The template:**
- The supervisor template is meant to be reused by "replacing only the reviewer command" (`reviewer-backends.md:284`). It appends `> "$OUT" 2>&1 < /dev/null`.
- If you drop the Claude command in literally, those trailing redirections override `< "$PROMPT_FILE"` and the stream/error redirections. The prompt is lost and stdout goes to `$OUT`.
- The run probably fails loudly (`-p` gets no input) rather than silently. But the documented composition is wrong.

**Fix:**
- Say that the Claude command replaces the whole redirected line in the supervisor, not just the reviewer command.
- Define a Claude liveness signal, for example `$STREAM_FILE` growing within about 90 seconds and no 5-minute stall, plus the same ~15-minute hard cap.

### Advisory (optional, non-blocking)

- **Leftover Astra reference:** `critic-loop/SKILL.md:87` still says "For the selected Astra critic…". The sentence that introduced that critic (old lines 82-83) was removed, so nothing in critic-loop now says what it is. Rewording it as "when a caller selects `gpt-6-astra`…" would keep the recipe without naming a caller.
- **Install path:** `README.md:118-119` says to install "`critic-loop` and its references, including `codex-review/reviewer-backends.md`". The links resolve as `../codex-review/` and `../../codex-review/`, so the file must sit in a sibling `codex-review/` directory, not inside critic-loop. Saying so would avoid a broken link in a standalone install.
- **Managed-settings check:** `claude-code.md:27-29` asks you to inspect managed settings for hooks, tools, credential helpers and provider overrides. It doesn't mention managed `additionalDirectories` or permission allow rules, which would widen what `--restricted` treats as working directories. The post-run audit (`:81-82`) would still invalidate an outside access, so this fails safe. Checking before dispatch just avoids wasted runs.
- **Text order:** `claude-code.md:50` ends with a colon that introduces the command, but the auth-preflight paragraph (`:52-58`) sits between it and the code block. Moving the preflight paragraph up would fix the flow.

## Verification limits

- **Nothing executed:** I ran no `claude`, `codex`, shell or test commands. I could not check:
  - the field names and acceptance of `claude auth status` with isolation flags (`loggedIn`, `authMethod`, `apiProvider`, `subscriptionType`);
  - whether stream-json init/usage events expose the provider, and whether image Read results carry image content blocks;
  - the env selectors `CLAUDE_CODE_USE_ANTHROPIC_AWS`, `CLAUDE_CODE_USE_ANTHROPIC_GOOGLE_CLOUD` and `CLAUDE_CODE_USE_MANTLE`.
- **Accepted on the author's word:** The disposition says the outside-Read denial and the stdin checks were tested. I relied on that and on the supplied help text, without reproducing them.
- **Codex route, outside this increment:** These are noted only and don't affect the verdict:
  - `codex --sandbox read-only` does not limit reads to a packet;
  - the Codex prompt, including part B's brief, is still passed in argv;
  - the Codex route has no actual-model acceptance gate like the Claude one.

  I didn't raise these last round and the increment didn't change them, apart from the output-path variable.
- **Not checked:** `.claude-plugin/plugin.json` and any version policy. critic-loop went from 1.1.0 to 1.2.0; I did not check whether the plugin version should also change.
- I made no edits.

## Verdict

**Ready.** Previous findings 2–7 are fixed. I accept the decline of finding 1: the supplied CLI help confirms `--restricted` confines file access, and the new audit backs it up. Finding 8 is mostly addressed. The one new Low finding (no timeout and a template mismatch for the Claude route) fails loudly rather than silently, so it doesn't block this. It's worth fixing in a follow-up along with the advisory notes.


## Host execution record

Actual backend: Claude Code CLI 2.1.312, `claude-opus-5-5`, firstParty provider. Process exited 0 and returned the saved final review above. Host metadata is authoritative where the model could not identify its exact runtime. The reviewed implementation state was `e46ca490e322c20104d4916f9ee7c0f1e0cf0208`.

## Disposition

- Low finding — ACCEPTED, fixed in `19d53e1`: specify replacing the whole redirected supervisor line, preserving prompt stdin, with explicit 90-second startup progress, five-minute stall and 15-minute phase limits.
- Advisory Astra wording — ACCEPTED: conditional now refers to a caller selecting Astra.
- Advisory sibling directory — ACCEPTED: standalone instructions specify the sibling codex-review directory.
- Advisory managed directory/permission rules — ACCEPTED: included in preflight inspection.
- Advisory text order — ACCEPTED: preflight now precedes the command introduction.

These final documentation clarifications were checked directly and did not receive another independent review. The final preflight ordering was executed successfully, and the literal command was exercised with synthetic provider selectors.
