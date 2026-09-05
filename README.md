# Marketplace Order Processing — Coroutine Simulation

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
