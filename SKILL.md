---
name: beautiful-obsidian-canvas
description: Create, restyle, and repair polished, editable Obsidian Canvas (.canvas) boards using native JSON Canvas nodes, groups, links, and edges. Use for architecture diagrams, flowcharts, timelines, comparisons, system maps, kanbans, infographics, visual explainers, named bundled styles, or existing boards with cluttered layout, incorrect or crossing connectors, misalignment, overlaps, or text overflow. For new boards and full restyles, offer curated style and layout choices unless the user already chose or delegated the decision. Requires Obsidian CLI only for opening and screenshot verification, not for JSON generation.
---

# Beautiful Obsidian Canvas

Build a real `.canvas` file that remains editable in Obsidian. Treat the style library as a palette and layout mood, not as a screenshot template or an automatic layout engine.

## Core workflow

1. Run `bash scripts/preflight.sh [canvas-path]` before CLI-dependent work.
2. Determine the content, purpose, audience, target Vault, and desired visual mood.
3. For a new board or full restyle, read [references/CATALOG.md](references/CATALOG.md). If the user did not name a style, present three relevant choices with vibe, formality, palette, and one recommendation; ask the user to choose or delegate. Wait unless the user already delegated. For a targeted repair, preserve the current style unless asked to change it.
4. Read [references/LAYOUTS.md](references/LAYOUTS.md). When more than one layout materially fits, present two or three choices with one recommendation; ask the user to choose or delegate. Wait unless the user already delegated.
5. Build a semantic map before coordinates: list every node, every necessary edge, its direction, relation type, and one-line reason. Never infer an edge from proximity, symmetry, or column position.
6. Read [references/RULES.md](references/RULES.md) and only the selected style file. Place nodes from the semantic graph, align them to a shared grid, and minimize crossings by reordering nodes or adding only genuine routing hubs.
7. Create or patch the `.canvas` file with native JSON Canvas 1.0 fields only.
8. Run `python3 scripts/validate_canvas.py <canvas>` during iteration and `python3 scripts/validate_canvas.py <canvas> --strict` before delivery.
9. Run `bash scripts/open_and_snapshot.sh <canvas> <preview.png>`, inspect the screenshot, and make small targeted corrections. Repeat until clean.
10. Deliver the `.canvas` path and preview image. State the chosen style and layout in chat, and mention that the same content can be switched to another bundled style.

## Create a new canvas

- Resolve the active Vault with `obsidian vault info=path` when the user did not provide one.
- Choose a descriptive `.canvas` filename and refuse to overwrite an existing file unless the user explicitly requested replacement.
- Compose the node inventory and semantic edge list before assigning coordinates. Put group nodes before their contents so z-order is correct.
- Generate opaque, unique IDs for every node and edge. Keep IDs stable across later edits.
- Keep every necessary relationship even when it complicates layout. Reduce visual complexity with graph-aware ordering, real semantic hubs, groups, and routing corridors; never with invented one-to-one mappings.
- Model cross-cutting concerns such as security, compliance, and observability as spanning regions or clearly named support hubs instead of pairing them arbitrarily with upstream nodes.

## Edit an existing canvas

- Read the current file immediately before editing because Obsidian may reorder or reformat JSON after opening.
- Preserve node IDs, text, file paths, URLs, and semantic groupings unless the requested change requires otherwise.
- Patch positions, sizes, colors, and edges in place. Do not regenerate the entire board to fix a local defect.
- Audit each connector against the semantic map. Remove incorrect or redundant edges, but never remove a real dependency merely to reduce crossings.
- When simplifying connectors, keep the business meaning and replace repeated relationships only with a genuine backbone or category hub whose label accurately describes the aggregation.
- Compare node and edge counts before and after; explain intentional removals.

## Visual quality contract

- Treat semantic correctness as a hard requirement. A clean but false graph is invalid.
- Use one dominant reading direction and order each layer from the adjacency of neighboring layers, not from cosmetic symmetry.
- Target zero edge crossings where the real graph permits it and zero connectors passing through unrelated nodes. Reorder nodes or use genuine hubs before accepting crossings; never alter meaning to reach zero.
- Keep total degree at four or fewer for ordinary nodes. A compact, colored semantic routing hub may reach six when its fan-in and fan-out are intentional and readable.
- Align peer nodes to exact shared coordinates, reuse sizes by role, distribute equal gaps, and preserve group padding.
- Keep text comfortably inside nodes with visible padding. Widen or heighten a node before shrinking content.
- Never print the prompt, chosen style name, source path, implementation notes, or validation results on the board.
- Do not create CSS snippets, modify `.obsidian`, or depend on a community plugin. A screenshot is a preview; the `.canvas` file is the source artifact.

## Tool behavior

- JSON creation and validation can continue without Obsidian CLI when a target Vault path is known.
- If the CLI or running app is unavailable, report the missing prerequisite and do not claim that opening or visual verification succeeded.
- Treat validator warnings as review prompts. Use visual judgment for intentional proximity, but resolve every unexplained overlap or crossing.

## Reference routing

- Style selection: [references/CATALOG.md](references/CATALOG.md)
- Canvas medium and verification rules: [references/RULES.md](references/RULES.md)
- Layout patterns and coordinates: [references/LAYOUTS.md](references/LAYOUTS.md)
- One selected palette: the matching file under `references/styles/`
