## Scope

Reviewed only changes introduced by `c3f5070..78b1b97`: seven files, 190 changed lines.

Exact command:

```sh
git diff c3f5070d34598387940ecce29eaa1a9f73ea9f49..78b1b97899ca0492a96a163d97eb5bbf812a47df
```

Backend/model: current Codex session, GPT-6; exact model variant is not exposed. No additional reviewer or third-party service was invoked.

## Findings

1. **Medium (P2) — Security: managed hooks remain active in the purportedly isolated critic.**
   **Location:** [skills/critic-loop/references/claude-code.md:19](/private/tmp/inkstone-deliver-change-20261028/skills/critic-loop/references/claude-code.md:19)

   The reference says `--safe-mode` disables hooks, but the installed Claude Code **2.1.312** explicitly retains managed hooks: its hook-selection function returns `policySettings.hooks` when safe mode is enabled. Restricting model tools to Read/Glob/Grep does not disable those hooks.

   On a machine with managed hooks, the critic can therefore execute hook commands or receive injected context, violating the stated read-only and blind-review contracts. Checking source integrity afterward detects some consequences but does not prevent them.

   **Correction:** Check effective managed hooks before dispatch. If the required isolation cannot be enforced under existing policy, mark this route unavailable. Correct the claim that safe mode disables all hooks.

2. **Medium (P2) — Contracts & call sites: environment cleanup does not enforce subscription routing.**
   **Location:** [skills/critic-loop/references/claude-code.md:49](/private/tmp/inkstone-deliver-change-20261028/skills/critic-loop/references/claude-code.md:49)

   The dispatch copies the parent environment but removes only three cloud-provider selectors. Claude Code 2.1.312 also recognizes `CLAUDE_CODE_USE_ANTHROPIC_AWS`, `CLAUDE_CODE_USE_ANTHROPIC_GOOGLE_CLOUD`, and `CLAUDE_CODE_USE_MANTLE`; all survive this cleanup and select their respective providers instead of the subscription route.

   If one is inherited and cloud credentials are available, the review can send artifacts through a separately billed provider despite an available Claude subscription. Recording the actual route afterward is too late to enforce this restriction.

   **Correction:** Handle all supported provider selectors and verify the effective authentication/provider route before inference using the same environment. Reject a route that does not satisfy the subscription requirement.

## Verification limitations

- Read the exact diff first, then relevant changed files and direct references.
- Inspected the locally installed CLI without launching it.
- An isolated, in-memory check confirmed the three omitted provider flags survive cleanup. Python syntax and changed skill name/description checks passed.
- No live authentication, image-reading, or two-critic execution was tested. No files were written, staged, or committed.

## Verdict

**Needs revision.**

## Host execution record

Actual backend: Codex CLI 0.165.0, model `gpt-6-astra`, provider `openai`, reasoning effort `ultra`, read-only sandbox. The model’s self-description above did not expose its exact variant; the CLI run metadata did. Process exited 0 and its saved final review was nonempty. Reviewed source remained unchanged.

## Disposition

- Finding 1 — ACCEPTED: corrected the safe-mode claim; managed hooks still apply. The route now requires preflight inspection of effective managed settings and is unavailable when the required isolation cannot be verified.
- Finding 2 — ACCEPTED: clear the additional supported AWS, Google Cloud and Mantle selectors; require auth/provider/subscription preflight in the same sanitized environment before sending the packet. Post-run provider identity remains a consistency check.

Repairs are in `e46ca49`. A focused review of that increment is recorded separately.
