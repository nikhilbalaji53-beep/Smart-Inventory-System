import { useState, useEffect } from 'react';
import { api } from './api';
import './SupplierDashboard.css';

function SupplierDashboard({ onLogout }) {
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [supplierData, setSupplierData] = useState(null);
  const [orders, setOrders] = useState([]);
  const [products, setProducts] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [orderQuantity, setOrderQuantity] = useState(1);

  const supplierId = localStorage.getItem('supplier_id');
  const companyName = localStorage.getItem('company_name');

  // Load supplier profile from the authenticated supplier backend record
  useEffect(() => {
    const fetchSupplierData = async () => {
      try {
        setLoading(true);
        const profile = await api.getSupplierProfile();

        const normalizedProfile = {
          id: profile.supplier_id || profile.id || supplierId,
          company_name: profile.company_name || companyName || 'Supplier Company',
          status: profile.is_approved === 1 ? 'ACTIVE' : 'PENDING',
          email: profile.email || localStorage.getItem('supplier_email') || '',
          phone: profile.phone || localStorage.getItem('supplier_phone') || '',
          address: profile.address || localStorage.getItem('supplier_address') || '',
          gst_number: profile.gst_number || localStorage.getItem('supplier_gst') || ''
        };

        if (normalizedProfile.email) localStorage.setItem('supplier_email', normalizedProfile.email);
        if (normalizedProfile.phone) localStorage.setItem('supplier_phone', normalizedProfile.phone);
        if (normalizedProfile.address) localStorage.setItem('supplier_address', normalizedProfile.address);
        if (normalizedProfile.gst_number) localStorage.setItem('supplier_gst', normalizedProfile.gst_number);

        setSupplierData(normalizedProfile);
        setError('');
      } catch (err) {
        console.error('Failed to load supplier profile:', err);

        const fallbackProfile = {
          id: supplierId,
          company_name: companyName || 'Supplier Company',
          status: 'ACTIVE',
          email: localStorage.getItem('supplier_email') || 'contact@supplier.com',
          phone: localStorage.getItem('supplier_phone') || '+1-234-567-8900',
          address: localStorage.getItem('supplier_address') || 'Supplier Address',
          gst_number: localStorage.getItem('supplier_gst') || 'GST123456789'
        };

        setSupplierData(fallbackProfile);
        setError('');
      } finally {
        setLoading(false);
      }
    };

    if (supplierId || companyName) {
      fetchSupplierData();
    }
  }, [supplierId, companyName]);

  // Load products (mock data for now)
  useEffect(() => {
    loadProducts();
  }, []);

  // Load orders and notifications
  useEffect(() => {
    loadOrders();
    loadNotifications();
  }, [activeTab]);

  const loadProducts = async () => {
    try {
      const response = await api.getProducts();
      setProducts(response || []);
    } catch (err) {
      console.error('Failed to load products:', err);
      // Set mock products for demo
      setProducts([
        { id: 1, name: 'Laptop', price: 50000, stock: 15, category: 'Electronics' },
        { id: 2, name: 'Office Chair', price: 8000, stock: 32, category: 'Furniture' },
        { id: 3, name: 'Desk Lamp', price: 1500, stock: 50, category: 'Accessories' },
        { id: 4, name: 'Monitor Stand', price: 3000, stock: 22, category: 'Accessories' }
      ]);
    }
  };

  const loadOrders = async () => {
    try {
      // Mock orders data
      setOrders([
        {
          id: 'ORD001',
          date: '2026-08-15',
          status: 'DELIVERED',
          items: 5,
          total: 125000,
          deliveryDate: '2026-08-18'
        },
        {
          id: 'ORD002',
          date: '2026-08-16',
          status: 'SHIPPED',
          items: 3,
          total: 45000,
          deliveryDate: '2026-08-20'
        },
        {
          id: 'ORD003',
          date: '2026-08-17',
          status: 'PENDING',
          items: 2,
          total: 16000,
          deliveryDate: 'TBD'
        }
      ]);
    } catch (err) {
      console.error('Failed to load orders:', err);
    }
  };

  const loadNotifications = async () => {
    try {
      // Mock notifications
      setNotifications([
        { id: 1, type: 'ORDER', message: 'Order ORD001 has been delivered', date: '2026-08-18', read: true },
        { id: 2, type: 'STOCK', message: 'Stock alert: Product XYZ is running low', date: '2026-08-17', read: false },
        { id: 3, type: 'DELIVERY', message: 'Your order ORD002 has been shipped', date: '2026-08-16', read: true },
        { id: 4, type: 'ALERT', message: 'New product available: Product ABC', date: '2026-08-15', read: false }
      ]);
    } catch (err) {
      console.error('Failed to load notifications:', err);
    }
  };

  const handlePlaceOrder = async () => {
    if (!selectedProduct) {
      setError('Please select a product');
      return;
    }
    try {
      setLoading(true);
      // Mock order placement
      alert(`Order placed for ${orderQuantity}x ${selectedProduct.name}`);
      setSelectedProduct(null);
      setOrderQuantity(1);
      loadOrders();
    } catch (err) {
      setError('Failed to place order');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('supplier_token');
    localStorage.removeItem('supplier_id');
    localStorage.removeItem('company_name');
    onLogout();
  };

  return (
    <div className="supplier-dashboard-container">
      {/* Header */}
      <div className="supplier-header">
        <div className="supplier-header-left">
          <h1>📦 SUPPLIER PORTAL</h1>
          <p>{companyName || 'Supplier Company'}</p>
        </div>
        <div className="supplier-header-right">
          <div className="supplier-status">
            <span className="status-badge active">● ACTIVE</span>
          </div>
          <button onClick={handleLogout} className="logout-btn">LOGOUT</button>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="supplier-nav-tabs">
        <button
          className={`nav-tab ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          📊 OVERVIEW
        </button>
        <button
          className={`nav-tab ${activeTab === 'orders' ? 'active' : ''}`}
          onClick={() => setActiveTab('orders')}
        >
          📋 ORDERS
        </button>
        <button
          className={`nav-tab ${activeTab === 'products' ? 'active' : ''}`}
          onClick={() => setActiveTab('products')}
        >
          🛍️ PRODUCTS
        </button>
        <button
          className={`nav-tab ${activeTab === 'stock' ? 'active' : ''}`}
          onClick={() => setActiveTab('stock')}
        >
          📦 STOCK AVAILABILITY
        </button>
        <button
          className={`nav-tab ${activeTab === 'delivery' ? 'active' : ''}`}
          onClick={() => setActiveTab('delivery')}
        >
          🚚 DELIVERY
        </button>
        <button
          className={`nav-tab ${activeTab === 'notifications' ? 'active' : ''}`}
          onClick={() => setActiveTab('notifications')}
        >
          🔔 NOTIFICATIONS
        </button>
        <button
          className={`nav-tab ${activeTab === 'profile' ? 'active' : ''}`}
          onClick={() => setActiveTab('profile')}
        >
          👤 PROFILE
        </button>
      </div>

      {/* Error Message */}
      {error && <div className="supplier-error-message">{error}</div>}

      {/* Content Area */}
      <div className="supplier-content">

        {/* OVERVIEW TAB */}
        {activeTab === 'overview' && (
          <div className="overview-section">
            <h2>Welcome, {companyName}!</h2>
            <div className="overview-grid">
              <div className="overview-card">
                <div className="card-icon">📋</div>
                <div className="card-content">
                  <h3>Total Orders</h3>
                  <p className="card-value">{orders.length}</p>
                  <p className="card-detail">3 Delivered, 1 Shipped</p>
                </div>
              </div>
              <div className="overview-card">
                <div className="card-icon">🛍️</div>
                <div className="card-content">
                  <h3>Available Products</h3>
                  <p className="card-value">{products.length}</p>
                  <p className="card-detail">Ready to order</p>
                </div>
              </div>
              <div className="overview-card">
                <div className="card-icon">🚚</div>
                <div className="card-content">
                  <h3>In Transit</h3>
                  <p className="card-value">1</p>
                  <p className="card-detail">Expected: 2026-08-20</p>
                </div>
              </div>
              <div className="overview-card">
                <div className="card-icon">🔔</div>
                <div className="card-content">
                  <h3>Notifications</h3>
                  <p className="card-value">{notifications.filter(n => !n.read).length}</p>
                  <p className="card-detail">Unread messages</p>
                </div>
              </div>
            </div>

            <div className="overview-section-full">
              <h3>Recent Orders</h3>
              <table className="orders-table">
                <thead>
                  <tr>
                    <th>Order ID</th>
                    <th>Date</th>
                    <th>Items</th>
                    <th>Total</th>
                    <th>Status</th>
                    <th>Delivery</th>
                  </tr>
                </thead>
                <tbody>
                  {orders.slice(0, 3).map(order => (
                    <tr key={order.id}>
                      <td className="order-id-cell">{order.id}</td>
                      <td>{order.date}</td>
                      <td>{order.items}</td>
                      <td>₹{order.total.toLocaleString()}</td>
                      <td><span className={`status-badge ${order.status.toLowerCase()}`}>{order.status}</span></td>
                      <td>{order.deliveryDate}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* ORDERS TAB */}
        {activeTab === 'orders' && (
          <div className="orders-section">
            <h2>Order Management</h2>
            <div className="orders-container">
              <table className="orders-table full-width">
                <thead>
                  <tr>
                    <th>Order ID</th>
                    <th>Date</th>
                    <th>Items</th>
                    <th>Total Amount</th>
                    <th>Status</th>
                    <th>Delivery Date</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {orders.map(order => (
                    <tr key={order.id}>
                      <td className="order-id-cell">{order.id}</td>
                      <td>{order.date}</td>
                      <td>{order.items} items</td>
                      <td className="price-cell">₹{order.total.toLocaleString()}</td>
                      <td><span className={`status-badge ${order.status.toLowerCase()}`}>{order.status}</span></td>
                      <td>{order.deliveryDate}</td>
                      <td><button className="action-btn view-btn">VIEW</button></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* PRODUCTS TAB */}
        {activeTab === 'products' && (
          <div className="products-section">
            <h2>Available Products</h2>
            <div className="products-container">
              {selectedProduct ? (
                <div className="product-detail-view">
                  <button className="back-btn" onClick={() => setSelectedProduct(null)}>← Back to Products</button>
                  <div className="product-detail-card">
                    <div className="product-detail-image">
                      <div className="image-placeholder">📦</div>
                    </div>
                    <div className="product-detail-info">
                      <h3>{selectedProduct.name}</h3>
                      <p className="category">Category: {selectedProduct.category}</p>
                      <div className="price-display">
                        <span className="price-label">Price:</span>
                        <span className="price-value">₹{selectedProduct.price.toLocaleString()}</span>
                      </div>
                      <div className="stock-display">
                        <span className="stock-label">Available Stock:</span>
                        <span className={`stock-value ${selectedProduct.stock > 0 ? 'available' : 'unavailable'}`}>
                          {selectedProduct.stock} units
                        </span>
                      </div>
                      <div className="order-form">
                        <div className="quantity-selector">
                          <label>Quantity Required:</label>
                          <div className="quantity-input">
                            <button onClick={() => setOrderQuantity(Math.max(1, orderQuantity - 1))}>−</button>
                            <input type="number" value={orderQuantity} onChange={(e) => setOrderQuantity(parseInt(e.target.value) || 1)} min="1" />
                            <button onClick={() => setOrderQuantity(orderQuantity + 1)}>+</button>
                          </div>
                        </div>
                        <div className="order-total">
                          <span>Total: ₹{(selectedProduct.price * orderQuantity).toLocaleString()}</span>
                        </div>
                        <button className="place-order-btn" onClick={handlePlaceOrder} disabled={loading}>
                          {loading ? 'PLACING ORDER...' : 'PLACE ORDER'}
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="products-grid">
                  {products.map(product => (
                    <div key={product.id} className="product-card" onClick={() => setSelectedProduct(product)}>
                      <div className="product-image">📦</div>
                      <h4>{product.name}</h4>
                      <p className="category">{product.category}</p>
                      <p className="price">₹{product.price.toLocaleString()}</p>
                      <div className="stock-info">
                        <span className={product.stock > 0 ? 'in-stock' : 'out-of-stock'}>
                          {product.stock > 0 ? `${product.stock} in stock` : 'Out of Stock'}
                        </span>
                      </div>
                      <button className="select-btn">SELECT</button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* STOCK AVAILABILITY TAB */}
        {activeTab === 'stock' && (
          <div className="stock-section">
            <h2>Stock Availability</h2>
            <div className="stock-container">
              <div className="stock-filters">
                <button className="filter-btn active">All Products</button>
                <button className="filter-btn">In Stock</button>
                <button className="filter-btn">Low Stock</button>
                <button className="filter-btn">Out of Stock</button>
              </div>
              <table className="stock-table">
                <thead>
                  <tr>
                    <th>Product Name</th>
                    <th>SKU</th>
                    <th>Category</th>
                    <th>Current Stock</th>
                    <th>Min Level</th>
                    <th>Status</th>
                    <th>Last Updated</th>
                  </tr>
                </thead>
                <tbody>
                  {products.map(product => (
                    <tr key={product.id}>
                      <td>{product.name}</td>
                      <td>SKU{String(product.id).padStart(4, '0')}</td>
                      <td>{product.category}</td>
                      <td className="stock-cell">{product.stock}</td>
                      <td>10</td>
                      <td>
                        <span className={`stock-status ${product.stock > 20 ? 'healthy' : product.stock > 0 ? 'warning' : 'critical'}`}>
                          {product.stock > 20 ? '✓ Healthy' : product.stock > 0 ? '⚠ Low' : '✗ Out'}
                        </span>
                      </td>
                      <td>2026-08-18</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* DELIVERY TAB */}
        {activeTab === 'delivery' && (
          <div className="delivery-section">
            <h2>Delivery Tracking</h2>
            <div className="delivery-container">
              {orders.map(order => (
                <div key={order.id} className="delivery-card">
                  <div className="delivery-header">
                    <h4>{order.id}</h4>
                    <span className={`status-badge ${order.status.toLowerCase()}`}>{order.status}</span>
                  </div>
                  <div className="delivery-timeline">
                    <div className="timeline-item">
                      <div className={`timeline-dot ${order.status === 'DELIVERED' || order.status === 'SHIPPED' ? 'completed' : order.status === 'PENDING' ? 'pending' : ''}`}></div>
                      <div className="timeline-content">
                        <p className="timeline-label">Order Placed</p>
                        <p className="timeline-date">{order.date}</p>
                      </div>
                    </div>
                    <div className="timeline-connector"></div>
                    <div className="timeline-item">
                      <div className={`timeline-dot ${order.status === 'SHIPPED' || order.status === 'DELIVERED' ? 'completed' : ''}`}></div>
                      <div className="timeline-content">
                        <p className="timeline-label">Shipped</p>
                        <p className="timeline-date">In Progress</p>
                      </div>
                    </div>
                    <div className="timeline-connector"></div>
                    <div className="timeline-item">
                      <div className={`timeline-dot ${order.status === 'DELIVERED' ? 'completed' : ''}`}></div>
                      <div className="timeline-content">
                        <p className="timeline-label">Delivery</p>
                        <p className="timeline-date">{order.deliveryDate}</p>
                      </div>
                    </div>
                  </div>
                  <div className="delivery-details">
                    <p><strong>Items:</strong> {order.items}</p>
                    <p><strong>Total:</strong> ₹{order.total.toLocaleString()}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* NOTIFICATIONS TAB */}
        {activeTab === 'notifications' && (
          <div className="notifications-section">
            <h2>Notifications</h2>
            <div className="notifications-container">
              {notifications.length > 0 ? (
                <div className="notifications-list">
                  {notifications.map(notification => (
                    <div key={notification.id} className={`notification-item ${notification.read ? 'read' : 'unread'}`}>
                      <div className="notification-icon">
                        {notification.type === 'ORDER' && '📋'}
                        {notification.type === 'STOCK' && '⚠️'}
                        {notification.type === 'DELIVERY' && '🚚'}
                        {notification.type === 'ALERT' && '🔔'}
                      </div>
                      <div className="notification-content">
                        <p className="notification-message">{notification.message}</p>
                        <p className="notification-date">{notification.date}</p>
                      </div>
                      <div className="notification-status">
                        {!notification.read && <span className="unread-dot"></span>}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="no-notifications">
                  <p>No notifications</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* PROFILE TAB */}
        {activeTab === 'profile' && (
          <div className="profile-section">
            <h2>Supplier Profile</h2>
            {supplierData ? (
              <div className="profile-container">
                <div className="profile-card">
                  <div className="profile-header">
                    <div className="profile-avatar">🏢</div>
                    <div className="profile-title">
                      <h3>{supplierData.company_name}</h3>
                      <p className="profile-status">
                        <span className="status-badge active">● {supplierData.status}</span>
                      </p>
                    </div>
                  </div>

                  <div className="profile-details">
                    <div className="detail-row">
                      <label>Supplier ID:</label>
                      <span>{supplierData.id}</span>
                    </div>
                    <div className="detail-row">
                      <label>Email:</label>
                      <span>{supplierData.email}</span>
                    </div>
                    <div className="detail-row">
                      <label>Phone:</label>
                      <span>{supplierData.phone}</span>
                    </div>
                    <div className="detail-row">
                      <label>Address:</label>
                      <span>{supplierData.address}</span>
                    </div>
                    <div className="detail-row">
                      <label>GST/Business Reg No:</label>
                      <span>{supplierData.gst_number}</span>
                    </div>
                  </div>

                  <div className="profile-actions">
                    <button className="action-btn edit-btn">EDIT PROFILE</button>
                    <button className="action-btn change-pwd-btn">CHANGE PASSWORD</button>
                  </div>
                </div>

                <div className="additional-info">
                  <h4>Account Information</h4>
                  <div className="info-grid">
                    <div className="info-item">
                      <p className="info-label">Member Since</p>
                      <p className="info-value">2026-01-15</p>
                    </div>
                    <div className="info-item">
                      <p className="info-label">Total Orders</p>
                      <p className="info-value">{orders.length}</p>
                    </div>
                    <div className="info-item">
                      <p className="info-label">Total Spent</p>
                      <p className="info-value">₹{orders.reduce((sum, o) => sum + o.total, 0).toLocaleString()}</p>
                    </div>
                    <div className="info-item">
                      <p className="info-label">Rating</p>
                      <p className="info-value">⭐⭐⭐⭐⭐</p>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="loading-state">Loading profile...</div>
            )}
          </div>
        )}

      </div>
    </div>
  );
}

export default SupplierDashboard;
