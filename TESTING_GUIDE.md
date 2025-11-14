# 🧪 ArcoírisPOS — Testing Guide  
Foreside Holdings LLC  
FastAPI • PostgreSQL • React • Docker • QA Workflow

---

# 📘 Overview

This **Testing Guide** documents all testing strategies for ArcoírisPOS, including:

- Test environment setup  
- Backend/API testing  
- Frontend/UI testing  
- Integration testing  
- Database integrity testing  
- Manual QA workflows  
- Recommended tools  
- Future automated testing plans  

ArcoírisPOS follows a **test-first mindset**, prioritizing reliability, data consistency, and domain correctness across POS, Inventory, and Accounting modules.

---

# 🧰 Testing Environment Setup

For consistency, testing should be performed in a **clean environment** using one of two options:

---

## **Option A — Docker-Based Test Environment (Recommended)**

Spin up a fresh environment:

```bash
docker-compose up --build
```

Then run tests from inside the backend container (future test tooling).

---

## **Option B — Local Manual Environment**

1. Start PostgreSQL  
2. Apply migrations  
3. Run backend on port 8000  
4. Run frontend on port 3000  
5. Execute tests manually or via tools  

---

# 🐍 Backend (FastAPI) Testing

Backend testing covers:

- Unit tests  
- API endpoint tests  
- Schema validation  
- Business logic tests  
- Authentication tests (future)  
- Domain model tests  

ArcoírisPOS will use:

- **pytest**  
- **httpx** (async client)  
- **pytest-asyncio**  

---

## 🧩 Directory Structure (Future)

Planned structure:

```
backend/
  tests/
    core/
    pos/
    inv/
    acct/
    conftest.py
    test_utils.py
```

---

# 🧪 Core Testing Types

---

## **1. Unit Tests**

Test all domain service functions individually:

- price calculation  
- tax calculation  
- stock decrement logic  
- journal balancing rules  
- data validators  

Example (future):

```python
def test_line_total():
    assert calculate_line_total(2, 10.00) == 20.00
```

---

## **2. API Endpoint Tests**

Simulate requests to FastAPI endpoints:

- GET /sales  
- POST /customers  
- POST /payments  
- GET /items  

Example (future):

```python
async def test_create_customer(async_client):
    response = await async_client.post("/api/pos/customers", json={
        "name": "Test Customer"
    })
    assert response.status_code == 201
```

---

## **3. Database Integrity Tests**

Ensure:

- Foreign keys enforce correctly  
- Cascading deletes behave as expected  
- UUID primary keys generate correctly  
- Journal entries always balance (accounting domain)  

Test queries:

```sql
SELECT * FROM journal_lines jl
JOIN journal_entries je ON je.id = jl.entry_id;
```

---

## **4. Domain-Specific Tests**

### POS  
- Sale totals correct  
- Tax applied consistently  
- Payment methods valid  
- Sale status transitions valid  

### Inventory  
- Stock cannot go negative (unless override)  
- Movements logged correctly  
- Quantity snapshots correct  

### Accounting  
- Double-entry balancing  
- Chart of accounts validation  
- Ledger summarization logic  

---

# ⚛️ Frontend (React) Testing

React testing will use:

- **Jest**  
- **React Testing Library (RTL)**  
- **Mock Service Worker (MSW)** for API mocks  

---

## **UI Testing Types**

### **1. Component Tests**
Test individual components:

- Buttons  
- Forms  
- Tables  
- Modals  

### **2. Integration Tests**
Simulate user interactions:

- Add item → Add sale → Pay sale  
- Item quantity updates automatically  
- Tax rate selection updates totals  

### **3. API Interaction Tests**
Using MSW to mock backend responses.

Example:

```javascript
test("renders customer list", async () => {
  mockCustomers();
  render(<CustomerList />);
  expect(await screen.findByText("John Smith")).toBeInTheDocument();
});
```

---

# 🔗 Integration Testing (End-to-End)

End-to-end testing ensures:

- Backend + Frontend communication  
- Database updates correctly  
- Full workflows behave as expected  

Recommended tools:

- **Playwright** (recommended)  
- **Cypress**  

Scenarios to test:

---

## POS End-to-End Tests

1. Create customer  
2. Add items to sale  
3. Apply discount or tax  
4. Complete payment  
5. Verify stock decremented  
6. Verify journal entries created (future)  

---

## Inventory End-to-End Tests

1. Add item  
2. Adjust stock  
3. Move stock between locations  
4. Verify updated levels  
5. Ensure stock movements recorded  

---

## Accounting End-to-End Tests (Future Phase)

1. Create journal entry  
2. Add multiple lines  
3. Ensure balanced  
4. Check ledger reconciliation  

---

# 🗄️ Database Testing

Database validation ensures correctness:

---

## **1. Migration Tests**

After each migration:

```sql
\d items;
\d sales;
\d journal_entries;
```

Ensure:

- All columns exist  
- Constraints valid  
- Indexes correct  

---

## **2. Referential Integrity Tests**

Queries to validate constraints:

```sql
SELECT * FROM sales WHERE customer_id NOT IN (SELECT id FROM customers);
```

Should always return **0 rows**.

---

## **3. Accounting Balance Tests**

```
SELECT
  entry_id,
  SUM(debit) AS debit_sum,
  SUM(credit) AS credit_sum
FROM journal_lines
GROUP BY entry_id
HAVING SUM(debit) != SUM(credit);
```

Should return **0 rows**.

---

# 🧯 Manual QA Testing

Manual testing ensures UX correctness.

---

## **POS Manual Checklist**

- Create customer  
- Edit customer  
- Create sale  
- Add/remove items  
- Tax calculated correctly  
- Complete sale with each payment type  

---

## **Inventory Manual Checklist**

- Create item  
- Adjust quantity  
- Verify movement record  
- Create location  
- Move stock between locations  

---

## **Accounting Manual Checklist (Future)**

- Create journal entry  
- Verify debit/credit requirement  
- Balance sheet accuracy  
- Income statement accuracy  

---

# 🧩 Testing Environments

ArcoírisPOS should use three types:

---

## **1. Development (local)**  
Docker-based or manual environment.

## **2. Testing (isolated)**  
Separate DB, no shared data.

## **3. Production (future)**  
Strictly limited changes  
Safe migrations only  
Automated test suite required  

---

# 🛠 Recommended Tools

Backend:
- pytest  
- httpx  
- pytest-asyncio  
- coverage.py  

Frontend:
- Jest  
- React Testing Library  
- MSW  
- Playwright  

Integration:
- Playwright  
- Docker Test Containers  

---

# 📈 Code Coverage (Future Implementation)

Target coverage:

| Layer | Coverage Goal |
|-------|---------------|
| Services | 90%+ |
| Models | 95%+ |
| API | 80%+ |
| Frontend | 70%+ |
| Accounting (critical) | 99%+ |

---

# 🧭 Developer Workflow for Tests

### When adding a new feature:

1. Create/update tests  
2. Run backend tests  
3. Run frontend tests  
4. Run integration tests  
5. Validate database behaviors  
6. Submit PR  

**Tests are required for production merges** (future policy).

---

# 🏁 Summary

This Testing Guide ensures:

- Consistent testing methodology  
- Backend and frontend reliability  
- Accurate financial logic  
- Stable POS operations  
- Predictable database behavior  
- Scalable long-term QA processes  

As ArcoírisPOS grows into Nano Business Suite, automated testing becomes critical to maintaining system integrity.

