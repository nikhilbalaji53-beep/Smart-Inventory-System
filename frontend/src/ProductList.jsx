import { useState, useEffect } from 'react';
import { api } from './api';
import './ProductList.css';

function ProductList({ onProductUpdated }) {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [editingId, setEditingId] = useState(null);
  const [editForm, setEditForm] = useState({});
  const [filterCategory, setFilterCategory] = useState('');
  const [categories, setCategories] = useState([]);

  useEffect(() => {
    loadProducts();
  }, []);

  const loadProducts = async () => {
    try {
      setLoading(true);
      const data = await api.getProducts();
      setProducts(data);

      // Extract unique categories
      const cats = [...new Set(data.filter(p => p.category).map(p => p.category))];
      setCategories(cats);

      setError('');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (productId) => {
    if (window.confirm('Are you sure you want to delete this product?')) {
      try {
        await api.deleteProduct(productId);
        loadProducts();
        onProductUpdated();
      } catch (err) {
        setError(err.message);
      }
    }
  };

  const handleEdit = (product) => {
    setEditingId(product.id);
    setEditForm({
      name: product.name,
      category: product.category || '',
      price: product.price,
      current_stock: product.current_stock,
      minimum_stock: product.minimum_stock,
      supplier: product.supplier || '',
      expiry_date: product.expiry_date || ''
    });
  };

  const handleSaveEdit = async (productId) => {
    try {
      await api.updateProduct(productId, editForm);
      setEditingId(null);
      loadProducts();
      onProductUpdated();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleCancel = () => {
    setEditingId(null);
    setEditForm({});
  };

  const handleStockChange = async (productId, currentStock) => {
    const newStock = prompt('Enter new stock quantity:', currentStock);
    if (newStock !== null && newStock !== '') {
      try {
        const changeAmount = parseInt(newStock) - currentStock;
        await api.updateStock(productId, changeAmount);
        loadProducts();
        onProductUpdated();
      } catch (err) {
        setError(err.message);
      }
    }
  };

  const filteredProducts = filterCategory
    ? products.filter(p => p.category === filterCategory)
    : products;

  if (loading) return <div className="loading">Loading products...</div>;

  return (
    <div className="product-list-container">
      <div className="product-list-header">
        <h2>📋 Product Inventory</h2>
        <div className="filter-section">
          <select
            value={filterCategory}
            onChange={(e) => setFilterCategory(e.target.value)}
            className="filter-select"
          >
            <option value="">All Categories</option>
            {categories.map(cat => (
              <option key={cat} value={cat}>{cat}</option>
            ))}
          </select>
        </div>
      </div>

      {error && <div className="error-message">{error}</div>}

      {filteredProducts.length === 0 ? (
        <div className="no-products">No products found</div>
      ) : (
        <div className="products-table-wrapper">
          <table className="products-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Category</th>
                <th>Price</th>
                <th>Current Stock</th>
                <th>Min Stock</th>
                <th>Expiry Date</th>
                <th>Supplier</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredProducts.map(product => (
                <tr key={product.id} className={product.current_stock <= product.minimum_stock ? 'low-stock' : ''}>
                  {editingId === product.id ? (
                    <>
                      <td>{product.id}</td>
                      <td>
                        <input
                          type="text"
                          value={editForm.name}
                          onChange={(e) => setEditForm({ ...editForm, name: e.target.value })}
                          className="edit-input"
                        />
                      </td>
                      <td>
                        <input
                          type="text"
                          value={editForm.category}
                          onChange={(e) => setEditForm({ ...editForm, category: e.target.value })}
                          className="edit-input"
                        />
                      </td>
                      <td>
                        <input
                          type="number"
                          value={editForm.price}
                          onChange={(e) => setEditForm({ ...editForm, price: e.target.value })}
                          className="edit-input"
                          step="0.01"
                        />
                      </td>
                      <td>
                        <input
                          type="number"
                          value={editForm.current_stock}
                          onChange={(e) => setEditForm({ ...editForm, current_stock: e.target.value })}
                          className="edit-input"
                        />
                      </td>
                      <td>
                        <input
                          type="number"
                          value={editForm.minimum_stock}
                          onChange={(e) => setEditForm({ ...editForm, minimum_stock: e.target.value })}
                          className="edit-input"
                        />
                      </td>
                      <td>
                        <input
                          type="date"
                          value={editForm.expiry_date}
                          onChange={(e) => setEditForm({ ...editForm, expiry_date: e.target.value })}
                          className="edit-input"
                        />
                      </td>
                      <td>
                        <input
                          type="text"
                          value={editForm.supplier}
                          onChange={(e) => setEditForm({ ...editForm, supplier: e.target.value })}
                          className="edit-input"
                        />
                      </td>
                      <td>
                        <button
                          onClick={() => handleSaveEdit(product.id)}
                          className="action-btn save"
                        >
                          ✓
                        </button>
                        <button onClick={handleCancel} className="action-btn cancel">
                          ✕
                        </button>
                      </td>
                    </>
                  ) : (
                    <>
                      <td>{product.id}</td>
                      <td><strong>{product.name}</strong></td>
                      <td>{product.category || '-'}</td>
                      <td>₹{parseFloat(product.price).toFixed(2)}</td>
                      <td
                        className={product.current_stock <= product.minimum_stock ? 'stock-warning' : ''}
                      >
                        {product.current_stock}
                      </td>
                      <td>{product.minimum_stock}</td>
                      <td>{product.expiry_date ? product.expiry_date : '-'}</td>
                      <td>{product.supplier || '-'}</td>
                      <td>
                        <button
                          onClick={() => handleEdit(product)}
                          className="action-btn edit"
                          title="Edit"
                        >
                          ✏️
                        </button>
                        <button
                          onClick={() => handleStockChange(product.id, product.current_stock)}
                          className="action-btn stock"
                          title="Update Stock"
                        >
                          📦
                        </button>
                        <button
                          onClick={() => handleDelete(product.id)}
                          className="action-btn delete"
                          title="Delete"
                        >
                          🗑️
                        </button>
                      </td>
                    </>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div className="product-count">
        Total: {filteredProducts.length} products
      </div>
    </div>
  );
}

export default ProductList;
