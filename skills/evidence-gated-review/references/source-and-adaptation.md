# Source and adaptation

Inspired by [How the Claude Code team does code review](https://claude.dev/blog/solving-code-review-at-anthropic/)
by Addy Osmani, Morgan Westlee Lunt, and Qing Wang, published October 15, 2026.
Discovered through [Igor Carvalho Rodrigues's LinkedIn summary](https://www.linkedin.com/posts/igorrodrigues14_how-the-claude-code-team-does-code-review-activity-7518164995688321024-AprY).

The article describes Anthropic's own layered checks, risk-sensitive human
review, reviewer evaluation from past failures, and measures against endless
review cycles. Those are ideas, not configuration supplied by this plugin.

This adaptation adds an Inkstone-specific evidence ledger and readiness packet
around the existing independent reviewer. It does not reproduce Anthropic's
approval counts, trusted-author list, infrastructure, or deployment assumptions.
Repository policy and the user's actual authorization remain authoritative.

The three-round ceiling is a stopping point for reconsideration, not evidence
of correctness. Evaluation is optional maintenance. Recovery must be assessed
for the target system rather than assumed.
