# Claude Code CLI visual critic

Use this route when selected by the user, project or calling workflow. It does
not change the default backend order for code or plan reviews. Read the
[shared backend reference](../../codex-review/reviewer-backends.md) for
supervision and source-integrity checks;
this reference is required even without the adversarial code-review stage.

## Model, account and tools

Use `claude-opus-5-5` or a later available Opus model through the existing
Claude subscription. Confirm the CLI, requested model and subscription login
are available. Record the actual resolved model; an alias alone is not evidence.
An unavailable selected route leaves review incomplete. Do not obtain API
credentials, use OpenRouter, switch providers or introduce new paid services.

Check the installed `claude --help` before using the flags below. They were
checked against Claude Code 2.1.312. In that version, `--restricted` confines
file tools to working directories, including with Read/Glob/Grep pre-approved;
an actual out-of-packet Read test was denied. Recheck the boundary with a
synthetic outside file when the CLI or permissions change. If the installation
cannot keep the critic isolated and read-only, report the route unavailable.

Run from a fresh packet directory containing only the assigned images and
current phase's inputs. Reject symlinks escaping the packet. `--safe-mode`
disables ordinary customizations; managed policy, including managed hooks,
still applies. Before dispatch, inspect effective managed settings for hooks,
extra tools, credential helpers, additional working directories, permission
allow rules or provider overrides. If they break this
contract or their effective state cannot be verified, leave the route unavailable.
`--restricted`, the explicit tools and empty strict MCP configuration limit
file/tool access; they do not disable managed hooks.
Do not use `--bare`, which skips subscription/keychain auth, or permission bypass.

## Separate phases and outputs

Use `critic-prompt.md`. List every neutral packet-relative image path in each
prompt and tell the critic to open all of them with Read before answering.
Part A receives only artifacts and viewing conditions. Part B is a fresh
process with the same images, that critic's fixed blind read, and the
rubric/brief/references. Part A's packet cannot contain part B's brief, even
as another file. Keep producer notes and the other critic's verdict out.
For later rounds, include only this critic's own earlier verdict.

Use a fresh prompt, stream log, stderr path and eventual Markdown result for
each critic/phase/round. Keep caller-owned logs and outputs outside the packet.
The host assembles the combined round record; no CLI writes directly over it.

Before inference, run `claude auth status` with the exact sanitized environment
and isolation flags intended for the review. Require `loggedIn: true`,
`authMethod: claude.ai` and `apiProvider: firstParty`; record `subscriptionType`
without credentials. If this preflight fails, do not send the review packet.
The cleanup below covers provider selectors recognized by the checked CLI;
recheck newly supported selectors when changing versions. Post-run metadata
is a consistency check, not a substitute for this preflight.

With the checked CLI, order the flags as `claude --strict-mcp-config
--mcp-config '{"mcpServers":{}}' --safe-mode --restricted auth status`.
The flag after the variadic `--mcp-config` prevents it consuming `auth status`.

The caller runs the command below with recorded absolute paths and a verified
model. Pass the prompt through stdin so it reaches EOF without exposing the
brief in process arguments. Clear API/provider overrides and preserve login:

```sh
env -u ANTHROPIC_API_KEY -u ANTHROPIC_AUTH_TOKEN -u ANTHROPIC_BASE_URL \
  -u CLAUDE_CODE_USE_BEDROCK -u CLAUDE_CODE_USE_VERTEX -u CLAUDE_CODE_USE_FOUNDRY \
  -u CLAUDE_CODE_USE_ANTHROPIC_AWS -u CLAUDE_CODE_USE_ANTHROPIC_GOOGLE_CLOUD \
  -u CLAUDE_CODE_USE_MANTLE \
  claude -p --model "$MODEL" --effort high --safe-mode --restricted \
  --tools "Read,Glob,Grep" --allowedTools "Read,Glob,Grep" \
  --permission-mode dontAsk --strict-mcp-config --mcp-config '{"mcpServers":{}}' \
  --no-session-persistence --output-format stream-json --verbose \
  < "$PROMPT_FILE" > "$STREAM_FILE" 2> "$ERROR_FILE"
```

In the shared backend supervisor, replace the entire redirected reviewer line
with this command. Preserve its prompt/stream/error redirections; do not append
the template's `< /dev/null` or output redirections. Record fresh PID and exit
files. Require stream/error progress within 90 seconds, treat a five-minute
stall as a hang, and cap each phase at 15 minutes. Terminate only the recorded
reviewer PID on timeout and preserve its logs. This command captures raw events only.
Before creating a verdict artifact, the caller must verify all of these:

- Successful process exit and one successful, non-error final result with text.
- Init and model-usage metadata identify the requested eligible Opus model
  and first-party provider, consistent with the subscription auth preflight. Model/provider
  substitution or unverifiable identity leaves the selected review incomplete.
- Available tools are only Read/Glob/Grep and no extra MCP tools were loaded.
- Every tool access resolves inside the canonical packet path. Audit Read file
  paths and Glob/Grep search roots; an outside access attempt invalidates the phase.
- For every assigned image, a Read tool-use ID has a matching successful
  tool-result containing image content. A plausible text answer alone is insufficient.
- Source-integrity checks still match the recorded inputs.

Only then save the final text and tool/model/provider identity to fresh result
and metadata paths. Failed/incomplete runs retain diagnostic logs separately;
they do not populate an accepted verdict path. CLI `costUSD` list-price metadata
is not proof of a separately billed API call.
