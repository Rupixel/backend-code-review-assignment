from decimal import Decimal
from sqlalchemy.exc import IntegrityError
from flask import request, jsonify

@app.route('/api/products', methods=['POST'])
def create_product():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid or missing JSON body"}), 400

    # Required fields
    required_fields = ["name", "sku", "price"]
    missing = [f for f in required_fields if f not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    # Validate SKU uniqueness
    existing_product = Product.query.filter_by(sku=data["sku"]).first()
    if existing_product:
        return jsonify({"error": "SKU already exists"}), 409

    # Validate price
    try:
        price = Decimal(str(data["price"]))
        if price < 0:
            raise ValueError
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid price value"}), 400

    warehouse_id = data.get("warehouse_id")
    initial_quantity = data.get("initial_quantity", 0)

    try:
        # Use a single transaction
        product = Product(
            name=data["name"],
            sku=data["sku"],
            price=price
        )
        db.session.add(product)
        db.session.flush()  # ensures product.id is available

        # Inventory is optional and warehouse-specific
        if warehouse_id is not None:
            warehouse = Warehouse.query.get(warehouse_id)
            if not warehouse:
                db.session.rollback()
                return jsonify({"error": "Invalid warehouse_id"}), 400

            inventory = Inventory(
                product_id=product.id,
                warehouse_id=warehouse_id,
                quantity=initial_quantity
            )
            db.session.add(inventory)

        db.session.commit()

    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Database integrity error"}), 409
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Internal server error"}), 500

    return jsonify({
        "message": "Product created successfully",
        "product_id": product.id
    }), 201

##API Endpoint code
@app.route('/api/products', methods=['POST'])
def create_product():
    ...
    return jsonify({...}), 201


# -------------------------------
# Low stock alerts API
# -------------------------------

from datetime import datetime, timedelta
from flask import jsonify

@app.route('/api/companies/<int:company_id>/alerts/low-stock', methods=['GET'])
def low_stock_alerts(company_id):
    alerts = []

    # Fetch warehouses for the company
    warehouses = Warehouse.query.filter_by(company_id=company_id).all()
    if not warehouses:
        return jsonify({"alerts": [], "total_alerts": 0}), 200

    thirty_days_ago = datetime.utcnow() - timedelta(days=30)

    for warehouse in warehouses:
        inventories = Inventory.query.filter_by(warehouse_id=warehouse.id).all()

        for inventory in inventories:
            product = Product.query.get(inventory.product_id)

            # Skip if product is missing
            if not product:
                continue

            # Get low-stock threshold (assumed per product type)
            threshold = product.low_stock_threshold

            if inventory.quantity >= threshold:
                continue

            # Check recent sales activity
            recent_sales = Sale.query.filter(
                Sale.product_id == product.id,
                Sale.created_at >= thirty_days_ago
            ).count()

            if recent_sales == 0:
                continue

            # Calculate average daily sales
            avg_daily_sales = recent_sales / 30
            if avg_daily_sales == 0:
                continue

            days_until_stockout = int(inventory.quantity / avg_daily_sales)

            # Fetch supplier info
            supplier_link = SupplierProduct.query.filter_by(
                product_id=product.id
            ).first()

            supplier_data = None
            if supplier_link:
                supplier = Supplier.query.get(supplier_link.supplier_id)
                if supplier:
                    supplier_data = {
                        "id": supplier.id,
                        "name": supplier.name,
                        "contact_email": supplier.contact_email
                    }

            alerts.append({
                "product_id": product.id,
                "product_name": product.name,
                "sku": product.sku,
                "warehouse_id": warehouse.id,
                "warehouse_name": warehouse.name,
                "current_stock": inventory.quantity,
                "threshold": threshold,
                "days_until_stockout": days_until_stockout,
                "supplier": supplier_data
            })

    return jsonify({
        "alerts": alerts,
        "total_alerts": len(alerts)
    }), 200

