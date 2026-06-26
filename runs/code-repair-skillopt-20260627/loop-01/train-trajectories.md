# Train Trajectories

All evidence below is from prepared `code_repair` train workspaces and train
grades only.

| Task | Visible behavior | Repair action | Train score | Lesson |
|---|---|---|---:|---|
| train-expression-evaluator | precedence, parentheses, unary signs, variables, and `//` | compact recursive-descent parser covering the visible grammar plus adjacent malformed-input checks | 1.0 | Visible tests required a real parser; the parent warning against parsers is too strong unless scoped to unrelated generality. |
| train-capacity-allocator | min-first allocation, integer-string coercion, priority ordering, input preservation | implemented one-unit-at-a-time priority allocation with coercion and validation helpers | 1.0 | Visible behavior and task contract shared one allocation loop; adjacent validation/coercion was cheap and useful. |
| train-dependency-order | deterministic topological ordering for mapping/list inputs and duplicate dependency collapse | implemented compact topo sort with duplicate-name, optional-dependency, unknown-dependency, and cycle handling | 1.0 | Determinism and validation belong in the same algorithm, not as unrelated edge-case expansion. |
| train-normalize-people | id/name aliases, title-casing, duplicate overwrite, schema control, input preservation | implemented small normalizer helpers for id/name/active | 1.0 | Normalization tasks need a coherent contract slice, including adjacent alias and token validation. |
| train-parse-duration | compact/spaced/case-insensitive unit parsing | implemented token scanner with unit families and duplicate rejection | 1.0 | A small scanner can cover visible behavior and adjacent invalid cases without becoming a broad parser. |
| train-quoted-tokens | separators outside quotes, quoted groups, empty quoted tokens | implemented state-machine tokenizer with escapes/comments/error handling | 1.0 | When visible tests require state, a compact state machine is appropriate despite the baseline warning. |
| train-rolling-window | numeric strings, dict values, invalid skips, rolling summaries | implemented numeric coercion and rolling window helper, including reset behavior from the same loop | 1.0 | Adjacent `task.json` rules that share the visible loop should be included when low-cost. |
| train-stable-frequency | trim/lower/count, first-seen tie order, input preservation | implemented count plus first-seen order | 1.0 | Stable ordering and input preservation are contract details that fit the visible behavior family. |

## Aggregate Lesson

The redesigned train fixtures reward compact coherent implementations of the
visible behavior family, not literal one-assertion patches. The parent skill
over-penalizes parsers/state machines and instructs agents to ignore
`task.json` edge cases too aggressively, even when those cases are naturally
handled by the same helper or loop needed for visible tests.
