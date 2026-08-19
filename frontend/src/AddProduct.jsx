import { useState } from 'react';
import { api } from './api';
import './AddProduct.css';

function AddProduct({ onProductAdded }) {
  const [formData, setFormData] = useState({
    name: '',
    category: '',
    price: '',
    current_stock: '',
    minimum_stock: '10',
    supplier: '',
    expiry_date: ''
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    try {
      // Validate required fields
      if (!formData.name || !formData.price || !formData.current_stock) {
        throw new Error('Please fill in all required fields');
      }

      // Convert price to decimal
      const productData = {
        ...formData,
        price: parseFloat(formData.price),
        current_stock: parseInt(formData.current_stock),
        minimum_stock: parseInt(formData.minimum_stock)
      };

      // Remove empty fields
      Object.keys(productData).forEach(key => {
        if (!productData[key]) delete productData[key];
      });

      const response = await api.createProduct(productData);

      if (response.id) {
        setSuccess('Product added successfully!');
        setFormData({
          name: '',
          category: '',
          price: '',
          current_stock: '',
          minimum_stock: '10',
          supplier: '',
          expiry_date: ''
        });

        setTimeout(() => {
          onProductAdded();
        }, 1000);
      }
    } catch (err) {
      setError(err.message || 'Failed to add product');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="add-product-container">
      <div className="add-product-form-wrapper">
        <h2>➕ Add New Product</h2>

        {error && <div className="error-message">{error}</div>}
        {success && <div className="success-message">{success}</div>}

        <form onSubmit={handleSubmit} className="add-product-form">
          <div className="form-row">
            <div className="form-group full-width">
              <label htmlFor="name">Product Name *</label>
              <input
                type="text"
                id="name"
                name="name"
                value={formData.name}
                onChange={handleChange}
                placeholder="Enter product name"
                required
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="category">Category</label>
              <input
                type="text"
                id="category"
                name="category"
                value={formData.category}
                onChange={handleChange}
                placeholder="e.g., Electronics"
              />
            </div>

            <div className="form-group">
              <label htmlFor="supplier">Supplier</label>
              <input
                type="text"
                id="supplier"
                name="supplier"
                value={formData.supplier}
                onChange={handleChange}
                placeholder="Supplier name"
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="price">Price (₹) *</label>
              <input
                type="number"
                id="price"
                name="price"
                value={formData.price}
                onChange={handleChange}
                placeholder="0.00"
                step="0.01"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="current_stock">Current Stock *</label>
              <input
                type="number"
                id="current_stock"
                name="current_stock"
                value={formData.current_stock}
                onChange={handleChange}
                placeholder="0"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="minimum_stock">Minimum Stock Level</label>
              <input
                type="number"
                id="minimum_stock"
                name="minimum_stock"
                value={formData.minimum_stock}
                onChange={handleChange}
                placeholder="10"
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group full-width">
              <label htmlFor="expiry_date">Expiry Date</label>
              <input
                type="date"
                id="expiry_date"
                name="expiry_date"
                value={formData.expiry_date}
                onChange={handleChange}
              />
            </div>
          </div>

          <div className="form-actions">
            <button
              type="submit"
              className="submit-btn"
              disabled={loading}
            >
              {loading ? 'Adding Product...' : 'Add Product'}
            </button>
          </div>
        </form>

        <div className="form-info">
          <h3>💡 Product Guidelines</h3>
          <ul>
            <li>Product Name and Price are required fields</li>
            <li>Current Stock must be a positive integer</li>
            <li>Minimum Stock Level helps track low inventory alerts</li>
            <li>Expiry Date is optional but recommended for tracking</li>
            <li>Products with stock below minimum will trigger alerts</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

export default AddProduct;
