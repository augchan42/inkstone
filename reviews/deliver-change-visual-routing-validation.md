# Deliver-change visual routing validation

Date: 28 October 2026. Release: 1.26.0.

## Scope and identities

Baseline: `c3f5070d34598387940ecce29eaa1a9f73ea9f49`.
Initial implementation reviewed: `78b1b97899ca0492a96a163d97eb5bbf812a47df`.
Review repairs: `e46ca49` (focused follow-up review recorded separately).
The seven implementation files were reviewed separately from this evidence
record and the reviewer reports. Publication through GitHub may create a
different commit identity; source blob identities must match the tested files.

## Behavioral routing exercise

Two separate fresh-context agents applied the original and updated skills to
the same eight requests. Neither received expected answers, the other agent's
results, or the producer's reasoning. They chose concrete next actions and
handoff claims; they did not run the hypothetical product work or its critics.

| Request/state | Baseline behavior | Updated behavior |
| --- | --- | --- |
| Three mech concepts; exports pass; renders ready; checkpoint due today | No required critic; proceed to handoff | Two independent visual critics before visual readiness |
| Backend invoice retry fix; reproducer and tests pass | Verification only | Verification only; no visual gate or unsolicited code review |
| Inventory screen/screenshots with `--no-review` | No critic | Visual pair required; optional code review omitted |
| Street renders; standalone install lacks critic-loop | No missing stage reported | Useful asset handoff with visual review explicitly incomplete |
| Change one numeral on an already approved overlay | Targeted correction/check | Targeted check; zero new visual critic rounds |
| Plan only with `--review`; unchanged reference renders | Plan only; code review not run | Plan only; no implementation or criticism of reference assets |
| Sword-effect stills; project requires Claude subscription, threshold 8 | Honor project critic policy, but no critic protocol in wrapper | Claude plus Astra; explicit backend preference does not reduce critic count; motion/sound pending |
| Backend CSV fix with `--review` | Opted-in isolated code review | Same code-review route; no visual stage |

The baseline's exact reasoning for the first case was: “the wrapper supplies
no additional visual-review gate.” Its inventory case likewise found that
the wrapper did not route screenshots to critic-loop by default. The updated
agent selected both named visual critics and separate blind/scored packets.
Its only flagged interpretation concerned whether the project’s mandatory
Claude route excluded a second critic; the final wording explicitly says a
backend preference alone does not reduce critic count.

These are routing observations, not statistical reliability estimates or
proof that future artifacts will pass visual review. Raw scenario responses
were retained in the task's temporary evaluation directory; the table preserves
their material decisions in the repository.

## Actual CLI image checks

A synthetic 256 × 256 PNG contained three vertical rectangles, red, green and
blue from left to right. The same image was used for both checks. Each critic first returned its own blind read, then received its own fixed
blind read and the same predeclared rubric in a separate fresh scored call.
The producer and critics did not share the other critic’s output.

- **Claude Code 2.1.312:** the documented Python dispatch ran with
  `claude-opus-5-5`, `--safe-mode`, `--restricted`, only Read/Glob/Grep,
  `dontAsk`, and an empty strict MCP configuration. Credential/provider
  environment overrides were removed. The event stream recorded
  `apiKeySource: none`, provider `firstParty`, a successful Read of the PNG
  returning image content, and a successful final result identifying the
  red, green and blue rectangles. No write tool was available. CLI list-price
  cost metadata is not evidence of separate API billing.
- **Codex CLI 0.165.0:** a fresh read-only call with `gpt-6-astra`,
  `model_reasoning_effort="ultra"`, and the attached PNG exited 0. Its run
  metadata recorded model `gpt-6-astra`, provider `openai`, and Ultra effort;
  its saved final message identified the same red, green and blue rectangles.
  Local model metadata also lists image input and Ultra effort for this model.

Both scored calls passed at 10/10 with no blocker; the combined lower score was
10/10. This establishes the small synthetic transport/phase fixture, not the
quality of real art or general critic reliability. A later Opus model’s
availability and future account quota must still be checked on each real run.

A separate outside-packet Read was refused with an error explicitly naming
`--restricted` file confinement. Its fixture contained only a synthetic
sentinel. This was a boundary test, not an accepted critic phase. Stdin prompt
input was also exercised successfully. Auth preflight recorded loggedIn true,
authMethod claude.ai, apiProvider firstParty and subscriptionType max without
recording credentials. The final reference requires that preflight before
inference and clears the additional provider selectors identified by Astra.

## Structural checks

- `bash validate-skills.sh`: exit 0; 26 skills passed and one pre-existing
  description warning remained for shaughnessy-iching.
- `claude plugin validate <checkout>`: exit 0, with existing warnings for the
  marketplace description, hook path quoting and missing icon. Those files or
  fields were not changed by this release.
- Changed Markdown relative links resolve; plugin JSON parses, version is
  1.26.0, `skills` remains `./skills`, and marketplace source remains `./`.
- The original Python dispatch was compiled and exercised; review replaced it
  with a raw-stream-only shell recipe using stdin. Equivalent stdin dispatch
  completed the scored and boundary tests. The final literal shell recipe also passed an actual image check with every
  supported provider selector set to a synthetic value in its parent
  environment. Its cleanup restored the expected Opus/firstParty route;
  restricted tools, in-packet image reads and successful final output were
  checked before the accepted result file was written.
- `git diff --check`: passed.
- The bundled generic quick-validator passed deliver-change but rejected
  critic-loop's existing `argument-hint` and `user-invocable` keys. Those keys
  predate this change and are supported by this repository's validator; they
  were not removed to satisfy a narrower validator schema.

Independent source-review results and finding dispositions are recorded in
the adjacent Opus and Astra reports. No game assets, gameplay, animation or
audio were implemented or certified by this plugin change.

## Independent source reviews and final state

Both source reviewers returned **Ready** for the focused repair increment
`78b1b97..e46ca49`. The host recorded Claude Code CLI / claude-opus-5-5 and
Codex CLI / gpt-6-astra at Ultra. Their findings, dispositions and execution
metadata are in the adjacent reports. These were source/instruction reviews,
separate from the synthetic visual critic round described above.

Commit `19d53e1` then applied Opus’s low-severity supervisor clarification and
advisory wording/path improvements. These final documentation edits were
checked directly, without a third independent review. The repository
validator and relative-reference checks were rerun afterward.

The first auth-preflight attempt put a variadic MCP option immediately before
`auth status`, so the CLI treated those words as config files. A second ordering
put unsupported parent flags on the subcommand. The successful ordering is
`claude --strict-mcp-config --mcp-config '{"mcpServers":{}}' --safe-mode
--restricted auth status`, under the same sanitized environment as inference.
No review packet was sent during either failed preflight.
