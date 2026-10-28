---
name: site-design
description: Apply this website’s UI preferences when designing or editing its pages, content lists, metadata, and embedded excerpts. Scoped to SriMed.github.io.
---

# Website design preferences

Apply these preferences within this website. Adapt them to the task and preserve later explicit user choices; they are not global design rules.

- Remove labels and explanatory copy when the surrounding content and layout already make their meaning clear. Avoid redundant status badges and headings inside excerpts.
- Group related metadata into one quiet line, separated by middle dots. For content entries, prefer `Author · Media type · Publication date`, without a `Published:` prefix. Allow natural wrapping on narrow screens.
- Use small, italic text for secondary context, source/cadence captions, and personal activity dates. Avoid bold emphasis for routine metadata.
- Omit missing optional information instead of displaying absence messages such as “date not recorded.” Never invent dates to fill a gap.
- Distinguish excerpts from surrounding page content with a subtle shared frame. Keep the entries together; avoid an extra “Notion excerpt” heading when the frame and source caption already establish the context.
- Keep publication dates separate from personal reading/listening/watching dates. Put known activity dates below the metadata as small italic `Read: …`, `Listened: …`, or `Watched: …` text; omit that line when unknown. State cadence only as supported by the actual sync configuration.

Before presenting a UI change, inspect the rendered result for redundant copy and unnecessary emphasis, including at narrow widths. Keep source and sync details in the quiet caption rather than explaining implementation in the main page copy.
