"""
 GROUP 8 : SACCO ACCOUNT WITHDRAWAL AND TRANSFER SIMULATOR
 Programming Languages Lab - Names, Bindings and Scopes
 Language: Python 3
"""
# [Named constant] MIN_BALANCE is bound once, at module load time,
# and is never reassigned. It replaces the "magic number" 500 everywhere
# a minimum-balance check is required.

MIN_BALANCE = 500          # training minimum balance every account must keep
CURRENCY = "KES"           # named constant used only for display formatting


# [CONCEPT: Global scope] institutionCode is bound in the module (global)
# scope. It is used unmodified inside report_header(), but deliberately
# SHADOWED inside report_body() by a local variable of the same name.

institutionCode = "SACCO-KE-001"


class Account:
    """A SACCO member account record."""

    def __init__(self, acc_no, member_name, balance, active=True):
        # These four are the account's core attributes: name, address(id),
        # value(balance), and an active/eligibility flag.
        self.acc_no = acc_no
        self.member_name = member_name
        self.balance = balance
        self.active = active

    def __repr__(self):
        status = "ACTIVE" if self.active else "INACTIVE"
        return (f"[{self.acc_no}] {self.member_name:<15} "
                f"Balance: {CURRENCY} {self.balance:>10,.2f}  ({status})")


class TransactionResult:
    """Simple record describing whether a transaction was approved."""

    def __init__(self, success, message):
        self.success = success
        self.message = message

    def __repr__(self):
        tag = "OK" if self.success else "REJECTED"
        return f"{tag}: {self.message}"


# A. TRANSACTION ENGINE

def deposit(account, amount):
    """
    Deposit money into `account`.
    `account` is a name bound to the SAME Account object the caller holds
    (Python passes object references) -- this is the alias relationship
    explored further in Task B.
    """
    if amount <= 0:
        return TransactionResult(False, "Deposit amount must be positive")
    if not account.active:
        return TransactionResult(False, "Cannot deposit into an inactive account")

    account.balance = account.balance + amount   # [CONCEPT] see l-value/r-value note (Task E)
    return TransactionResult(True, f"Deposited {CURRENCY} {amount:,.2f}")


def validate_withdrawal(account, amount):
    """ function-local scope
    `approved` and `reason` are declared only inside this function. Python
    has no separate block scope for if/else (unlike C++ braces), so both
    names are visible for the rest of THIS function once assigned, but
    they do not exist at all outside validate_withdrawal(). This is
    demonstrated by the deliberate out-of-scope access attempt below the
    function definition.
    """
    if amount <= 0:
        approved = False
        reason = "Withdrawal amount must be positive"
    elif not account.active:
        approved = False
        reason = "Account is inactive"
    elif account.balance - amount < MIN_BALANCE:
        approved = False
        reason = f"Would breach minimum balance of {CURRENCY} {MIN_BALANCE}"
    else:
        approved = True
        reason = "Validated"
    return approved, reason


def withdraw(account, amount):
    approved, reason = validate_withdrawal(account, amount)
    if not approved:
        return TransactionResult(False, reason)

    account.balance = account.balance - amount    # [CONCEPT] l-value/r-value, Task E
    return TransactionResult(True, f"Withdrew {CURRENCY} {amount:,.2f}")


def transfer(from_account, to_account, amount):
    """ aliasing
    `from_account` and `to_account` are new local names, but they are bound
    to the SAME two Account objects the caller passed in (their object ids
    are identical -- proven with id() in main()). Any mutation made here
    through from_account/to_account is therefore visible to the caller
    through its own names for the same accounts: the parameters and the
    caller's variables are ALIASES of one another.The transfer is treated
    as atomic in this simulation: withdrawal is validated BEFORE any
    balance is changed, so either both balances move or neither does.
    """
    if from_account.acc_no == to_account.acc_no:
        return TransactionResult(False, "Cannot transfer to the same account")

    approved, reason = validate_withdrawal(from_account, amount)
    if not approved:
        return TransactionResult(False, f"Transfer blocked: {reason}")
    if not to_account.active:
        return TransactionResult(False, "Transfer blocked: destination account inactive")

    from_account.balance = from_account.balance - amount
    to_account.balance = to_account.balance + amount
    return TransactionResult(
        True,
        f"Transferred {CURRENCY} {amount:,.2f} from {from_account.acc_no} to {to_account.acc_no}"
    )

# D. STORAGE AND LIFETIME

def process_transaction(kind, *args):
    """ "Static" local variable 
    Python has no `static` keyword, so the nearest equivalent is a function
    attribute: process_transaction.counter is created ONCE (initialised
    just below the function) and every call updates the same storage cell.
    Its SCOPE is still just this function (it is not a global name that
    other functions can see directly), but its LIFETIME spans the entire
    life of the program, exactly like a static local variable in C/C++.
    """
    if kind == "deposit":
        result = deposit(*args)
    elif kind == "withdraw":
        result = withdraw(*args)
    elif kind == "transfer":
        result = transfer(*args)
    else:
        result = TransactionResult(False, f"Unknown transaction type '{kind}'")

    process_transaction.counter += 1
    return result


process_transaction.counter = 0   # storage allocated once, at module load time


def make_temporary_receipt_number(account):
    """Ordinary local variable, stack-like lifetime
   Every time the function runs, it makes a new serial value. As soon as the function 
   finishes, that value disappears because nothing outside is holding onto it. Python 
   quickly cleans it up. By contrast, the Account objects created in main() stay around
     for the whole program since they’re stored in the accounts list.
    """
    serial = f"RCPT-{account.acc_no}-{process_transaction.counter:04d}"
    return serial

# C. GLOBAL / LOCAL SCOPE EXPERIMENT (shadowing)

def report_header():
    """Uses the GLOBAL institutionCode (no local variable of that name here)."""
    global institutionCode
    print(f"--- {institutionCode} : OFFICIAL TRANSACTION REPORT ---")


def report_body():
    """Shadowing
    In this function, we create a local variable called institutionCode. Even though 
    there’s  a global variable with the same name, the local one takes priority 
    inside the function. That means when the function runs, it only “sees” the local 
    value, while the global version still exists but is hidden in the background.
    """
    institutionCode = "BR-NAIROBI-01"   # local name hides the global
    print(f"[Inside report_body - local ] institutionCode = {institutionCode}")
    print(f"[Inside report_body - global] institutionCode = {globals()['institutionCode']}")


def scope_experiment():
    print("\n=== C. GLOBAL/LOCAL SCOPE + SHADOWING EXPERIMENT ===")
    report_header()
    report_body()
    print(f"[Back in module/global scope] institutionCode = {institutionCode}")

    # Demonstrate the block-local variable `approved` from validate_withdrawal
    # cannot be reached from outside that function.
    try:
        print(approved)          # noqa: F821  (intentional NameError demo)
    except NameError as e:
        print(f"Out-of-scope access attempt correctly failed -> {e}")

# E. OUTPUT AND REASONING HELPERS

def print_statement(account):
    print(account)


def print_final_table(accounts):
    print("\n--- FINAL ACCOUNT BALANCE TABLE ---")
    for acc in accounts:
        print_statement(acc)


def explain_lvalue_rvalue():
    print("\n=== E. L-VALUE / R-VALUE REASONING ===")
    print("Statement analysed: balance = balance - amount")
    print("  - On the LEFT of '=', 'balance' is used as an l-value: it names")
    print("    the STORAGE LOCATION (the attribute slot on the Account object)")
    print("    that will receive a new value.")
    print("  - On the RIGHT of '=', the SAME name 'balance' is used as an")
    print("    r-value: Python first reads its CURRENT value from that")
    print("    storage location before the subtraction is evaluated.")
    print("  - So one identifier plays both roles in a single statement:")
    print("    r-value read happens first, then the l-value write commits")
    print("    the result back into the same memory cell.")

# MAIN DEMO / TEST DATA

def main():
    print("=" * 78)
    print(" SACCO ACCOUNT WITHDRAWAL AND TRANSFER SIMULATOR - GROUP 8 ")
    print("=" * 78)

    
    # Dynamic allocation
    # Every Account below is created at RUN TIME with Account(...), the
    # Python equivalent of heap allocation. They are kept alive for the
    # whole program because the `accounts` list still references them.
    
    accounts = [
        Account("ACC001", "Wanjiru Kamau", 5000.00),
        Account("ACC002", "Otieno Owino", 1200.00),
        Account("ACC003", "Chebet Nyambura", 800.00),
        Account("ACC004", "Mwangi Kiptoo", 3000.00),
        Account("ACC005", "Achieng Njeri", 2500.00, active=False),   # inactive on purpose
    ]

    by_no = {acc.acc_no: acc for acc in accounts}

    print("\n--- A. INITIAL ACCOUNT TABLE ---")
    print_final_table(accounts)

    # -------------------- TEST RUNS (successful) ----------------------
    print("\n=== SUCCESSFUL TEST RUN 1: Deposit ===")
    r1 = process_transaction("deposit", by_no["ACC001"], 1500.00)
    print(r1)

    print("\n=== SUCCESSFUL TEST RUN 2: Withdrawal within limits ===")
    r2 = process_transaction("withdraw", by_no["ACC002"], 500.00)
    print(r2)

    print("\n=== SUCCESSFUL TEST RUN 3: Transfer between two active accounts ===")
    # ---- B. ALIAS PROOF ----
    from_acc = by_no["ACC004"]
    to_acc = by_no["ACC002"]
    print(f"id(from_acc) before call = {id(from_acc)}  (ACC004 object)")
    print(f"id(to_acc)   before call = {id(to_acc)}  (ACC002 object)")
    print("Balances BEFORE transfer:")
    print_statement(from_acc)
    print_statement(to_acc)

    r3 = process_transaction("transfer", from_acc, to_acc, 1000.00)
    print(r3)

    print("Balances AFTER transfer (same objects, mutated through the "
          "from_account/to_account aliases inside transfer()):")
    print_statement(from_acc)
    print_statement(to_acc)
    print("--> from_acc and to_acc, and the from_account/to_account parameters\n"
          "    used inside transfer(), refer to the identical objects in memory\n"
          "    (see matching id() values below), which is the definition of an alias.")
    print(f"id(from_acc) after call  = {id(from_acc)}")
    print(f"id(to_acc)   after call  = {id(to_acc)}")

    # More transactions to satisfy the 10-transaction minimum
    print("\n=== More transactions (5 - 10) ===")
    print(process_transaction("deposit", by_no["ACC003"], 200.00))
    print(process_transaction("withdraw", by_no["ACC001"], 2000.00))
    print(process_transaction("deposit", by_no["ACC005"], 100.00))   # will fail: inactive
    print(process_transaction("transfer", by_no["ACC001"], by_no["ACC003"], 300.00))
    print(process_transaction("deposit", by_no["ACC002"], 50.00))
    print(process_transaction("withdraw", by_no["ACC004"], 100.00))

    # -------------------- TEST RUNS (boundary / error cases) ------------
    print("\n=== BOUNDARY/ERROR TEST RUN 1: Negative amount rejected ===")
    print(process_transaction("deposit", by_no["ACC002"], -50.00))

    print("\n=== BOUNDARY/ERROR TEST RUN 2: Withdrawal breaching MIN_BALANCE ===")
    print(process_transaction("withdraw", by_no["ACC003"], 900.00))

    print("\n=== BOUNDARY/ERROR TEST RUN 3: Transfer involving inactive account ===")
    print(process_transaction("transfer", by_no["ACC005"], by_no["ACC001"], 100.00))

    print("\n=== BOUNDARY/ERROR TEST RUN 4: Unknown account number ===")
    try:
        target = by_no["ACC999"]
    except KeyError as e:
        print(f"REJECTED: unknown account number {e}")

    # ---- C. Scope / shadowing experiment ----
    scope_experiment()

    # ---- D. lifetime note ----
    print("\n=== D. STORAGE AND LIFETIME NOTE ===")
    receipt_no = make_temporary_receipt_number(by_no["ACC001"])
    print(f"Temporary receipt id generated and already usable: {receipt_no}")
    print("(the local variable 'serial' inside make_temporary_receipt_number "
          "has already gone out of scope and been reclaimed by this point)")
    print(f"process_transaction.counter (static-style, program-lifetime) = "
          f"{process_transaction.counter}")

    # ---- E. l-value / r-value discussion ----
    explain_lvalue_rvalue()

    # ---- Final report ----
    print_final_table(accounts)
    failed = sum(1 for acc in accounts if not acc.active)
    print(f"\nTotal transactions processed (static counter): {process_transaction.counter}")
    print(f"Accounts currently inactive: {failed}")


if __name__ == "__main__":
    main()
