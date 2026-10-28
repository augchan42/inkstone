# Claude Code CLI visual critic

Use this route when selected by the user, project or calling workflow. It does
not change the default backend order for code or plan reviews.

## Model, account and tools

Use `claude-opus-5-5` or a later available Opus model through the existing
Claude subscription. Record the exact model returned by the run. A moving
alias alone does not prove that the requested model ran. Confirm the CLI,
model and subscription login are available; if they are not, leave this
selected review incomplete. Do not obtain API credentials, use OpenRouter,
switch providers or introduce new paid services to complete the review.

Check the installed `claude --help` before using these flags. The example was
checked against Claude Code 2.1.312. If that installation lacks the controls
needed to keep the critic isolated and read-only, report the limitation.

Run from a fresh packet directory containing only the assigned images and
inputs for the current phase. `--safe-mode` disables project instructions,
skills, hooks and other customizations; `--restricted`, the explicit tool
list and empty strict MCP configuration limit the critic to reading/searching
the packet. Do not use `--bare`: it skips the subscription/keychain auth route.
Do not use permission bypass flags. Verify that managed settings do not
enable extra tools or change the provider. Do not print credentials.

## Dispatch and evidence

Use `critic-prompt.md`: run part A with only the artifact and viewing conditions;
then part B in another fresh process with the same images, that critic's fixed
blind read, and the rubric/brief/references. Keep producer notes and the other
critic's verdict out of both packets. Part A must not be able to read part B's
brief from its working directory. Use neutral image names during the blind read.

The caller creates separate, fresh absolute paths for the prompt, stream log,
stderr and final Markdown outside the read-only packet. Pass those paths as
script arguments; keep input text out of shell interpolation. This illustrative
Python dispatch captures one phase without giving the reviewer write tools:

```python
import json
import os
from pathlib import Path
import subprocess
import sys

packet, prompt_file, stream_file, error_file, result_file, model = sys.argv[1:]
env = os.environ.copy()
for key in (
    "ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_BASE_URL",
    "CLAUDE_CODE_USE_BEDROCK", "CLAUDE_CODE_USE_VERTEX", "CLAUDE_CODE_USE_FOUNDRY",
):
    env.pop(key, None)  # retain the existing subscription login
command = [
    "claude", "-p", Path(prompt_file).read_text(), "--model", model,
    "--effort", "high", "--safe-mode", "--restricted",
    "--tools", "Read,Glob,Grep", "--allowedTools", "Read,Glob,Grep",
    "--permission-mode", "dontAsk", "--strict-mcp-config",
    "--mcp-config", '{"mcpServers":{}}', "--no-session-persistence",
    "--output-format", "stream-json", "--verbose",
]
with open(stream_file, "x") as output, open(error_file, "x") as errors:
    completed = subprocess.run(
        command, cwd=packet, env=env, stdin=subprocess.DEVNULL,
        stdout=output, stderr=errors, timeout=900,
    )
completed.check_returncode()
events = [json.loads(line) for line in Path(stream_file).read_text().splitlines()]
results = [event for event in events if event.get("type") == "result"]
if (len(results) != 1 or results[0].get("subtype") != "success"
        or results[0].get("is_error") or not results[0].get("result", "").strip()):
    raise RuntimeError("Claude critic did not return a successful final result")
with open(result_file, "x") as result:
    result.write(results[0]["result"] + "\n")
```

Run this under the shared backend supervisor so progress is observable and
timeouts are handled; use distinct logs for the two phases. The caller parses
the JSON stream, requires a successful final result, and saves its text to the
fresh `result_file`. A process exit code alone is insufficient. Record the
actual model and provider/auth route, and verify that successful `Read` calls
opened every assigned image. If those events or identity evidence are missing,
the visual review is incomplete. Never manufacture a verdict from log fragments.

Apply the shared backend source-integrity checks before and after dispatch.
The host saves the result; the critic never writes reports or repairs assets.
`costUSD` in CLI metadata is not proof of a separately billed API call.
