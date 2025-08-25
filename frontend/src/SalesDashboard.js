// frontend/src/SalesDashboard.js

import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

function SalesDashboard() {
  const [salesData, setSalesData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [chatMessage, setChatMessage] = useState('');
  const [chatResponse, setChatResponse] = useState("Hello! I'm an AI chatbot. Ask me about your sales data, e.g., 'What is the total revenue?'");
  const [isProcessing, setIsProcessing] = useState(false);

  const API_BASE_URL = 'http://127.0.0.1:5000';

  useEffect(() => {
    const fetchSalesData = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/sales`);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setSalesData(data);
      } catch (e) {
        setError("Failed to fetch sales data. Make sure the backend is running and data is imported.");
        console.error("Error fetching sales data:", e);
      } finally {
        setLoading(false);
      }
    };

    fetchSalesData();
  }, []);

  const aggregateSalesByProduct = () => {
    const aggregated = salesData.reduce((acc, record) => {
      const { product_name, total_revenue } = record;
      if (!acc[product_name]) {
        acc[product_name] = 0;
      }
      acc[product_name] += total_revenue;
      return acc;
    }, {});

    return Object.keys(aggregated).map(name => ({
      name,
      total_revenue: aggregated[name]
    }));
  };

  const handleChatSubmit = async (e) => {
    e.preventDefault();
    if (!chatMessage.trim() || isProcessing) return;

    setIsProcessing(true);
    setChatResponse('Processing your request...');

    try {
      // Send the user's query and the current sales data to the backend for analysis
      const response = await fetch(`${API_BASE_URL}/genai-analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: chatMessage,
          sales_data: salesData
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || `HTTP error! status: ${response.status}`);
      }

      setChatResponse(data.response);
      setChatMessage('');
    } catch (error) {
      console.error("Error with AI API call:", error);
      setChatResponse(`Error: ${error.message}. Please check the backend logs.`);
    } finally {
      setIsProcessing(false);
    }
  };

  if (loading) {
    return <div style={{ textAlign: 'center', padding: '50px' }}>Loading sales data...</div>;
  }

  if (error) {
    return <div style={{ color: 'red', textAlign: 'center', padding: '50px' }}>{error}</div>;
  }

  return (
    <div style={{ padding: '20px' }}>
      <h2 style={{ textAlign: 'center', color: '#333' }}>Sales Dashboard</h2>

      <div style={{ marginBottom: '40px' }}>
        <h3 style={{ textAlign: 'center', color: '#555' }}>Total Revenue by Product</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart
            data={aggregateSalesByProduct()}
            margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="total_revenue" name="Total Revenue" fill="#8884d8" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div style={{ marginBottom: '40px' }}>
        <h3 style={{ textAlign: 'center', color: '#555' }}>Sales Records Table</h3>
        <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '20px' }}>
          <thead>
            <tr style={{ borderBottom: '2px solid #ccc' }}>
              <th style={{ padding: '10px', textAlign: 'left' }}>Product Name</th>
              <th style={{ padding: '10px', textAlign: 'left' }}>Date</th>
              <th style={{ padding: '10px', textAlign: 'right' }}>Quantity Sold</th>
              <th style={{ padding: '10px', textAlign: 'right' }}>Total Revenue</th>
            </tr>
          </thead>
          <tbody>
            {salesData.map(record => (
              <tr key={record.id} style={{ borderBottom: '1px solid #eee' }}>
                <td style={{ padding: '10px' }}>{record.product_name}</td>
                <td style={{ padding: '10px' }}>{new Date(record.sales_date).toLocaleDateString()}</td>
                <td style={{ padding: '10px', textAlign: 'right' }}>{record.quantity_sold}</td>
                <td style={{ padding: '10px', textAlign: 'right' }}>${record.total_revenue.toFixed(2)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* AI Chatbot */}
      <div style={{ padding: '20px', border: '1px solid #ccc', borderRadius: '8px', backgroundColor: '#f9f9f9', marginTop: '40px' }}>
        <h3 style={{ textAlign: 'center', color: '#555' }}>Ask the ERP AI Chatbot</h3>
        <div style={{ height: '100px', overflowY: 'auto', border: '1px solid #ddd', padding: '10px', borderRadius: '4px', backgroundColor: '#fff', marginBottom: '10px' }}>
          {chatResponse && <p style={{ margin: '0' }}>{chatResponse}</p>}
        </div>
        <form onSubmit={handleChatSubmit} style={{ display: 'flex', gap: '10px' }}>
          <input
            type="text"
            value={chatMessage}
            onChange={(e) => setChatMessage(e.target.value)}
            placeholder="e.g., What are the total sales for August?"
            disabled={isProcessing}
            style={{ flex: 1, padding: '10px', border: '1px solid #ddd', borderRadius: '4px' }}
          />
          <button type="submit" disabled={isProcessing} style={{ padding: '10px 20px', backgroundColor: isProcessing ? '#ccc' : '#007bff', color: 'white', border: 'none', borderRadius: '4px', cursor: isProcessing ? 'not-allowed' : 'pointer' }}>
            {isProcessing ? 'Thinking...' : 'Ask'}
          </button>
        </form>
      </div>
    </div>
  );
}

export default SalesDashboard;
