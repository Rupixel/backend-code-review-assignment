
Endpoint:
GET /api/companies/{company_id}/alerts/low-stock

---

## Assumptions

1. Products belong to a single company.
2. Inventory is tracked per product per warehouse.
3. Recent sales activity means at least one sale in the last 30 days.
4. Low-stock threshold is defined per product type.
5. Days until stockout is calculated using average daily sales.
6. Each product has one primary supplier for reordering.
7. Inventory history and sales data are reliable sources of truth.

---

## High-Level Approach

1. Fetch all warehouses belonging to the company.
2. For each warehouse, fetch inventory records.
3. Filter products that:
   - Have stock below their defined threshold
   - Have recent sales activity
4. Calculate estimated days until stockout.
5. Attach supplier details for reordering.
6. Aggregate results across warehouses.

---

## Edge Cases Handled

- Company with no warehouses
- Products with zero recent sales
- Missing supplier information
- Zero or negative inventory
- Division by zero when calculating stockout days

