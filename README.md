| Name | Registration Number |
|Tatiannah Mbula|C026-01-2697/2025|
| Tabitha Mungai |C026-01-0900/2025  |
|  Joyann Ndiritu|C026-01-0897/2026  |


#     task 1. SACCO Account Withdrawal and Transfer Simulator — Group 8

A classroom simulator for a SACCO (savings and credit cooperative) that handles
deposits, withdrawals, and transfers between member accounts, built to make
several **names, bindings, and scopes** concepts from the Programming
Languages Lab observable in a running program.

> ⚠️ Training exercise only. `MIN_BALANCE` and `CURRENCY` are fictional
> classroom values, not real SACCO policy.

---

## Requirements

- Python 3.6 or newer (uses f-strings; no external packages required)

## How to run

```bash
python3 sacco_simulator_main.py
```

No arguments or setup needed — `main()` builds its own test data (5 accounts,
12 transactions including 4 deliberate boundary/error cases) and prints a
full walkthrough to the console.

---

## What the program does

1. Builds 5 `Account` records (one deliberately `INACTIVE`).
2. Runs deposits, withdrawals, and transfers through `process_transaction()`.
3. Demonstrates aliasing by transferring funds between two accounts and
   printing `id()` before/after to prove the same objects were mutated.
4. Runs a global/local **shadowing** experiment (`institutionCode`).
5. Runs 4 boundary/error cases (negative amount, breached minimum balance,
   inactive account, unknown account number).
6. Prints a final balance table and transaction summary.

---

## Code structure

| Section | Functions | Purpose |
|---|---|---|
| Constants & globals | `MIN_BALANCE`, `CURRENCY`, `institutionCode` | Named constants + one global used later for the shadowing demo |
| Data model | `Account`, `TransactionResult` | Account record and a pass/fail result wrapper |
| A. Transaction engine | `deposit`, `validate_withdrawal`, `withdraw`, `transfer` | Core business logic and validation |
| D. Storage/lifetime | `process_transaction`, `make_temporary_receipt_number` | Dispatcher with a "static-style" counter; a short-lived local variable |
| C. Scope experiment | `report_header`, `report_body`, `scope_experiment` | Global vs. shadowed local name; an intentional out-of-scope access |
| E. Output/reasoning | `print_statement`, `print_final_table`, `explain_lvalue_rvalue` | Reporting and an l-value/r-value walkthrough |
| Entry point | `main()` | Builds test data and drives every scenario above |

---

## Where each required concept appears

| Concept | Where | Explanation |
|---|---|---|
| **Named constants** | `MIN_BALANCE`, `CURRENCY` (top of file) | Bound once at module load; replace hard-coded literals used across `deposit`, `withdraw`, `transfer` |
| **Global scope** | `institutionCode` (module level) | Declared once at module scope, read unmodified in `report_header()` |
| **Shadowing** | `report_body()` | A local `institutionCode` hides the global one only inside that function; `globals()['institutionCode']` proves the global is untouched |
| **Function-local scope** | `validate_withdrawal()` | `approved` / `reason` exist only for the life of that call — `scope_experiment()` proves this by catching a `NameError` when accessing `approved` outside the function |
| **References / aliasing** | `transfer(from_account, to_account, amount)` | Parameters are bound to the *same* objects the caller passed (Python passes object references); `id()` calls in `main()` prove no copy was made |
| **Storage & lifetime — "static" equivalent** | `process_transaction.counter` | A function attribute created once at load time; its *scope* is limited to `process_transaction`, but its *lifetime* spans the whole program run — the closest Python equivalent to a C/C++ `static` local |
| **Ordinary local variable / stack-like lifetime** | `serial` in `make_temporary_receipt_number()` | Created fresh each call, discarded as soon as the function returns |
| **Dynamic allocation, run-time lifetime** | `accounts = [Account(...), ...]` in `main()` | Objects created at run time and kept alive for the whole program because `accounts` (and `by_no`) still reference them |
| **L-value / R-value** | `balance = balance - amount` (in `withdraw`/`transfer`) | Walked through explicitly in `explain_lvalue_rvalue()`: left side is the storage location being written, right side is a value read from that same location before the write commits |

---

## Test runs included

**Successful (7):** initial deposit, in-limit withdrawal, account-to-account
transfer (with alias/`id()` proof), plus 4 more mixed transactions.

**Boundary/error (4):**
1. Negative deposit amount → rejected
2. Withdrawal that would breach `MIN_BALANCE` → rejected
3. Transfer touching an inactive account → rejected
4. Lookup of an unknown account number → `KeyError` caught and reported

**Verified:** the script was run end-to-end and completes with no errors;
final state shows 12 transactions processed and 1 inactive account, matching
the console trace.

---

## Known limitations / notes for the concept report

- Python has no block scope (`if`/`else` don't create a new scope the way
  C++ braces do), so `approved`/`reason` are *function*-local, not
  *block*-local — worth stating explicitly if the brief expects a true
  block-scope example.
- `process_transaction.counter` is the closest Python idiom to a `static`
  local variable, but technically it's a function *attribute*, not a
  language-level static — worth noting the distinction in the viva.
- The "atomic" transfer is only atomic at the level of this single-threaded
  simulation (validate-before-mutate order); there's no real transaction
  rollback mechanism.


# task 2.Marketplace Order Processing — Coroutine Simulation

A small Lua simulation of order processing for a fictional Kenyan online
marketplace. Each order moves through six stages using a coroutine, and a
central scheduler runs several orders concurrently, interleaving their
progress.

## Order Pipeline

Every order passes through these stages, in order:

1. `validation`
2. `payment`
3. `warehouse_allocation`
4. `packaging`
5. `courier_assignment`
6. `dispatch`

## How It Works

- **Orders as coroutines** — each order is a Lua table holding its own
  persistent state (id, customer, current stage, status, log) plus a
  `coroutine` that walks it through the pipeline.
- **Yielding between stages** — after successfully completing a stage, the
  coroutine yields control back to the scheduler before starting the next
  one.
- **Cancellation** — if an order hits an "unrecoverable condition" at a
  given stage, it stops immediately and is marked `cancelled` (as opposed
  to a normal `failed` outcome).
- **Scheduler** — repeatedly resumes each order's coroutine in round-robin
  order until every order has finished, so all orders progress in an
  interleaved fashion rather than one after another.
- **Summary** — at the end, a full log is printed followed by a count of
  `completed`, `failed`, and `cancelled` orders.

## Running It

Requires a Lua interpreter (5.3 or 5.4).

```bash
lua orders.lua
```

## Sample Output

```
===== ORDER PROCESSING LOG =====
Order 1 (Customer1): completed stage 'validation'
...
Order 6 (Customer6): CANCELLED at stage 'validation' - unrecoverable condition

===== FINAL SUMMARY =====
Completed (2): 1, 4
Failed    (2): 2, 5
Cancelled (2): 3, 6
```

## Customizing Orders

Orders are created with `newOrder(id, options)`:

```lua
newOrder(1)                          -- runs through all stages successfully
newOrder(2, { failStage = 2 })       -- fails (normal failure) at stage 2
newOrder(3, { cancelStage = 3 })     -- cancelled (unrecoverable) at stage 3
```

The demo at the bottom of `orders.lua` creates six orders to demonstrate
completions, failures, and cancellations running concurrently.

## Files

- `orders.lua` — the full implementation and demo run.
