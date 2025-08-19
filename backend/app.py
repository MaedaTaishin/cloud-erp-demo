# backend/app.py

import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import click
from flask_cors import CORS # NEW: Import CORS

print("--- Starting app.py execution ---")

# --- Configuration ---
basedir = os.path.abspath(os.path.dirname(__file__))
print(f"Basedir: {basedir}")

app = Flask(__name__)
CORS(app) # NEW: Enable CORS for your Flask app. This allows requests from your frontend.

# Configure the database
db_dir = os.path.join(basedir, '../database')
db_path = os.path.join(db_dir, 'erp_demo.db')

os.makedirs(db_dir, exist_ok=True)
print(f"Database directory ensured at: {db_dir}")
print(f"Database path configured to: {db_path}")

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
print("SQLAlchemy DB object initialized.")

# --- Database Model ---
class Product(db.Model):
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
    print("Attempting to create database tables via CLI command...")
    try:
        with app.app_context():
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            db.create_all()
        click.echo('Initialized the database.')
        print("Database tables created successfully or already exist.")
    except Exception as e:
        click.echo(f"Error initializing database: {e}")
        print(f"Error initializing database: {e}")

# --- API Endpoints ---
@app.route('/')
def home():
    return jsonify({"message": "Welcome to the Cloud ERP Demo Backend!"})

@app.route('/products', methods=['POST'])
def create_product():
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
    products = Product.query.all()
    return jsonify([product.to_dict() for product in products]), 200

@app.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get(product_id)
    if product is None:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(product.to_dict()), 200

@app.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
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
    app.run(debug=True, port=5000)
    print("--- Exited app.run() ---")