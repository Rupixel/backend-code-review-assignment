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
