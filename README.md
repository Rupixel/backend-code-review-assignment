# Backend Code Review & Debugging Assignment

This repository contains my review and fixes for a Flask API endpoint
responsible for creating products and initializing inventory.

The original implementation compiled successfully but had multiple
issues that could cause failures and data inconsistencies in production.

---

## 1. Issues Identified

### 1. Missing request validation
The code assumed a valid JSON body and the presence of all required fields.

### 2. SKU uniqueness not enforced
There was no check to ensure SKUs are unique across the platform.

### 3. Multiple database commits
The product and inventory were committed in separate transactions.

### 4. Tight coupling of product and inventory creation
Inventory was always created at product creation time, even though
products can exist in multiple warehouses.

### 5. Unsafe price handling
Price values were taken directly from the request without validation
or proper decimal handling.

### 6. No error handling or rollback
Database errors could leave the session in a broken state or result
in partial data writes.

### 7. No validation of warehouse existence
Inventory could be created with an invalid warehouse reference.

---

## 2. Impact in Production

- Invalid or malformed requests could cause 500 Internal Server Errors.
- Duplicate SKUs could break downstream systems such as inventory,
  ordering, and reporting.
- Partial commits could create orphaned products without inventory.
- Floating-point price storage could lead to incorrect monetary values.
- Data inconsistencies would require manual cleanup and impact reliability.

---

## 3. Fixes Implemented

- Added request body and required field validation.
- Enforced SKU uniqueness at the API layer.
- Used a single database transaction to ensure atomicity.
- Used `Decimal` for safe price handling.
- Made inventory creation optional and warehouse-specific.
- Added proper error handling with session rollback.
- Returned meaningful HTTP status codes for all outcomes.

---

## 4. Assumptions

- A product can exist without inventory.
- Inventory is managed per warehouse.
- SKU uniqueness is a strict business requirement.
- Database enforces foreign key constraints.

---

## Files

- `app.py` — Corrected and production-safe API implementation
