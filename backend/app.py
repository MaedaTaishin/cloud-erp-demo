# backend/app.py

import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import click # Import click for CLI commands

print("--- Starting app.py execution ---")

# --- Configuration ---
# Determine the base directory of the project
basedir = os.path.abspath(os.path.dirname(__file__))
print(f"Basedir: {basedir}")

app = Flask(__name__)

# Configure the database
# Using SQLite for local development simplicity.
# The database file will be created in the 'database' directory.
db_dir = os.path.join(basedir, '../database')
db_path = os.path.join(db_dir, 'erp_demo.db')

# Ensure the database directory exists before configuring SQLAlchemy
os.makedirs(db_dir, exist_ok=True)
print(f"Database directory ensured at: {db_dir}")
print(f"Database path configured to: {db_path}")

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Suppress a warning

db = SQLAlchemy(app)
print("SQLAlchemy DB object initialized.")

# --- Database Model ---
class Product(db.Model):
    """
    Represents a product in the ERP system.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Product {self.name}>'

    def to_dict(self):
        """
        Converts a Product object to a dictionary for JSON serialization.
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'quantity': self.quantity,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# --- CLI Command for Database Initialization ---
@app.cli.command('init-db')
def init_db_command():
    """Clear existing data and create new tables."""
    print("Attempting to create database tables via CLI command...")
    try:
        with app.app_context():
            # Ensure the database directory exists before creating tables
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            db.create_all()
        click.echo('Initialized the database.') # Use click.echo for CLI output
        print("Database tables created successfully or already exist.")
    except Exception as e:
        click.echo(f"Error initializing database: {e}")
        print(f"Error initializing database: {e}")


# --- API Endpoints ---

@app.route('/')
def home():
    """
    Basic home route to confirm the server is running.
    """
    return jsonify({"message": "Welcome to the Cloud ERP Demo Backend!"})

@app.route('/products', methods=['POST'])
def create_product():
    """
    Creates a new product.
    Expects JSON input with 'name', 'price', and 'quantity'.
    'description' is optional.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    name = data.get('name')
    price = data.get('price')
    quantity = data.get('quantity')
    description = data.get('description')

    if not all([name, price is not None, quantity is not None]):
        return jsonify({"error": "Missing required fields: name, price, quantity"}), 400

    if not isinstance(price, (int, float)) or price < 0:
        return jsonify({"error": "Price must be a non-negative number"}), 400
    if not isinstance(quantity, int) or quantity < 0:
        return jsonify({"error": "Quantity must be a non-negative integer"}), 400

    new_product = Product(
        name=name,
        description=description,
        price=float(price),
        quantity=int(quantity)
    )

    try:
        db.session.add(new_product)
        db.session.commit()
        return jsonify(new_product.to_dict()), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": f"Product with name '{name}' already exists."}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route('/products', methods=['GET'])
def get_products():
    """
    Retrieves all products.
    """
    products = Product.query.all()
    return jsonify([product.to_dict() for product in products]), 200

@app.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """
    Retrieves a single product by its ID.
    """
    product = Product.query.get(product_id)
    if product is None:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(product.to_dict()), 200

@app.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    """
    Updates an existing product by its ID.
    Expects JSON input with fields to update.
    """
    product = Product.query.get(product_id)
    if product is None:
        return jsonify({"error": "Product not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    try:
        if 'name' in data:
            product.name = data['name']
        if 'description' in data:
            product.description = data['description']
        if 'price' in data:
            if not isinstance(data['price'], (int, float)) or data['price'] < 0:
                return jsonify({"error": "Price must be a non-negative number"}), 400
            product.price = float(data['price'])
        if 'quantity' in data:
            if not isinstance(data['quantity'], int) or data['quantity'] < 0:
                return jsonify({"error": "Quantity must be a non-negative integer"}), 400
            product.quantity = int(data['quantity'])

        db.session.commit()
        return jsonify(product.to_dict()), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": f"Product with name '{data.get('name')}' already exists."}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    """
    Deletes a product by its ID.
    """
    product = Product.query.get(product_id)
    if product is None:
        return jsonify({"error": "Product not found"}), 404

    try:
        db.session.delete(product)
        db.session.commit()
        return jsonify({"message": "Product deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    print("--- Entering __main__ block ---")
    # This block runs when the script is executed directly.
    # It's generally not recommended to call db.create_all() here
    # when using 'flask run' as the primary way to start the app.
    # Instead, use the 'flask init-db' CLI command.
    # The app.run() will still work if you run 'python app.py' directly.
    app.run(debug=True, port=5000)
    print("--- Exited app.run() ---")