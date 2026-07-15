# Obsidian JSON Canvas rules

These rules apply to every board. A style file supplies color roles and mood; this file defines the native medium and quality bar.

## Contents

1. Native file format
2. Z-order and grouping
3. Geometry, alignment, and spacing
4. Text
5. Colors
6. Semantics and connectors
7. Existing-board edits
8. Verification checklist

## 1. Native file format

Use JSON Canvas 1.0 with top-level `nodes` and `edges` arrays. Do not add invented presentation fields.

Every node requires string `id` and `type`, plus integer `x`, `y`, `width`, and `height`. Width and height must be positive.

Supported node types and fields:

- `text`: required string `text`, using Markdown.
- `file`: required Vault-relative string `file`; optional `subpath` starting with `#`.
- `link`: required string `url`.
- `group`: optional string `label`, optional string `background`, and optional `backgroundStyle` of `cover`, `ratio`, or `repeat`.

Every edge requires string `id`, `fromNode`, and `toNode`. Optional sides are `top`, `right`, `bottom`, or `left`; optional ends are `none` or `arrow`; optional `label` is a string.

Colors must be a six-digit hex string such as `#E85D5D`, or preset string `1` through `6`. Prefer explicit hex colors for bundled styles.

Use unique IDs across all nodes and edges. Keep stable IDs when editing.

## 2. Z-order and grouping

The first item in `nodes` renders below later items. Place group nodes before the nodes they visually contain.

- Use groups for semantic regions, layers, columns, or phases.
- Leave at least 50 px between a group's boundary and its contents; use 70 px where the group has a label.
- Do not use overlapping groups unless the overlap is the meaning of the diagram.
- Avoid a decorative full-board group. JSON Canvas has no global background field; let whitespace remain the canvas ground.
- Keep titles outside groups unless the title belongs only to that group.

## 3. Geometry, alignment, and spacing

Let content define the bounds. A typical landscape board is 1400–2200 px wide.

- Board title: 600–1000 × 100–160 px.
- Standard card: at least 240 × 120 px.
- Compact label: at least 200 × 90 px.
- Dense explanatory card: 280–380 × 160–240 px.
- Gap between sibling cards: 40–80 px.
- Gap between major groups or layers: 100–160 px.
- Outer breathing room: at least 100 px.

Align sibling nodes to a shared grid. Reuse widths and heights within the same semantic role. Nodes in a row must share the exact `y` and height; nodes in a column must share the exact `x` and width. Equal-role siblings must use equal gaps. Do not overlap ordinary nodes; touching edges still feels cramped, so maintain a visible gap.

- Snap peer coordinates exactly; do not leave 1–8 px visual drift.
- Keep at least 50 px group padding on the left, right, and bottom, and at least 70 px at the top when the group has a label.
- Use 200–240 × 90–120 px for compact semantic routing hubs. Give them a color and a short noun label so they remain visually distinct from content cards.
- Reserve an empty routing column for a skip-layer edge instead of sending it through intervening cards.

## 4. Text

Use Markdown hierarchy instead of unsupported font controls.

- Use `#` for the board title and `##` for card or section titles.
- Keep a standard card to a short heading plus two to four compact lines or bullets.
- Wrap long text intentionally with line breaks. Avoid Markdown tables inside text nodes.
- Do not reduce a node below the minimum sizes to make a diagram fit.
- Remove prompt restatements, tool names, file paths, style labels, citations, validation notes, and build metadata from the board.

Estimate CJK characters at roughly 16 px wide and Latin characters at roughly 8 px. Allow about 22 px line height plus 28–40 px total vertical padding. Treat the validator's text-capacity result as conservative.

## 5. Colors

Obsidian Canvas exposes a node or edge `color`; it does not expose per-node font family, text color, border width, corner radius, opacity, gradient, blur, or shadow in JSON Canvas 1.0.

- Use uncolored or pale nodes for ordinary content.
- Use the style's primary color for titles, milestones, or decisive nodes.
- Use the secondary color for groups or supporting nodes.
- Use one connector color per flow; use a second only to distinguish a genuinely different relationship.
- Keep no more than three active accent colors in one view, even when a palette contains more.
- Never emulate unsupported styling with CSS or nonstandard JSON keys.

## 6. Semantics and connectors

Create the semantic edge list before coordinates. For every edge, record its source, target, direction, relation type, and reason. Reject any edge whose only justification is visual symmetry, shared column position, or proximity.

Choose one main direction after the edge list is stable.

- Horizontal flow: connect `right` to `left`.
- Vertical flow: connect `bottom` to `top`.
- Use `fromEnd: "none"` and `toEnd: "arrow"` for directed flow.
- Keep every necessary dependency. Do not delete a real edge or add a false edge to make the picture symmetrical.
- Target zero crossings where the real graph permits it and zero lines through unrelated nodes. Reorder neighboring layers, reserve routing gutters, or introduce a genuine semantic hub before accepting a crossing.
- Keep an ordinary node's total degree at four or fewer.
- A compact colored semantic routing hub may have degree up to six. Its label must describe the shared function, and its incoming and outgoing edges must all match that meaning.
- Keep edge labels under about 12 CJK characters or 24 Latin characters.
- Do not connect every detail to every downstream detail. Use groups, one visible backbone, or category hubs.
- If a hub requires more than six links, split it into meaningful category hubs or express non-relational membership spatially.
- Model security, privacy, compliance, tenancy, and observability as cross-cutting regions or support rails when they apply broadly; do not pair them arbitrarily with upstream cards.

Mixed horizontal and vertical connectors are acceptable only when the secondary direction is clearly a branch off the dominant flow.

## 7. Existing-board edits

- Inspect the current JSON before every patch.
- Preserve content-bearing fields and IDs by default.
- Make the smallest useful change: move a node, widen a card, rewrap text, recolor a region, or replace a noisy edge set.
- Do not silently delete content. If an edge is redundant because grouping now carries the relationship, remove only that edge and retain both nodes.
- Do not overwrite another `.canvas` file or the Vault configuration.

## 8. Verification checklist

Before delivery:

1. Parse the JSON successfully.
2. Confirm unique IDs and valid edge references.
3. Run the validator in strict mode.
4. Confirm every edge appears in the semantic map and still means what its source and target imply.
5. Confirm the title and all required content are present.
6. Confirm peers are aligned, equal-role gaps and dimensions are consistent, and group padding is sufficient.
7. Confirm no unexplained overlaps, clipped text, avoidable edge crossings, or lines through nodes remain.
8. Open the board in Obsidian and capture a screenshot.
9. Inspect the screenshot at readable zoom, then batch all visible fixes into one targeted edit pass.
10. Revalidate and reopen after the final edit.
