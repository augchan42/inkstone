# HKOSCon 2026 — Gallery Slide Verses

Five full-screen result slides (slides 16–20), one per style category. Each slide shows the generated painting with the source Jiaoshi Yilin (焦氏易林) couplet in Chinese and English.

## Slide Mapping

| Slide | Style | Verse Key | Hexagrams | CDN Image | Chinese | English |
|-------|-------|-----------|-----------|-----------|---------|---------|
| 16 | atmospheric-night | 21-27 | 噬嗑 → 頤 (Biting Through → Nourishment) | `yilin-inkbrush/21-27.webp` | 明滅光息，不能復食；精魄既喪，以夜為室 | Light dims, radiance dies. Night becomes one's dwelling. |
| 17 | ink-landscape | 1-16 | 乾 → 豫 (Creative → Enthusiasm) | `yilin-inkbrush/1-16.webp` | 禹鑿龍門，通利水源；東注滄海，民得安存 | Yu carved Dragon Gate and opened the water's source. Flowing east to the vast sea, the people found safe dwelling. |
| 18 | figures-in-mist | 41-42 | 損 → 益 (Decrease → Increase) | `yilin-inkbrush/41-42.webp` | 雨師娶婦，黃岩季子；成禮既婚，相呼面南 | The Rain Master takes a bride. Rites completed, they face south. Timely rain; a bountiful year. |
| 19 | bold-action | 42-8 | 益 → 比 (Increase → Holding Together) | `yilin-inkbrush/42-8.webp` | 白龍黑虎，起伏俱怒；蚩尤敗走，死於魯首 | White dragon and black tiger rise in shared fury. Chi You flees in defeat. |
| 20 | cosmic-night | 64-54 | 未濟 → 歸妹 (Before Completion → Marrying Maiden) | `yilin-inkbrush/64-54.webp` | 龍生馬淵，壽考且神；飛騰上天，舍宿軒轅 | The dragon born in the deep pool, long-lived and divine. Flying upward to heaven, dwelling among the stars. |

## CDN Base URLs

- Yilin inkbrush paintings: `https://cdn.sixlines.online/yilin-inkbrush/{from}-{to}.webp`
- Verse data source: `sixlines-ios/data/yilin/prompts/*.json` (prompts) + `sixlines-site/src/data/yilin/verses.json` (Chinese text & gloss)

## Selection Criteria

Each verse was chosen for:
1. Strong visual imagery that matches its style category
2. Short, memorable Chinese couplet (16–20 characters)
3. Painting quality — the generated image is a strong exemplar of the style

## Slide 15 (What the Human Kept) — Style Category Thumbnails

These are separate images from the gallery slides, used as small thumbnails on the rules overview:

| Style | Image Key | CDN Path |
|-------|-----------|----------|
| atmospheric-night | 52-39 | `yilin-inkbrush/52-39.webp` |
| ink-landscape | 47-29 | `yilin-inkbrush/47-29.webp` |
| figures-in-mist | 3-20 | `yilin-inkbrush/3-20.webp` |
| bold-action | 29-7 | `yilin-inkbrush/29-7.webp` |
| cosmic-night | 1-14 | `yilin-inkbrush/1-14.webp` |
