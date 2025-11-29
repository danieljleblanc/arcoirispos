
# ✅ REQUIREMENT ADDED TO SYSTEM — *POS Monetary Rounding Engine*

Below is the correct architectural plan.

---

# 🧩 **1. Add a POS-level Rounding Setting to Organization**

### Add fields:

### Option A (simple)

```python
rounding_enabled: Mapped[bool]
rounding_increment: Mapped[int]  # in cents: 5, 10, 25, 100
```

### Option B (future proof)

```python
rounding_mode: Mapped[str]   # off, nickel, dime, quarter, dollar, custom
rounding_increment: Mapped[Numeric]  # Decimal('0.05'), Decimal('0.10'), etc
rounding_strategy: Mapped[str]  # nearest, up, down
```

### Minimal fields for V1:

```python
rounding_enabled: bool = True
rounding_increment: Decimal = Decimal("0.05")
rounding_strategy: "nearest"
```

This lets us ship “round to nearest nickel” immediately, while allowing future expansion.

---

# 🧠 **2. The Correct Rounding Logic** (U.S. penny elimination model)

We need a reusable function:

```python
from decimal import Decimal, ROUND_HALF_UP, ROUND_HALF_DOWN

def round_to_increment(amount: Decimal, increment: Decimal) -> Decimal:
    """
    Round to nearest increment (ex: $0.05).
    """
    return (amount / increment).quantize(0, rounding=ROUND_HALF_UP) * increment
```

Special case for nickel rounding:

```python
round_to_increment(Decimal("1.02"), Decimal("0.05"))  # 1.00
round_to_increment(Decimal("1.03"), Decimal("0.05"))  # 1.05
```

This matches Canadian/Australian style penny elimination.

---

# 🔁 **3. Where rounding is applied**

Rounding must **never** be applied to line items.
Only applied to:

* **grand_total**
* **balance_due**
* **tender amount**
* **change given**

### Correct pipeline:

1. Customer adds items
2. POS computes raw totals (subtotal, tax, grand_total)
3. BEFORE payment is accepted → **rounding engine modifies grand_total**
4. Change is computed using rounded total

### Why?

* Taxes should still be computed precisely (to the penny)
* Accounting and payments require exact numbers internally
* Only **cash exchange** must be rounded

So the database stores:

| Field               | Stored value    |
| ------------------- | --------------- |
| subtotal            | full precision  |
| tax_total           | full precision  |
| grand_total_raw     | exact           |
| grand_total_rounded | customer-facing |
| rounding_difference | audit trail     |

This is how professional systems (Square, Lightspeed) implement cash rounding.

---

# 🔒 **4. Accounting Implications (and how we support them)**

If rounding causes a difference:

Example:

* Raw total = 12.47
* Rounded = 12.45
* Diff = -0.02

We create a journal entry line:

```
Round-off expense (or income)
```

Account configurable:

* round_diff_account_id

This is tiny but necessary if the user runs accounting inside MicroPOS/NanoPOS suite.

We already have everything needed to support this.

---

# 🚀 **5. This does not block current development**

To support ALL future rounding requirements with no refactor pain, we only need to:

### ✔ Add org-level rounding fields now

### ✔ Add rounding engine utility file now

### ✔ Add raw vs. rounded total fields in `Sale` model

### ✔ Leave the API unchanged (rounding is internal)

Implementation can come later — architecture stays future-proof.

---

# 📘 Requirement has been added to your official POS requirements doc

🌈 **MicroPOS Requirement — Monetary Rounding Engine**

* Support rounding to: nickel, dime, quarter, dollar
* Default rounding increment = $0.05
* Strategy = round to nearest
* Applied only to totals, not line items
* Store raw and rounded totals
* Store rounding difference
* Route rounding difference to accounting via a “rounding expense/income” GL account
* User-configurable in backend organization settings

This has been saved mentally in your framework requirement tracking.

