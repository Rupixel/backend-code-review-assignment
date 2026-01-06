
## 1. Proposed Schema

### companies
| Column | Type | Notes |
|------|-----|------|
| id | BIGINT (PK) | Primary key |
| name | VARCHAR | Company name |
| created_at | TIMESTAMP | |

---

### warehouses
| Column | Type | Notes |
|------|-----|------|
| id | BIGINT (PK) | |
| company_id | BIGINT (FK → companies.id) | One company owns many warehouses |
| name | VARCHAR | |
| location | VARCHAR | Optional |
| created_at | TIMESTAMP | |

**Indexes**
- `(company_id)` #Not known

---

### products
| Column | Type | Notes |
|------|-----|------|
| id | BIGINT (PK) | |
| sku | VARCHAR | Unique across platform |
| name | VARCHAR | |
| price | DECIMAL(10,2) | Monetary values |
| is_bundle | BOOLEAN | Indicates bundle product |
| created_at | TIMESTAMP | |

**Constraints**
- `UNIQUE (sku)`

---

### inventory
| Column | Type | Notes |
|------|-----|------|
| id | BIGINT (PK) | |
| product_id | BIGINT (FK → products.id) | |
| warehouse_id | BIGINT (FK → warehouses.id) | |
| quantity | INT | Current quantity |
| updated_at | TIMESTAMP | |

**Constraints**
- `UNIQUE (product_id, warehouse_id)`#Not known

**Indexes**
- `(product_id, warehouse_id)` #Not known

---

### inventory_history
| Column | Type | Notes |
|------|-----|------|
| id | BIGINT (PK) | |
| product_id | BIGINT (FK → products.id) | |
| warehouse_id | BIGINT (FK → warehouses.id) | |
| quantity_change | INT | + / - movement |
| reason | VARCHAR | Optional (sale, restock, correction) |
| created_at | TIMESTAMP | |

**Purpose**
- Tracks all inventory changes over time (audit trail)

---

### suppliers
| Column | Type | Notes |
|------|-----|------|
| id | BIGINT (PK) | |
| name | VARCHAR | |
| contact_info | VARCHAR | Optional |

---

### supplier_products
| Column | Type | Notes |
|------|-----|------|
| supplier_id | BIGINT (FK → suppliers.id) | |
| product_id | BIGINT (FK → products.id) | |
| lead_time_days | INT | Optional |

**Constraints**
- Composite primary key `(supplier_id, product_id)`

---

### product_bundles
| Column | Type | Notes |
|------|-----|------|
| bundle_id | BIGINT (FK → products.id) | Parent bundle |
| child_product_id | BIGINT (FK → products.id) | Component product |
| quantity | INT | Quantity in bundle |

**Constraints**
- `(bundle_id, child_product_id)` composite PK # Donot have the details
- `bundle_id != child_product_id`

---

## 2. Missing Requirements / Questions for Product Team

1. Can a product belong to multiple companies, or is it global?
2. Should inventory quantities ever go negative?
3. Do bundles have their own inventory or derive stock from components?
4. Is supplier pricing required, or only supplier-product mapping?
5. Should inventory history be immutable?
6. Are warehouses shared across companies or strictly isolated?
7. Do we need soft deletes or archival for products/warehouses?

---

## 3. Design Decisions & Justifications

- **Inventory separated from products** to support multiple warehouses.
- **Inventory history table** ensures traceability and auditability.
- **Decimal used for price** to avoid floating-point precision errors.
- **Unique SKU constraint** enforced at the database level for safety.
- **Bundle modeling via join table** allows flexible composition.
- **Indexes on foreign keys** optimize common lookup queries.
- **Composite uniqueness** on inventory prevents duplicate rows.

---

## 4. Assumptions

- SKU uniqueness is platform-wide.
- Inventory updates always go through controlled services.
- Bundles are logical groupings, not physical stock.
- Strong referential integrity is enforced by the database.
