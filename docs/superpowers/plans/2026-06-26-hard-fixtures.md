# Hard Fixtures Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make both `data_normalization` and `code_repair` fixtures substantially harder while preserving the manual SkillOpt harness contract.

**Architecture:** Keep the fixture directory layout unchanged and harden each existing task in place. Each task keeps one public function, a weak starter implementation, a stronger `task.json` contract, a representative visible test, and stricter hidden tests.

**Tech Stack:** Python fixtures, pytest, `uv run skillopt-harness`, `uv run pytest`, `uv run ruff check .`

---

## File Structure

- Modify every existing `fixtures/data_normalization/{train,selection,test}/*/task.json`.
- Modify every existing `fixtures/data_normalization/{train,selection,test}/*/tests_visible/test_*.py`.
- Modify every existing `fixtures/data_normalization/{train,selection,test}/*/tests_hidden/test_*.py`.
- Modify data-normalization starter source files only when a function name or starter weakness must stay aligned with the new contract.
- Modify every existing `fixtures/code_repair/{train,selection,test}/*/task.json`.
- Modify every existing `fixtures/code_repair/{train,selection,test}/*/tests_visible/test_*.py`.
- Modify every existing `fixtures/code_repair/{train,selection,test}/*/tests_hidden/test_*.py`.
- Modify code-repair starter source files only to keep intentionally weak but syntactically valid implementations.
- Do not modify `skillopt.yaml`, `skillopt_harness/`, `.codex/skills/`, split directories, or verifier commands.

## Fixture Contract Matrix

### Data Normalization

| Split | Task | Hardened Contract |
|---|---|---|
| train | `active_skus` | Accept `sku` or nested `product.sku`; active tokens are `active`, `enabled`, `1`, or `True`; skip blank/missing SKUs; sort by normalized SKU with duplicate collapse. |
| train | `totals_by_customer` | Accept `customer_id`, `customer.id`, or `customer`; ignore cancelled/void statuses; parse numeric amounts from ints, floats, or numeric strings; missing/blank amount is 0; preserve first-seen canonical customer order. |
| train | `normalize_contacts` | Build exact schema with id, name, email, active; accept email aliases and nested contact info; active token map; merge duplicate ids by preferring active records and later nonblank fields; sort by id. |
| train | `normalize_flags` | Normalize keys from `key` or `name`; skip blank keys; explicit true/false token maps; unknown tokens are false; later rows override earlier rows for the same key. |
| train | `unique_tags` | Accept strings or dicts with `tag`/`label`; split comma-separated tag strings; normalize case/whitespace; skip blanks and non-values; preserve first-seen canonical order. |
| selection | `unique_emails` | Accept strings or dicts with `email`, `mail`, or nested `contact.email`; lowercase/trim; skip blanks and invalid emails without `@`; preserve first-seen canonical order. |
| selection | `published_skus` | Accept `sku` or nested `product.sku`; published tokens are `published`, `live`, `1`, or `True`; skip blank SKUs and missing/unpublished status; sort by normalized SKU and collapse duplicates. |
| selection | `hours_by_employee` | Accept employee aliases; ignore rejected/void rows; parse numeric hours from numbers and numeric strings; missing/blank hours are 0; preserve first-seen employee order. |
| selection | `normalize_accounts` | Exact schema with id, owner, email, enabled; owner/email aliases; enabled token map; duplicate id conflict resolution prefers enabled records and later nonblank fields; sort by id. |
| selection | `subscription_flags` | Normalize plan from `plan`, `name`, or nested `subscription.plan`; skip blank plans; explicit true tokens; false for all other tokens; later rows override earlier rows. |
| test | `active_member_ids` | Accept member id aliases and nested ids; active tokens are `active`, `enabled`, `yes`, `1`, or `True`; skip blanks; sort canonical ids and collapse duplicates. |
| test | `totals_by_project` | Accept project aliases; ignore rejected/void rows; parse numeric amounts; missing/blank amount is 0; preserve first-seen project order. |
| test | `normalize_events` | Exact schema with id, title, kind, public; aliases/nested metadata; public token map; duplicate id resolution prefers public records and later nonblank fields; sort by id. |
| test | `preference_flags` | Normalize preference names from aliases; skip blanks; explicit on/enabled/yes/1/True tokens; false for all other tokens; later rows override earlier rows. |
| test | `unique_categories` | Accept strings or dict categories, split pipe/comma lists, normalize whitespace/case, skip blanks, preserve first-seen canonical order. |

### Code Repair

| Split | Task | Hardened Contract |
|---|---|---|
| train | `add_numbers` | Add numeric inputs after coercing numeric strings; reject booleans and nonnumeric strings with `TypeError`; do not mutate inputs. |
| train | `clamp` | Clamp with numeric coercion; support reversed bounds by normalizing low/high; preserve int result when all inputs are ints; reject nonnumeric values with `TypeError`. |
| train | `normalize_people` | Exact schema with id, name, active; aliases/nested fields; active token map; duplicate id resolution; no input mutation; sort by id. |
| train | `parse_duration` | Parse compact or spaced tokens with h/hr/hour, m/min/minute, s/sec/second; case-insensitive; reject duplicates, invalid units, negative values, and empty text. |
| train | `rank_labels` | Normalize labels by trimming/lowercasing; skip blanks; count canonical labels; sort by frequency then first-seen canonical order; handle limit <= 0; no input mutation. |
| selection | `merge_intervals` | Normalize reversed endpoints; merge overlapping or touching inclusive intervals; preserve no mutation; reject malformed intervals with `ValueError`; deterministic sorted output. |
| selection | `normalize_records` | Exact schema with id, name, active; aliases/nested fields; active token map; duplicate id conflict resolution; no input mutation; sort by id. |
| selection | `parse_duration` | Same parser family as train with different visible cases; include punctuation/commas and unit aliases; reject invalid/duplicate tokens. |
| selection | `parse_query` | Parse optional leading `?`; percent decode keys/values; `+` becomes space; keys without `=` map to empty string; repeated keys collect lists; blank key is skipped; no external deps. |
| selection | `top_k_frequent` | Normalize hashable values through string trim/lowercase for strings; skip blank strings; preserve original canonical value type for non-strings; tie by first-seen canonical order; no mutation. |
| test | `factorial` | Support non-negative integers and integer strings; reject booleans, negatives, and non-integers with `ValueError`; iterative implementation avoids recursion limits for moderate inputs. |
| test | `is_even` | Support ints and integer strings with whitespace/sign; reject booleans and non-integer strings with `TypeError`; handle negative values and zero. |
| test | `is_palindrome` | Case-insensitive alphanumeric palindrome check; ignore spaces and punctuation; empty normalized string is true; reject non-strings with `TypeError`. |
| test | `safe_divide` | Coerce numeric strings; return `None` for zero denominator or invalid numeric input; preserve float quotient; reject booleans by returning `None`. |
| test | `unique_items` | Remove duplicates by canonical key; strings trim/lowercase and blanks skipped; unhashable lists/dicts supported by structural canonicalization; preserve first-seen output representation; no mutation. |

---

### Task 1: Harden Data Normalization Train Fixtures

**Files:**
- Modify: `fixtures/data_normalization/train/active_skus/task.json`
- Modify: `fixtures/data_normalization/train/active_skus/tests_visible/test_inventory_visible.py`
- Modify: `fixtures/data_normalization/train/active_skus/tests_hidden/test_inventory_hidden.py`
- Modify: `fixtures/data_normalization/train/group_orders/task.json`
- Modify: `fixtures/data_normalization/train/group_orders/tests_visible/test_orders_visible.py`
- Modify: `fixtures/data_normalization/train/group_orders/tests_hidden/test_orders_hidden.py`
- Modify: `fixtures/data_normalization/train/normalize_contacts/task.json`
- Modify: `fixtures/data_normalization/train/normalize_contacts/tests_visible/test_contacts_visible.py`
- Modify: `fixtures/data_normalization/train/normalize_contacts/tests_hidden/test_contacts_hidden.py`
- Modify: `fixtures/data_normalization/train/parse_flags/task.json`
- Modify: `fixtures/data_normalization/train/parse_flags/tests_visible/test_flags_visible.py`
- Modify: `fixtures/data_normalization/train/parse_flags/tests_hidden/test_flags_hidden.py`
- Modify: `fixtures/data_normalization/train/unique_tags/task.json`
- Modify: `fixtures/data_normalization/train/unique_tags/tests_visible/test_tags_visible.py`
- Modify: `fixtures/data_normalization/train/unique_tags/tests_hidden/test_tags_hidden.py`

- [ ] **Step 1: Replace train task descriptions**

Use the contracts in the Data Normalization matrix for the five train tasks. Keep the existing ids and entrypoints unchanged. Example for `active_skus`:

```json
{
  "id": "data-train-active-skus",
  "description": "Repair active_skus so it returns unique active item SKUs sorted by normalized sku. Read the sku from sku or product.sku, trim it, skip blanks, and compare status case-insensitively. Active status tokens are 'active', 'enabled', '1', and True; missing or blank status is inactive.",
  "entrypoint": "inventory.py"
}
```

- [ ] **Step 2: Replace visible train tests with representative hard cases**

Use one visible test per task that demonstrates the main new behavior. Example for `active_skus`:

```python
from inventory import active_skus


def test_active_skus_accepts_nested_status_tokens_and_sorts_unique_skus():
    assert active_skus(
        [
            {"product": {"sku": " b-2 "}, "status": "ENABLED"},
            {"sku": "a-1", "status": "inactive"},
            {"sku": " c-3 ", "status": True},
            {"sku": "b-2", "status": "active"},
            {"product": {"sku": " "}, "status": "active"},
        ]
    ) == ["b-2", "c-3"]
```

- [ ] **Step 3: Replace hidden train tests with edge cases**

Add hidden tests for malformed rows, aliases, defaults, duplicate conflict resolution, and ordering. Example for `normalize_flags`:

```python
from flags import normalize_flags


def test_blank_keys_are_skipped_and_later_rows_override():
    assert normalize_flags(
        [
            {"name": " Beta ", "value": "yes"},
            {"key": "beta", "value": "off"},
            {"key": " ", "value": "yes"},
            {"name": "Internal", "value": None},
        ]
    ) == {"beta": False, "internal": False}
```

- [ ] **Step 4: Run focused fixture syntax checks**

Run:

```bash
uv run pytest fixtures/data_normalization/train -q
```

Expected: tests fail against weak starter implementations, but import and syntax errors should not occur. If a test file has syntax/import errors, fix the test file.

### Task 2: Harden Data Normalization Selection Fixtures

**Files:**
- Modify: `fixtures/data_normalization/selection/dedupe_emails/task.json`
- Modify: `fixtures/data_normalization/selection/dedupe_emails/tests_visible/test_emails_visible.py`
- Modify: `fixtures/data_normalization/selection/dedupe_emails/tests_hidden/test_emails_hidden.py`
- Modify: `fixtures/data_normalization/selection/filter_products/task.json`
- Modify: `fixtures/data_normalization/selection/filter_products/tests_visible/test_products_visible.py`
- Modify: `fixtures/data_normalization/selection/filter_products/tests_hidden/test_products_hidden.py`
- Modify: `fixtures/data_normalization/selection/group_timesheets/task.json`
- Modify: `fixtures/data_normalization/selection/group_timesheets/tests_visible/test_timesheets_visible.py`
- Modify: `fixtures/data_normalization/selection/group_timesheets/tests_hidden/test_timesheets_hidden.py`
- Modify: `fixtures/data_normalization/selection/normalize_accounts/task.json`
- Modify: `fixtures/data_normalization/selection/normalize_accounts/tests_visible/test_accounts_visible.py`
- Modify: `fixtures/data_normalization/selection/normalize_accounts/tests_hidden/test_accounts_hidden.py`
- Modify: `fixtures/data_normalization/selection/parse_subscriptions/task.json`
- Modify: `fixtures/data_normalization/selection/parse_subscriptions/tests_visible/test_subscriptions_visible.py`
- Modify: `fixtures/data_normalization/selection/parse_subscriptions/tests_hidden/test_subscriptions_hidden.py`

- [ ] **Step 1: Replace selection task descriptions**

Use the selection contracts in the Data Normalization matrix. Keep ids and entrypoints unchanged. Example for `subscription_flags`:

```json
{
  "id": "data-selection-parse-subscriptions",
  "description": "Repair subscription_flags so it returns a dict from normalized plan names to booleans. Read the plan from plan, name, or subscription.plan, trim and lowercase it, and skip blank plans. Values 'enabled', 'yes', '1', and True mean True; every other value, missing value, blank string, and None means False. Later rows override earlier rows for the same normalized plan.",
  "entrypoint": "subscriptions.py"
}
```

- [ ] **Step 2: Replace visible selection tests**

Use representative recombinations of train motifs. Example for `unique_emails`:

```python
from emails import unique_emails


def test_unique_emails_accepts_aliases_and_keeps_first_seen_order():
    assert unique_emails(
        [
            {"mail": " A@EXAMPLE.COM "},
            {"contact": {"email": "b@example.com"}},
            "a@example.com",
            {"email": "not-an-email"},
            " ",
        ]
    ) == ["a@example.com", "b@example.com"]
```

- [ ] **Step 3: Replace hidden selection tests**

Hidden tests should catch overfitting to field names and visible examples. Example for `hours_by_employee`:

```python
from timesheets import hours_by_employee


def test_aliases_numeric_strings_and_rejected_rows():
    assert hours_by_employee(
        [
            {"employee": {"id": "e2"}, "hours": "1.5"},
            {"employee_id": "e1", "hours": ""},
            {"employee": "e2", "hours": 2, "status": "VOID"},
            {"employee": "e2", "hours": "2.25"},
        ]
    ) == {"e2": 3.75, "e1": 0}
```

- [ ] **Step 4: Run focused selection syntax checks**

Run:

```bash
uv run pytest fixtures/data_normalization/selection -q
```

Expected: tests fail against weak starter implementations, but import and syntax errors should not occur.

### Task 3: Harden Data Normalization Test Fixtures

**Files:**
- Modify: `fixtures/data_normalization/test/filter_members/task.json`
- Modify: `fixtures/data_normalization/test/filter_members/tests_visible/test_members_visible.py`
- Modify: `fixtures/data_normalization/test/filter_members/tests_hidden/test_members_hidden.py`
- Modify: `fixtures/data_normalization/test/group_expenses/task.json`
- Modify: `fixtures/data_normalization/test/group_expenses/tests_visible/test_expenses_visible.py`
- Modify: `fixtures/data_normalization/test/group_expenses/tests_hidden/test_expenses_hidden.py`
- Modify: `fixtures/data_normalization/test/normalize_events/task.json`
- Modify: `fixtures/data_normalization/test/normalize_events/tests_visible/test_events_visible.py`
- Modify: `fixtures/data_normalization/test/normalize_events/tests_hidden/test_events_hidden.py`
- Modify: `fixtures/data_normalization/test/parse_preferences/task.json`
- Modify: `fixtures/data_normalization/test/parse_preferences/tests_visible/test_preferences_visible.py`
- Modify: `fixtures/data_normalization/test/parse_preferences/tests_hidden/test_preferences_hidden.py`
- Modify: `fixtures/data_normalization/test/stable_categories/task.json`
- Modify: `fixtures/data_normalization/test/stable_categories/tests_visible/test_categories_visible.py`
- Modify: `fixtures/data_normalization/test/stable_categories/tests_hidden/test_categories_hidden.py`

- [ ] **Step 1: Replace test split task descriptions**

Use the test contracts in the Data Normalization matrix. Keep ids and entrypoints unchanged. Example for `normalize_events`:

```json
{
  "id": "data-test-normalize-events",
  "description": "Repair normalize_events so it returns events sorted by id with exact output fields id, title, kind, and public. Read title/kind from top-level fields or metadata aliases, trim title and kind, title-case title, lowercase kind, and default missing public to False. Public tokens 'public', 'yes', '1', and True mean True. Merge duplicate ids by preferring public records and later nonblank title/kind values.",
  "entrypoint": "events.py"
}
```

- [ ] **Step 2: Replace visible test split tests**

Visible tests should use novel domains while showing the main behavior. Example for `unique_categories`:

```python
from categories import unique_categories


def test_unique_categories_splits_lists_and_keeps_first_seen_order():
    assert unique_categories(
        [
            " Support | Sales ",
            {"category": "support"},
            {"label": " Finance, sales "},
            "",
        ]
    ) == ["support", "sales", "finance"]
```

- [ ] **Step 3: Replace hidden test split tests**

Hidden tests should be stricter than train and selection and verify exact schemas, duplicate resolution, and malformed-row behavior. Example for `active_member_ids`:

```python
from members import active_member_ids


def test_aliases_duplicates_and_blank_ids_are_handled():
    assert active_member_ids(
        [
            {"member": {"id": " m2 "}, "status": "yes"},
            {"member_id": "m1", "status": "disabled"},
            {"id": "m2", "status": True},
            {"id": " ", "status": "active"},
            {"member": {"id": "m0"}, "status": "1"},
        ]
    ) == ["m0", "m2"]
```

- [ ] **Step 4: Run focused test-split syntax checks**

Run:

```bash
uv run pytest fixtures/data_normalization/test -q
```

Expected: tests fail against weak starter implementations, but import and syntax errors should not occur.

### Task 4: Harden Code Repair Train Fixtures

**Files:**
- Modify: `fixtures/code_repair/train/addition_bug/task.json`
- Modify: `fixtures/code_repair/train/addition_bug/tests_visible/test_calculator_visible.py`
- Modify: `fixtures/code_repair/train/addition_bug/tests_hidden/test_calculator_hidden.py`
- Modify: `fixtures/code_repair/train/clamp_bug/task.json`
- Modify: `fixtures/code_repair/train/clamp_bug/tests_visible/test_bounds_visible.py`
- Modify: `fixtures/code_repair/train/clamp_bug/tests_hidden/test_bounds_hidden.py`
- Modify: `fixtures/code_repair/train/normalize_people/task.json`
- Modify: `fixtures/code_repair/train/normalize_people/tests_visible/test_people_visible.py`
- Modify: `fixtures/code_repair/train/normalize_people/tests_hidden/test_people_hidden.py`
- Modify: `fixtures/code_repair/train/parse_duration/task.json`
- Modify: `fixtures/code_repair/train/parse_duration/tests_visible/test_duration_visible.py`
- Modify: `fixtures/code_repair/train/parse_duration/tests_hidden/test_duration_hidden.py`
- Modify: `fixtures/code_repair/train/stable_frequency/task.json`
- Modify: `fixtures/code_repair/train/stable_frequency/tests_visible/test_frequency_visible.py`
- Modify: `fixtures/code_repair/train/stable_frequency/tests_hidden/test_frequency_hidden.py`

- [ ] **Step 1: Replace code-repair train descriptions**

Use the Code Repair train contracts in the matrix. Keep ids and entrypoints unchanged. Example for `parse_duration`:

```json
{
  "id": "train-parse-duration",
  "description": "Repair parse_duration so it converts duration text to seconds. Accept compact or spaced non-negative integer tokens with h/hr/hour, m/min/minute, and s/sec/second units case-insensitively. Reject empty text, duplicate units, negative values, malformed tokens, and unknown units with ValueError.",
  "entrypoint": "duration.py"
}
```

- [ ] **Step 2: Replace visible code-repair train tests**

Visible tests should show one representative edge contract per task. Example for `rank_labels`:

```python
from frequency import rank_labels


def test_rank_labels_normalizes_counts_and_preserves_first_seen_ties():
    labels = [" Red ", "blue", "red", "", "BLUE", "green"]
    assert rank_labels(labels, 3) == ["red", "blue", "green"]
    assert labels == [" Red ", "blue", "red", "", "BLUE", "green"]
```

- [ ] **Step 3: Replace hidden code-repair train tests**

Hidden tests should cover TypeError/ValueError behavior, no mutation, and boundary values. Example for `clamp`:

```python
import pytest

from bounds import clamp


def test_reversed_bounds_numeric_strings_and_invalid_values():
    assert clamp("5", "10", "0") == 5
    assert clamp("-2", "10", "0") == 0
    with pytest.raises(TypeError):
        clamp("five", 0, 10)
```

- [ ] **Step 4: Run focused code-repair train syntax checks**

Run:

```bash
uv run pytest fixtures/code_repair/train -q
```

Expected: tests fail against weak starter implementations, but import and syntax errors should not occur.

### Task 5: Harden Code Repair Selection Fixtures

**Files:**
- Modify: `fixtures/code_repair/selection/merge_intervals/task.json`
- Modify: `fixtures/code_repair/selection/merge_intervals/tests_visible/test_intervals_visible.py`
- Modify: `fixtures/code_repair/selection/merge_intervals/tests_hidden/test_intervals_hidden.py`
- Modify: `fixtures/code_repair/selection/normalize_records/task.json`
- Modify: `fixtures/code_repair/selection/normalize_records/tests_visible/test_records_visible.py`
- Modify: `fixtures/code_repair/selection/normalize_records/tests_hidden/test_records_hidden.py`
- Modify: `fixtures/code_repair/selection/parse_duration/task.json`
- Modify: `fixtures/code_repair/selection/parse_duration/tests_visible/test_duration_visible.py`
- Modify: `fixtures/code_repair/selection/parse_duration/tests_hidden/test_duration_hidden.py`
- Modify: `fixtures/code_repair/selection/tokenize_query/task.json`
- Modify: `fixtures/code_repair/selection/tokenize_query/tests_visible/test_query_visible.py`
- Modify: `fixtures/code_repair/selection/tokenize_query/tests_hidden/test_query_hidden.py`
- Modify: `fixtures/code_repair/selection/top_k_frequent/task.json`
- Modify: `fixtures/code_repair/selection/top_k_frequent/tests_visible/test_frequency_visible.py`
- Modify: `fixtures/code_repair/selection/top_k_frequent/tests_hidden/test_frequency_hidden.py`

- [ ] **Step 1: Replace code-repair selection descriptions**

Use the Code Repair selection contracts in the matrix. Keep ids and entrypoints unchanged. Example for `parse_query`:

```json
{
  "id": "selection-tokenize-query",
  "description": "Repair parse_query so it parses a URL query string into a dict. Accept an optional leading '?', decode percent escapes and '+', skip blank parts and blank keys, assign keys without '=' an empty string value, and collect repeated keys in first-seen value lists.",
  "entrypoint": "query.py"
}
```

- [ ] **Step 2: Replace visible code-repair selection tests**

Use visible tests that recombine train motifs with different function names. Example for `merge_intervals`:

```python
from intervals import merge_intervals


def test_reversed_touching_and_nested_intervals_merge_without_mutation():
    intervals = [[5, 3], [1, 2], [2, 4], [10, 12], [11, 11]]
    assert merge_intervals(intervals) == [[1, 5], [10, 12]]
    assert intervals == [[5, 3], [1, 2], [2, 4], [10, 12], [11, 11]]
```

- [ ] **Step 3: Replace hidden code-repair selection tests**

Hidden tests should catch missing parser errors, mutation, and tie-break instability. Example for `top_k_frequent`:

```python
from frequency import top_k_frequent


def test_normalizes_strings_skips_blanks_and_preserves_first_seen_ties():
    values = [" B ", "a", "b", "A", "", 3, 3, "3"]
    assert top_k_frequent(values, 4) == ["b", "a", 3, "3"]
    assert values == [" B ", "a", "b", "A", "", 3, 3, "3"]
```

- [ ] **Step 4: Run focused code-repair selection syntax checks**

Run:

```bash
uv run pytest fixtures/code_repair/selection -q
```

Expected: tests fail against weak starter implementations, but import and syntax errors should not occur.

### Task 6: Harden Code Repair Test Fixtures

**Files:**
- Modify: `fixtures/code_repair/test/factorial_bug/task.json`
- Modify: `fixtures/code_repair/test/factorial_bug/tests_visible/test_factorial_visible.py`
- Modify: `fixtures/code_repair/test/factorial_bug/tests_hidden/test_factorial_hidden.py`
- Modify: `fixtures/code_repair/test/is_even_bug/task.json`
- Modify: `fixtures/code_repair/test/is_even_bug/tests_visible/test_parity_visible.py`
- Modify: `fixtures/code_repair/test/is_even_bug/tests_hidden/test_parity_hidden.py`
- Modify: `fixtures/code_repair/test/palindrome_bug/task.json`
- Modify: `fixtures/code_repair/test/palindrome_bug/tests_visible/test_palindrome_visible.py`
- Modify: `fixtures/code_repair/test/palindrome_bug/tests_hidden/test_palindrome_hidden.py`
- Modify: `fixtures/code_repair/test/safe_divide_bug/task.json`
- Modify: `fixtures/code_repair/test/safe_divide_bug/tests_visible/test_division_visible.py`
- Modify: `fixtures/code_repair/test/safe_divide_bug/tests_hidden/test_division_hidden.py`
- Modify: `fixtures/code_repair/test/unique_items_bug/task.json`
- Modify: `fixtures/code_repair/test/unique_items_bug/tests_visible/test_unique_visible.py`
- Modify: `fixtures/code_repair/test/unique_items_bug/tests_hidden/test_unique_hidden.py`

- [ ] **Step 1: Replace code-repair test descriptions**

Use the Code Repair test contracts in the matrix. Keep ids and entrypoints unchanged. Example for `unique_items`:

```json
{
  "id": "test-unique-items-bug",
  "description": "Repair unique_items so it removes duplicates in first-seen order without mutating the input. String values are compared after trimming and lowercasing, blank strings are skipped, and unhashable lists or dicts are compared by structural value while preserving the first-seen output representation.",
  "entrypoint": "unique.py"
}
```

- [ ] **Step 2: Replace visible code-repair test split tests**

Use novel but fair visible examples. Example for `is_palindrome`:

```python
from palindrome import is_palindrome


def test_palindrome_ignores_case_spaces_and_punctuation():
    assert is_palindrome("A man, a plan, a canal: Panama!") is True
```

- [ ] **Step 3: Replace hidden code-repair test split tests**

Hidden tests should verify stricter edge behavior. Example for `factorial`:

```python
import pytest

from factorial import factorial


def test_integer_strings_zero_and_invalid_values():
    assert factorial("5") == 120
    assert factorial(0) == 1
    with pytest.raises(ValueError):
        factorial(-1)
    with pytest.raises(ValueError):
        factorial(True)
```

- [ ] **Step 4: Run focused code-repair test-split syntax checks**

Run:

```bash
uv run pytest fixtures/code_repair/test -q
```

Expected: tests fail against weak starter implementations, but import and syntax errors should not occur.

### Task 7: Verify Harness Invariants

**Files:**
- Test: `tests/test_fixtures.py`
- Test: `tests/test_cli.py`
- Read: `skillopt.yaml`

- [ ] **Step 1: Run repository tests**

Run:

```bash
uv run pytest
```

Expected: repository tests pass. Fixture task tests are not part of the repo testpaths, so failures inside weak fixture tasks should not fail this command.

- [ ] **Step 2: Run lint**

Run:

```bash
uv run ruff check .
```

Expected: all checks pass.

- [ ] **Step 3: Confirm fixture layout still satisfies harness expectations**

Run:

```bash
uv run skillopt-harness list-tasks --track data_normalization --split train
uv run skillopt-harness list-tasks --track data_normalization --split selection
uv run skillopt-harness list-tasks --track data_normalization --split test
uv run skillopt-harness list-tasks --track code_repair --split train
uv run skillopt-harness list-tasks --track code_repair --split selection
uv run skillopt-harness list-tasks --track code_repair --split test
```

Expected: each command lists five tasks, ids are unchanged, and descriptions reflect the hardened contracts.

- [ ] **Step 4: Confirm prepared workspaces still hide hidden tests**

Run:

```bash
uv run skillopt-harness prepare-task --track data_normalization --task data-train-active-skus --split train --output workspaces/fixture-hardening-check/data-train-active-skus
uv run skillopt-harness prepare-task --track code_repair --task train-parse-duration --split train --output workspaces/fixture-hardening-check/train-parse-duration
```

Expected: both prepared workspaces contain `tests_visible` and do not contain `tests_hidden`.

- [ ] **Step 5: Grade every fixture task after writing reference repairs in temporary prepared workspaces**

Prepare all tasks into deterministic workspace paths with this script:

```bash
python3 - <<'PY'
import subprocess

tasks = {
    "data_normalization": {
        "train": [
            "data-train-active-skus",
            "data-train-group-orders",
            "data-train-normalize-contacts",
            "data-train-parse-flags",
            "data-train-unique-tags",
        ],
        "selection": [
            "data-selection-dedupe-emails",
            "data-selection-filter-products",
            "data-selection-group-timesheets",
            "data-selection-normalize-accounts",
            "data-selection-parse-subscriptions",
        ],
        "test": [
            "data-test-filter-members",
            "data-test-group-expenses",
            "data-test-normalize-events",
            "data-test-parse-preferences",
            "data-test-stable-categories",
        ],
    },
    "code_repair": {
        "train": [
            "train-addition-bug",
            "train-clamp-bug",
            "train-normalize-people",
            "train-parse-duration",
            "train-stable-frequency",
        ],
        "selection": [
            "selection-merge-intervals",
            "selection-normalize-records",
            "selection-parse-duration",
            "selection-tokenize-query",
            "selection-top-k-frequent",
        ],
        "test": [
            "test-factorial-bug",
            "test-is-even-bug",
            "test-palindrome-bug",
            "test-safe-divide-bug",
            "test-unique-items-bug",
        ],
    },
}

for track, splits in tasks.items():
    for split, ids in splits.items():
        for task_id in ids:
            output = f"workspaces/fixture-hardening-grade/{track}/{split}/{task_id}"
            subprocess.run(
                [
                    "uv",
                    "run",
                    "skillopt-harness",
                    "prepare-task",
                    "--track",
                    track,
                    "--task",
                    task_id,
                    "--split",
                    split,
                    "--output",
                    output,
                ],
                check=True,
            )
PY
```

After manually repairing each prepared workspace according to its task contract, grade all prepared workspaces with this script:

```bash
python3 - <<'PY'
import subprocess
from pathlib import Path

tasks = {
    "data_normalization": {
        "train": [
            "data-train-active-skus",
            "data-train-group-orders",
            "data-train-normalize-contacts",
            "data-train-parse-flags",
            "data-train-unique-tags",
        ],
        "selection": [
            "data-selection-dedupe-emails",
            "data-selection-filter-products",
            "data-selection-group-timesheets",
            "data-selection-normalize-accounts",
            "data-selection-parse-subscriptions",
        ],
        "test": [
            "data-test-filter-members",
            "data-test-group-expenses",
            "data-test-normalize-events",
            "data-test-parse-preferences",
            "data-test-stable-categories",
        ],
    },
    "code_repair": {
        "train": [
            "train-addition-bug",
            "train-clamp-bug",
            "train-normalize-people",
            "train-parse-duration",
            "train-stable-frequency",
        ],
        "selection": [
            "selection-merge-intervals",
            "selection-normalize-records",
            "selection-parse-duration",
            "selection-tokenize-query",
            "selection-top-k-frequent",
        ],
        "test": [
            "test-factorial-bug",
            "test-is-even-bug",
            "test-palindrome-bug",
            "test-safe-divide-bug",
            "test-unique-items-bug",
        ],
    },
}

Path("runs/fixture-hardening-grade.jsonl").unlink(missing_ok=True)
for track, splits in tasks.items():
    for split, ids in splits.items():
        for task_id in ids:
            workspace = f"workspaces/fixture-hardening-grade/{track}/{split}/{task_id}"
            subprocess.run(
                [
                    "uv",
                    "run",
                    "skillopt-harness",
                    "grade-task",
                    "--track",
                    track,
                    "--workspace",
                    workspace,
                    "--output",
                    "runs/fixture-hardening-grade.jsonl",
                    "--redact-output",
                ],
                check=True,
            )
PY
```

Expected: every repaired workspace receives score `1.0`. Do not edit fixture originals while doing these reference repairs.

## Self-Review Notes

- Spec coverage: both tracks and all splits are covered; task count and split assignment stay fixed; harness/verifier/deployable skill files are excluded.
- Placeholder scan: no placeholder markers are used.
- Type consistency: all function names, ids, and entrypoint filenames match the current fixtures.
