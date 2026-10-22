# Examples and Source Analysis

These are illustrative rewrites, not analyses that have been run. Adapt
methods to the actual evidence and constraints rather than copying them
into every task.

## Business analysis: investigate a churn claim

**Request:** "Make a quarterly review deck explaining why churn increased.
We think onboarding is the problem. Keep it to six slides."

**Diagnosis:** The deliverable is clear, but the explanation is assumed.
A stronger approach defines churn consistently, checks whether customer
mix changed, and tests the onboarding hypothesis against plausible
alternatives. Relevant event and billing records are more informative
than a chart of aggregate churn alone. Access to those records is an
input requirement, not something the prompt can grant.

**Rewritten prompt:**

> Produce a six-slide quarterly review explaining the increase in churn
> and the decision the evidence supports. Use the supplied billing and
> onboarding event exports; if only aggregate charts are available, state
> what they cannot establish and request the smallest relevant extracts.
> Define the churn numerator, denominator, and observation window before
> comparing acquisition cohorts and customer segments. Check whether the
> aggregate increase persists within comparable groups. Use SQL or a
> dataframe tool to make the calculations reproducible and compare the
> onboarding hypothesis with changes in customer mix and plan mix where
> the supplied fields permit. Treat associations as hypotheses about
> causes. Reconcile customer counts to the billing totals, and test any
> predictive signal on a later period excluded from model selection. If
> there is insufficient history, report that limitation. Deliver six
> slides with source references and reproducible calculations in the
> slide notes, and the next decision or experiment. Stop at the supported
> explanation; do not invent a causal finding or build a monitoring system.

The notes make the calculations inspectable within the six-slide artifact.
An optional appendix should be proposed separately if the calculations
outgrow that format.

## Creative work: deepen a source-based painting prompt

**Request:** "Improve this ink painting prompt based on the supplied verse.
Keep the final prompt under 60 words."

**Diagnosis:** Better adjectives may polish an incorrect interpretation.
Start with the original verse and supplied translation, resolve the image
that carries its meaning, then choose composition and visual emphasis.
Philology contributes source accuracy; painting contributes composition.
Neither requires role-playing a panel of experts.

**Rewritten prompt:**

> Revise the supplied ink painting prompt into fewer than 60 words.
> Compare its depicted action and symbols with the original verse and
> supplied translation. Flag any ambiguity that changes the scene and
> avoid resolving it through invented historical context. Choose a clear
> focal action, framing, and depth that preserve the verse's emotional
> movement. Check the final scene against the source for contradictions
> and count its words. Deliver the prompt and a brief explanation of the
> consequential change. Label aesthetic choices as choices; visual
> coherence and source fidelity do not prove that an image will be liked.

This can lead into Inkstone's verse-to-prompt workflow when appropriate.
It does not replace that skill's established composition guidance.

## Boundary cases

- **"Make this two-line email friendlier; keep it two lines."** Edit the
  email directly unless the user requests a deeper brief. No raw-data
  investigation or audience study is needed.
- **"Review this implementation plan for missing steps."** Use
  plan-review-loop for the review. Deepen-task addresses how to frame the
  task, not the lifecycle of reviewing a written plan.
- **"Give me a deeper approach, then implement it in this repo."** Write
  the brief and proceed with authorized implementation. Do not stop after
  prompt rewriting merely because rewriting is this skill's default.
- **"Use only this PDF to rewrite my analysis prompt."** Work within that
  evidence boundary. Explain what the PDF cannot establish; do not fetch
  raw customer data or treat a desired finding as verified.

## Source and interpretation

- **Post analyzed:** [CG, 15 October 2026](https://x.com/cgtwts/status/2110571916973207906).
  Its two attached screenshots highlight a depth-oriented prompt and the
  four-lens framework. The short caption comments on the author's role;
  the reusable method is in the screenshots and linked article.
- **Original announcement:** [Felix Rieseberg, 13 October 2026](https://x.com/felixrieseberg/status/2110023283169247623).
  He describes himself as an engineering lead working on Claude. That
  wording does not establish that he is Anthropic's sole lead engineer.
- **Primary source:** [How to be more ambitious: A tutorial for humans with models](https://felixrieseberg.com/how-to-be-more-ambitious-a-tutorial-for-humans-with-models/),
  published 13 October 2026; read with both screenshots on 22 October 2026.

The useful distinction is between improving the task's formulation and
merely increasing its volume. The article connects that to four lenses:
speed, altitude, depth, and range. Its most directly reusable move is to
ask what professional work is missing, find the underlying evidence,
choose real methods, and define an outside check before rewriting a
request. It also warns that expert vocabulary and theatrical personas
can leave the method unchanged.

This is practitioner advice, not a controlled demonstration that a
particular prompt reliably improves every task. The skill therefore
requires task-specific evidence and checks rather than promising an
improvement. It treats aggressive targets as hypotheses to test and
cross-disciplinary work as concrete contributions, without importing
the article's expansive access assumptions or rhetorical encouragement
to keep pushing indefinitely.
