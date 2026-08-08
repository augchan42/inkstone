#!/usr/bin/env python3
"""Flag CJK characters in built slides that do NOT appear in the source text.

Catches the silent-corruption failure mode where a hand-authored numeric XML
entity (e.g. &#22317;) decodes to a valid-but-wrong character. Since every
codepoint decodes to *some* real glyph, the pack/validate tooling never errors;
the only reliable signal is that the wrong character is not in the source deck's
character inventory.

Usage:
    python audit_cjk.py <source_text.md> <unpacked_build_dir>

  <source_text.md>      Ground-truth text: `python -m markitdown source.pptx > source_text.md`
  <unpacked_build_dir>  The directory you are about to pack (contains ppt/slides/*.xml)

Exit code 0 = clean, 1 = suspicious characters found (review before packing).
"""

import glob
import re
import sys
from pathlib import Path

CJK = lambda c: (
    "一" <= c <= "鿿"      # CJK Unified Ideographs
    or "㐀" <= c <= "䶿"   # Extension A
    or "豈" <= c <= "﫿"   # Compatibility Ideographs
)
ENTITY = re.compile(r"&#(\d+);")
ATAG = re.compile(r"<a:t[^>]*>(.*?)</a:t>", re.S)


def decode(raw: str) -> str:
    return ENTITY.sub(lambda m: chr(int(m.group(1))), raw)


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    source_text = Path(sys.argv[1]).read_text(encoding="utf-8")
    source_chars = {c for c in source_text if CJK(c)}

    slide_files = sorted(
        glob.glob(f"{sys.argv[2]}/ppt/slides/slide*.xml"),
        key=lambda p: int(re.search(r"(\d+)", Path(p).name).group(1)),
    )

    suspicious = []
    for f in slide_files:
        content = Path(f).read_text(encoding="utf-8")
        for m in ATAG.finditer(content):
            text = decode(m.group(1))
            bad = {c for c in text if CJK(c) and c not in source_chars}
            if bad:
                suspicious.append((Path(f).name, "".join(sorted(bad)), text.strip()))

    if not suspicious:
        print("CJK audit clean: every CJK char in the build appears in the source.")
        return 0

    print("SUSPICIOUS CJK — not present in source text (likely corruption):\n")
    for name, bad, text in suspicious:
        print(f"  {name}: [{bad}] in: {text[:80]}")
    print("\nVerify each against the source; do not pack until resolved.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
