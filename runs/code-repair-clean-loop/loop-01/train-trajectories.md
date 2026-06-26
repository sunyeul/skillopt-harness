# loop-01 Train Trajectories

All evidence below comes from train tasks prepared with explicit `--split train`.

## train-addition-bug

- Contract: `add_numbers` returns the sum of both inputs.
- Visible coverage: one positive-number assertion, `add_numbers(2, 3) == 5`.
- Initial behavior: returned `a - b`.
- Repair action: changed the operator to `a + b`.
- Verifier feedback: score `1.0`; visible and hidden tests passed.
- Lesson: the task description can fully identify the intended behavior even when visible coverage is minimal.

## train-clamp-bug

- Contract: `clamp` returns the value bounded by inclusive low and high limits.
- Visible coverage: one above-high assertion, `clamp(12, 0, 10) == 10`.
- Initial behavior: returned `value` unchanged.
- Repair action: implemented `max(low, min(value, high))`.
- Verifier feedback: score `1.0`; visible and hidden tests passed.
- Lesson: visible tests may cover only one boundary; repair should enumerate both lower and upper contract boundaries.

## train-normalize-people

- Contract: return people sorted by id; each output person has `id`, `name`, and `active`; trim and title-case names; default missing `active` to `False`.
- Visible coverage: mixed ordering, whitespace, title casing, and missing active default.
- Initial behavior: returned the input unchanged.
- Repair action: built normalized dictionaries with the required fields and sorted by `id`.
- Verifier feedback: score `1.0`; visible and hidden tests passed.
- Lesson: data-shaping tasks need explicit field/default/order handling, not mutation or passthrough.

## train-parse-duration

- Contract: parse space-separated duration tokens with `h`, `m`, and `s` units; sum total seconds; invalid tokens raise `ValueError`.
- Visible coverage: one combined hours-and-minutes assertion.
- Initial behavior: stripped the final character and converted the remaining text to int.
- Repair action: split into tokens, validated unit and numeric amount, applied unit multipliers, and raised `ValueError` for invalid tokens.
- Verifier feedback: score `1.0`; visible and hidden tests passed.
- Lesson: parser repairs should implement all specified token forms and invalid-input behavior even if visible coverage shows only one valid example.

## train-stable-frequency

- Contract: return the `limit` most frequent labels, sorted by descending frequency and first-seen order for ties.
- Visible coverage: one frequency ordering assertion without a tie.
- Initial behavior: sorted unique labels alphabetically.
- Repair action: counted labels, recorded first-seen indexes, and sorted by `(-count, first_seen)`.
- Verifier feedback: score `1.0`; visible and hidden tests passed.
- Lesson: ranking repairs should preserve stability requirements named in the description, including tie behavior not directly visible.

## Cross-task pattern

The parent skill already says to read task metadata and visible tests, but train evidence shows a recurring need for an explicit procedure: convert the task description into a short behavioral checklist, compare the current implementation against every listed behavior, and use visible tests as examples rather than as the full contract.
