import React, { useState, useEffect } from 'react';
import {
  Edit2,
  Trash2,
  Plus,
  Filter,
  Search,
  ChevronDown,
  Loader
} from 'lucide-react';
import { api } from '../api';

const StatusBadge = ({ stock, minimum }) => {
  if (stock <= 0) {
    return <span className="badge-critical">Out of Stock</span>;
  } else if (stock <= minimum) {
    return <span className="badge-warning">Low Stock</span>;
  } else {
    return <span className="badge-success">In Stock</span>;
  }
};

export const ProductsTable = ({ onEdit, onDelete, onAddProduct }) => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('All');
  const [categories, setCategories] = useState(['All']);

  useEffect(() => {
    loadProducts();
  }, []);

  const loadProducts = async () => {
    try {
      setLoading(true);
      const data = await api.getProducts();
      setProducts(data || []);

      // Extract unique categories
      const uniqueCategories = ['All', ...new Set(data.map(p => p.category))];
      setCategories(uniqueCategories);

      setError('');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const filteredProducts = products.filter(product => {
    const matchesSearch = product.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         product.category.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = categoryFilter === 'All' || product.category === categoryFilter;
    return matchesSearch && matchesCategory;
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="flex flex-col items-center gap-3">
          <Loader size={32} className="text-indigo-600 animate-spin" />
          <p className="text-slate-500">Loading products...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Products</h1>
          <p className="text-slate-500 mt-1">Manage your inventory items.</p>
        </div>
        <button
          onClick={onAddProduct}
          className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 transition-colors"
        >
          <Plus size={18} />
          Add Product
        </button>
      </div>

      {error && (
        <div className="card p-4 bg-rose-50 border-rose-200">
          <p className="text-sm text-rose-700">{error}</p>
        </div>
      )}

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400" size={18} />
          <input
            type="text"
            placeholder="Search products..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="form-input pl-10"
          />
        </div>
        <div className="relative">
          <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400" size={18} />
          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="form-input pl-10 pr-4 appearance-none"
          >
            {categories.map(cat => (
              <option key={cat} value={cat}>{cat}</option>
            ))}
          </select>
          <ChevronDown className="absolute right-3 top-1/2 transform -translate-y-1/2 text-slate-400 pointer-events-none" size={18} />
        </div>
      </div>

      {/* Table */}
      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-200 bg-slate-50">
                <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-600">Product Name</th>
                <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-600">Category</th>
                <th className="px-6 py-3 text-right text-xs font-semibold uppercase tracking-wider text-slate-600">Price</th>
                <th className="px-6 py-3 text-right text-xs font-semibold uppercase tracking-wider text-slate-600">Stock</th>
                <th className="px-6 py-3 text-center text-xs font-semibold uppercase tracking-wider text-slate-600">Status</th>
                <th className="px-6 py-3 text-center text-xs font-semibold uppercase tracking-wider text-slate-600">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filteredProducts.length > 0 ? (
                filteredProducts.map(product => (
                  <tr key={product.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="table-cell font-medium">{product.name}</td>
                    <td className="table-cell-muted">{product.category}</td>
                    <td className="table-cell text-right">₹{parseFloat(product.price).toLocaleString('en-IN', { minimumFractionDigits: 2 })}</td>
                    <td className="table-cell text-right">
                      <span className={parseFloat(product.current_stock) <= parseFloat(product.minimum_stock) ? 'text-rose-600 font-medium' : ''}>
                        {product.current_stock} / {product.minimum_stock}
                      </span>
                    </td>
                    <td className="table-cell text-center">
                      <StatusBadge stock={product.current_stock} minimum={product.minimum_stock} />
                    </td>
                    <td className="table-cell text-center">
                      <div className="flex items-center justify-center gap-2">
                        <button
                          onClick={() => onEdit(product)}
                          className="btn-icon"
                          title="Edit product"
                        >
                          <Edit2 size={18} />
                        </button>
                        <button
                          onClick={() => onDelete(product.id)}
                          className="inline-flex items-center justify-center w-10 h-10 rounded-lg text-slate-600 hover:bg-rose-50 hover:text-rose-600 focus:ring-2 focus:ring-rose-500 focus:ring-offset-2 transition-colors"
                          title="Delete product"
                        >
                          <Trash2 size={18} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="6" className="px-6 py-12 text-center text-slate-500">
                    <p>No products found</p>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Summary */}
      <div className="text-sm text-slate-500">
        Showing {filteredProducts.length} of {products.length} products
      </div>
    </div>
  );
};

export default ProductsTable;
