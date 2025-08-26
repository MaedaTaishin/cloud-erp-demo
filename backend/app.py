# backend/app.py

import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import click
import csv
from flask_cors import CORS
import requests
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
CORS(app)

db_dir = os.path.join(basedir, '../database')
db_path = os.path.join(db_dir, 'erp_demo.db')

os.makedirs(db_dir, exist_ok=True)

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- Database Models ---
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

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

class SalesRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    sales_date = db.Column(db.DateTime, nullable=False)
    quantity_sold = db.Column(db.Integer, nullable=False)
    total_revenue = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'product_name': self.product_name,
            'sales_date': self.sales_date.isoformat(),
            'quantity_sold': self.quantity_sold,
            'total_revenue': self.total_revenue
        }

# --- CLI Command for Database Initialization and Data Import ---
@app.cli.command('init-db')
def init_db_command():
    click.echo("Initializing the database...")
    try:
        with app.app_context():
            db.create_all()
        click.echo('Database tables created.')
    except Exception as e:
        click.echo(f"Error initializing database: {e}")
        raise

@app.cli.command('import-sales')
@click.argument('filepath')
def import_sales_command(filepath):
    click.echo(f"Importing sales data from {filepath}...")
    try:
        with open(filepath, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            sales_records = []
            for row in reader:
                record = SalesRecord(
                    product_name=row['product_name'],
                    sales_date=datetime.strptime(row['sales_date'], '%Y-%m-%d'),
                    quantity_sold=int(row['quantity_sold']),
                    total_revenue=float(row['total_revenue'])
                )
                sales_records.append(record)
        with app.app_context():
            db.session.add_all(sales_records)
            db.session.commit()
        click.echo(f"Successfully imported {len(sales_records)} sales records.")
    except Exception as e:
        click.echo(f"Error importing sales data: {e}")
        db.session.rollback()

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

@app.route('/sales', methods=['GET'])
def get_sales_data():
    sales = SalesRecord.query.all()
    return jsonify([record.to_dict() for record in sales])

@app.route('/genai-analyze', methods=['POST'])
def genai_analyze_data():
    data = request.get_json()
    if not data or 'query' not in data or 'sales_data' not in data:
        return jsonify({"error": "Invalid request. Missing 'query' or 'sales_data'."}), 400
    
    user_query = data['query']
    sales_data = data['sales_data']
    
    # Get your API key and model ID from the environment variables
    api_key = os.getenv("HUGGINGFACE_API_KEY") 
    model_id = os.getenv("HUGGINGFACE_MODEL_ID")

    # Fallback to hardcoded logic if API keys are not set
    if not api_key or not model_id:
        response_text = "I'm sorry, the AI model API key or model ID is not configured. Please check your .env file."
        return jsonify({"response": response_text}), 200

    # --- Hugging Face API Call ---
    # Construct the full prompt for the model
    prompt_text = f"""
    You are a helpful and concise sales data analyst. Here is some sales data in JSON format:
    
    {json.dumps(sales_data)}
    
    The user is asking the following question: '{user_query}'. Please answer the user's question based ONLY on the data provided, without any extra commentary.
    """
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    api_url = f"https://api-inference.huggingface.co/models/{model_id}"

    payload = {
        "inputs": prompt_text,
        "parameters": {
            "max_new_tokens": 100,
            "temperature": 0.1,
            "return_full_text": False
        }
    }

    try:
        api_response = requests.post(api_url, headers=headers, json=payload, timeout=30)
        api_response.raise_for_status()

        model_response_json = api_response.json()
        model_text = model_response_json[0]['generated_text']
        
        return jsonify({"response": model_text}), 200

    except requests.exceptions.RequestException as e:
        print(f"Error calling Hugging Face API: {e}")
        return jsonify({"error": "Failed to get a response from the Hugging Face model. Please check the backend logs."}), 500
    except (KeyError, IndexError) as e:
        print(f"Unexpected response format from Hugging Face API: {e}")
        return jsonify({"error": "The Hugging Face model returned an unexpected response format."}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
