# Train Trajectories

## data-train-active-skus

- Visible behavior repaired: read SKU from `sku` or `product.sku`, trim blanks,
  accept active/enabled/true tokens, deduplicate by SKU winner, and sort output.
- Train grade: failed, 0.0.
- Verifier feedback: duplicate `a-1` and `A-1` rows were not treated as the same
  normalized SKU, so the lower-priority active feed row survived even though the
  higher-priority catalog row was inactive.
- Lesson: when a task says a grouping key is normalized or compared
  case-insensitively, the repair should compute a canonical key before duplicate
  resolution and use that canonical key consistently for winner choice and output.

## data-train-group-orders

- Visible behavior repaired: read customer aliases, trim strings, parse numeric
  amounts, ignore cancelled/void, and preserve first-seen customer order.
- Train grade: failed, 0.0.
- Verifier feedback: a malformed `customer` dict without an `id` fell through as
  the customer key and caused an unhashable-dict crash.
- Lesson: alias extraction helpers should reject missing, blank, and non-scalar
  values before using them as dictionary keys or grouping keys.

## data-train-normalize-contacts

- Visible behavior repaired: merge duplicate ids, normalize name/email/active,
  sort by id, and emit exact keys.
- Train grade: passed, 1.0.
- Lesson: explicit helpers for rank, aliases, and active/tombstone status made
  the priority/timestamp/input-order merge robust.

## data-train-parse-flags

- Visible behavior repaired: normalize key/name aliases, parse boolean tokens,
  skip blanks, and let later rows override.
- Train grade: passed, 1.0.
- Lesson: compact token helpers are sufficient when duplicate resolution is
  simple last-write-wins.

## data-train-unique-tags

- Visible behavior repaired: accept string and dict aliases, split commas, trim,
  lowercase, collapse whitespace, skip invalid values, and preserve first-seen
  order.
- Train grade: passed, 1.0.
- Lesson: canonicalizing each candidate value before `seen` membership avoids
  duplicate and ordering errors.

## Aggregate Lesson

The parent already mentions normalizing comparison keys, but the train failures
show the instruction is too easy to apply partially. Candidate guidance should
make canonical scalar key helpers explicit for every grouping, deduplication,
and output-key path.
