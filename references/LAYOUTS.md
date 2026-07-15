# Native Canvas layout patterns

Choose one primary pattern. Coordinates are starting grids, not fixed templates; expand them to fit content. Build the semantic graph before selecting coordinates.

## Graph-aware placement

1. Write the necessary edge list first. Give every edge a direction, relation type, and reason.
2. Assign nodes to layers or lanes from their role in that graph.
3. Order each layer by the median or barycenter of its neighbors in the adjacent layer; repeat top-down and bottom-up until crossings stop improving.
4. Align important dependencies vertically or horizontally. Reserve empty columns or gutters for long skip-layer connections.
5. Use a compact routing hub only when several edges genuinely share the same semantic aggregation. Label it with a noun phrase; never use an unlabeled cosmetic junction.
6. Represent cross-cutting capabilities as a spanning group or support rail. Do not force them into one-to-one vertical chains.
7. Snap peers to exact shared `x` or `y` coordinates, reuse dimensions by role, and distribute equal gaps before visual review.

## 1. Stage flow

Use for sequential processes with three to six stages.

- Put the title around `(0, -260)` with size `800 × 120`.
- Place stages left to right at `x = 0, 360, 720...`, sharing one `y` and one card size near `280 × 160`.
- Connect `right` to `left`; keep branches below their owning stage.
- For more than six stages, wrap into two clearly numbered rows rather than compressing cards.

## 2. Timeline

Use for events, releases, or historical progression.

- Build one horizontal backbone with milestones spaced 320–420 px apart.
- Place event cards consistently above the backbone; use below only for a second explicit track.
- Connect milestone to milestone, not every event card to every other card.
- Keep dates in the milestone card so connector labels remain short.

## 3. Layered architecture

Use for business, product, AI, data, platform, or governance stacks.

- Use landscape groups about `1800 × 260–360` px.
- Stack groups vertically with 100–140 px gaps.
- Keep cards in aligned rows inside each group.
- Use one left-side or center backbone between layer headers. Draw the real module dependencies separately; do not substitute a cosmetic backbone for required relationships.
- Reorder cards within each layer from their real adjacency. Add a routing hub in the inter-layer gap only when it represents a genuine shared entry, orchestration, or support function.
- Put outcomes at the top and foundations at the bottom unless the audience expects the opposite convention.
- Put security, compliance, tenancy, and observability in a spanning foundation or side rail when they support several layers.

## 4. Comparison matrix

Use for alternatives, before/after states, or capability comparisons.

- Create two to four equal-width column groups with 60–100 px gutters.
- Keep the same row order and card dimensions in every column.
- Use color to identify the winning or highlighted column; do not connect corresponding cells unless the comparison depends on transformation.
- Put shared evaluation criteria in a narrow left column when there are three or more rows.

## 5. Center and satellites

Use for an ecosystem, product map, or concept overview.

- Put one hub near `(0, 0)` at `320 × 180`.
- Place up to four category nodes on the cardinal sides, at least 260 px from the hub boundary.
- Put detailed nodes behind category nodes without direct links to the central hub.
- For five or more categories, switch to a grouped grid or use two category hubs; do not create a high-degree starburst.

## 6. Kanban or workboard

Use for status, ownership, or work stages.

- Create three to five equal-width vertical groups.
- Align group tops and card widths; stack cards with 40–60 px gaps.
- Use no edges unless a specific dependency must be visible.
- Put status in group labels and ownership or priority inside cards rather than adding decorative badges.

## Choosing quickly

- Ordered transformation → Stage flow.
- Time-based narrative → Timeline.
- Support stack or system levels → Layered architecture.
- Alternatives or criteria → Comparison matrix.
- One concept with categories → Center and satellites.
- Status or ownership → Kanban.
