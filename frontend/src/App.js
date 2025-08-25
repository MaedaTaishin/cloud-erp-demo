// frontend/src/App.js

import React, { useState, useEffect } from 'react';
import SalesDashboard from './SalesDashboard'; // Import the new component

function App() {
  const [products, setProducts] = useState([]);
  const [newProductName, setNewProductName] = useState('');
  const [newProductDescription, setNewProductDescription] = useState('');
  const [newProductPrice, setNewProductPrice] = useState('');
  const [newProductQuantity, setNewProductQuantity] = useState('');
  const [editingProductId, setEditingProductId] = useState(null);
  const [editFormData, setEditFormData] = useState({
    name: '',
    description: '',
    price: '',
    quantity: ''
  });
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState('');
  const [currentPage, setCurrentPage] = useState('products'); // State for current page

  const API_BASE_URL = 'http://127.0.0.1:5000';

  const fetchProducts = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/products`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setProducts(data);
      setMessage('');
    } catch (error) {
      console.error("Error fetching products:", error);
      setMessage(`Error fetching products: ${error.message}`);
      setMessageType('error');
    }
  };

  useEffect(() => {
    fetchProducts();
  }, []);

  const handleAddProduct = async (e) => {
    e.preventDefault();
    setMessage('');

    const productData = {
      name: newProductName,
      description: newProductDescription,
      price: parseFloat(newProductPrice),
      quantity: parseInt(newProductQuantity, 10)
    };

    if (!productData.name || isNaN(productData.price) || isNaN(productData.quantity)) {
      setMessage('Please fill in all required fields with valid numbers.');
      setMessageType('error');
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/products`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(productData),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || `HTTP error! status: ${response.status}`);
      }

      setMessage('Product added successfully!');
      setMessageType('success');
      setNewProductName('');
      setNewProductDescription('');
      setNewProductPrice('');
      setNewProductQuantity('');
      fetchProducts();
    } catch (error) {
      console.error("Error adding product:", error);
      setMessage(`Error adding product: ${error.message}`);
      setMessageType('error');
    }
  };

  const handleEditClick = (product) => {
    setEditingProductId(product.id);
    setEditFormData({
      name: product.name,
      description: product.description,
      price: product.price,
      quantity: product.quantity
    });
    setMessage('');
  };

  const handleEditFormChange = (e) => {
    const { name, value } = e.target;
    setEditFormData(prevData => ({
      ...prevData,
      [name]: value
    }));
  };

  const handleUpdateProduct = async (e) => {
    e.preventDefault();
    setMessage('');

    const updatedData = {
      name: editFormData.name,
      description: editFormData.description,
      price: parseFloat(editFormData.price),
      quantity: parseInt(editFormData.quantity, 10)
    };

    if (!updatedData.name || isNaN(updatedData.price) || isNaN(updatedData.quantity)) {
      setMessage('Please fill in all required fields with valid numbers.');
      setMessageType('error');
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/products/${editingProductId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updatedData),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || `HTTP error! status: ${response.status}`);
      }

      setMessage('Product updated successfully!');
      setMessageType('success');
      setEditingProductId(null);
      fetchProducts();
    } catch (error) {
      console.error("Error updating product:", error);
      setMessage(`Error updating product: ${error.message}`);
      setMessageType('error');
    }
  };

  const handleCancelEdit = () => {
    setEditingProductId(null);
    setMessage('');
  };

  const handleDeleteProduct = async (productId) => {
    setMessage('');
    if (!window.confirm('Are you sure you want to delete this product?')) {
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/products/${productId}`, {
        method: 'DELETE',
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || `HTTP error! status: ${response.status}`);
      }

      setMessage('Product deleted successfully!');
      setMessageType('success');
      fetchProducts();
    } catch (error) {
      console.error("Error deleting product:", error);
      setMessage(`Error deleting product: ${error.message}`);
      setMessageType('error');
    }
  };

  const renderContent = () => {
    if (currentPage === 'products') {
      return (
        <>
          {message && (
            <div style={{
              padding: '10px',
              borderRadius: '5px',
              marginBottom: '15px',
              backgroundColor: messageType === 'success' ? '#d4edda' : '#f8d7da',
              color: messageType === 'success' ? '#155724' : '#721c24',
              borderColor: messageType === 'success' ? '#c3e6cb' : '#f5c6cb'
            }}>
              {message}
            </div>
          )}

          <h2 style={{ color: '#555', borderBottom: '1px solid #eee', paddingBottom: '10px', marginBottom: '20px' }}>Add New Product</h2>
          <form onSubmit={handleAddProduct} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px', marginBottom: '30px', padding: '15px', border: '1px solid #eee', borderRadius: '5px', backgroundColor: '#f9f9f9' }}>
            <div style={{ gridColumn: 'span 2' }}>
              <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>Product Name:</label>
              <input
                type="text"
                value={newProductName}
                onChange={(e) => setNewProductName(e.target.value)}
                placeholder="e.g., Laptop Pro"
                required
                style={{ width: 'calc(100% - 20px)', padding: '10px', border: '1px solid #ddd', borderRadius: '4px' }}
              />
            </div>
            <div style={{ gridColumn: 'span 2' }}>
              <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>Description:</label>
              <textarea
                value={newProductDescription}
                onChange={(e) => setNewProductDescription(e.target.value)}
                placeholder="A brief description of the product."
                rows="3"
                style={{ width: 'calc(100% - 20px)', padding: '10px', border: '1px solid #ddd', borderRadius: '4px' }}
              ></textarea>
            </div>
            <div>
              <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>Price:</label>
              <input
                type="number"
                step="0.01"
                value={newProductPrice}
                onChange={(e) => setNewProductPrice(e.target.value)}
                placeholder="e.g., 1200.50"
                required
                style={{ width: 'calc(100% - 20px)', padding: '10px', border: '1px solid #ddd', borderRadius: '4px' }}
              />
            </div>
            <div>
              <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>Quantity:</label>
              <input
                type="number"
                value={newProductQuantity}
                onChange={(e) => setNewProductQuantity(e.target.value)}
                placeholder="e.g., 50"
                required
                style={{ width: 'calc(100% - 20px)', padding: '10px', border: '1px solid #ddd', borderRadius: '4px' }}
              />
            </div>
            <button type="submit" style={{ gridColumn: 'span 2', padding: '10px 20px', backgroundColor: '#4CAF50', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer', fontSize: '16px', marginTop: '10px' }}>
              Add Product
            </button>
          </form>

          <h2 style={{ color: '#555', borderBottom: '1px solid #eee', paddingBottom: '10px', marginBottom: '20px' }}>Current Products</h2>
          {products.length === 0 ? (
            <p style={{ textAlign: 'center', color: '#777' }}>No products found. Add some above!</p>
          ) : (
            <ul style={{ listStyle: 'none', padding: 0 }}>
              {products.map(product => (
                <li key={product.id} style={{ border: '1px solid #ddd', borderRadius: '5px', padding: '15px', marginBottom: '15px', backgroundColor: '#fff', display: 'flex', flexDirection: 'column', gap: '10px' }}>
                  {editingProductId === product.id ? (
                    <form onSubmit={handleUpdateProduct} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                      <div style={{ gridColumn: 'span 2' }}>
                        <label style={{ display: 'block', marginBottom: '3px', fontSize: '0.9em' }}>Name:</label>
                        <input
                          type="text"
                          name="name"
                          value={editFormData.name}
                          onChange={handleEditFormChange}
                          required
                          style={{ width: 'calc(100% - 16px)', padding: '8px', border: '1px solid #ccc', borderRadius: '3px' }}
                        />
                      </div>
                      <div style={{ gridColumn: 'span 2' }}>
                        <label style={{ display: 'block', marginBottom: '3px', fontSize: '0.9em' }}>Description:</label>
                        <textarea
                          name="description"
                          value={editFormData.description}
                          onChange={handleEditFormChange}
                          rows="2"
                          style={{ width: 'calc(100% - 16px)', padding: '8px', border: '1px solid #ccc', borderRadius: '3px' }}
                        ></textarea>
                      </div>
                      <div>
                        <label style={{ display: 'block', marginBottom: '3px', fontSize: '0.9em' }}>Price:</label>
                        <input
                          type="number"
                          step="0.01"
                          name="price"
                          value={editFormData.price}
                          onChange={handleEditFormChange}
                          required
                          style={{ width: 'calc(100% - 16px)', padding: '8px', border: '1px solid #ccc', borderRadius: '3px' }}
                        />
                      </div>
                      <div>
                        <label style={{ display: 'block', marginBottom: '3px', fontSize: '0.9em' }}>Quantity:</label>
                        <input
                          type="number"
                          name="quantity"
                          value={editFormData.quantity}
                          onChange={handleEditFormChange}
                          required
                          style={{ width: 'calc(100% - 16px)', padding: '8px', border: '1px solid #ccc', borderRadius: '3px' }}
                        />
                      </div>
                      <div style={{ gridColumn: 'span 2', display: 'flex', gap: '10px', marginTop: '10px' }}>
                        <button type="submit" style={{ flex: 1, padding: '8px 15px', backgroundColor: '#2196F3', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>Save</button>
                        <button type="button" onClick={handleCancelEdit} style={{ flex: 1, padding: '8px 15px', backgroundColor: '#f44336', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>Cancel</button>
                      </div>
                    </form>
                  ) : (
                    <>
                      <h3 style={{ margin: '0', color: '#333' }}>{product.name} (ID: {product.id})</h3>
                      <p style={{ margin: '5px 0', color: '#666' }}>{product.description}</p>
                      <p style={{ margin: '5px 0', color: '#444' }}><strong>Price:</strong> ${product.price ? product.price.toFixed(2) : 'N/A'}</p>
                      <p style={{ margin: '5px 0', color: '#444' }}><strong>Quantity:</strong> {product.quantity}</p>
                      <p style={{ margin: '5px 0', fontSize: '0.8em', color: '#888' }}>
                        Created: {new Date(product.created_at).toLocaleString()} | Last Updated: {new Date(product.updated_at).toLocaleString()}
                      </p>
                      <div style={{ display: 'flex', gap: '10px', marginTop: '10px' }}>
                        <button onClick={() => handleEditClick(product)} style={{ padding: '8px 15px', backgroundColor: '#FFC107', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>Edit</button>
                        <button onClick={() => handleDeleteProduct(product.id)} style={{ padding: '8px 15px', backgroundColor: '#F44336', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>Delete</button>
                      </div>
                    </>
                  )}
                </li>
              ))}
            </ul>
          )}
        </>
      );
    } else if (currentPage === 'dashboard') {
      return <SalesDashboard />;
    }
  };

  return (
    <div style={{ fontFamily: 'Arial, sans-serif', maxWidth: '800px', margin: '20px auto', padding: '20px', border: '1px solid #ccc', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
      <h1 style={{ textAlign: 'center', color: '#333' }}>Cloud ERP Demo</h1>
      <nav style={{ marginBottom: '20px', textAlign: 'center' }}>
        <button
          onClick={() => setCurrentPage('products')}
          style={{ padding: '10px 20px', margin: '0 10px', border: 'none', backgroundColor: currentPage === 'products' ? '#007bff' : '#f0f0f0', color: currentPage === 'products' ? 'white' : 'black', borderRadius: '5px', cursor: 'pointer' }}
        >
          Products
        </button>
        <button
          onClick={() => setCurrentPage('dashboard')}
          style={{ padding: '10px 20px', margin: '0 10px', border: 'none', backgroundColor: currentPage === 'dashboard' ? '#007bff' : '#f0f0f0', color: currentPage === 'dashboard' ? 'white' : 'black', borderRadius: '5px', cursor: 'pointer' }}
        >
          Sales Dashboard
        </button>
      </nav>
      {renderContent()}
    </div>
  );
}

export default App;
