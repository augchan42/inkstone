# Licence classes — the only taxonomy the audit uses

Every flagged package lands in exactly one class. The class decides the
flag level, never the verdict. Verdicts belong to a lawyer.

## Permissive

MIT, ISC, Apache-2.0, BSD-2-Clause, BSD-3-Clause, CC0-1.0, Unlicense, 0BSD,
Python-2.0, Zlib, BSL-1.0, Artistic-2.0, BlueOak-1.0.0.

Commercial use is allowed. The standing obligation is attribution: ship the
licence text and copyright notices with the product. The most common real
failure is not copyleft at all — it is a shipped app or image with no
NOTICE file.

## Weak copyleft

LGPL-2.0/2.1/3.0 (only or or-later), MPL-2.0, EPL-1.0/2.0, CDDL-1.0.

Proprietary combination is usually allowed, but the component's own source
(and sometimes the mechanism that links it) must be offered, and notices
must be preserved. How the component is linked — static, dynamic, separate
process — changes the answer, which is why weak copyleft always gets a
MEDIUM flag and a question for counsel, not a pass.

## Strong copyleft

GPL-1.0/2.0/3.0 (only or or-later).

Triggered by distribution of a combined or derivative work: the combined
work must be offered under the same licence, source included. "We only run
it on our servers" avoids the trigger for GPL (not for AGPL, below) — but
on-prem delivery, mobile apps, containers handed to customers, and OEM
deals all count as distribution. HIGH flag in production scope, always.

## Network copyleft / source-available

AGPL-3.0 (only or or-later), SSPL-1.0, Elastic-2.0, BUSL-1.1.

AGPL closes the SaaS gap: users interacting with the software over a
network trigger disclosure. SSPL, Elastic-2.0, and BUSL are not OSI
open-source licences at all — they restrict competitive hosting and carry
their own commercial terms. Treat any of these in a commercial product as
HIGH until counsel says otherwise.

## Needs review

Anything the scanner does not recognise: missing licence fields,
`SEE LICENSE IN <file>`, `LicenseRef-` ids, unparseable expressions, and
dual licences (`MIT OR GPL-3.0`). For compounds the script reports the
strictest class and names the part it could not read. A human opens the
actual licence text. There is no shortcut for this step.

## Triggers, plainly

| Licence family | SaaS-only | Distributed (on-prem, app, image, OEM) |
|---|---|---|
| Permissive | Attribution | Attribution |
| Weak copyleft | Notices; component source on request | Notices; component source; linking terms apply |
| Strong copyleft (GPL) | Usually no trigger — confirm | Combined-work source disclosure |
| Network copyleft (AGPL) | Source disclosure on network use | Source disclosure |

"Usually" and "confirm" are doing load-bearing work in that table. The
table triages. Counsel concludes.
