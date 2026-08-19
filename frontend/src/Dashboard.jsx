import { useState, useEffect } from 'react';
import { api } from './api';
import './Dashboard.css';
import './styles/NotificationCenter.css';
import ProductList from './ProductList';
import AddProduct from './AddProduct';
import Alerts from './Alerts';
import NotificationCenter from './NotificationCenter';

function Dashboard({ onLogout, userType }) {
  const [activeTab, setActiveTab] = useState('overview');
  const [dashboardData, setDashboardData] = useState(null);
  const [summaryData, setSummaryData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [notificationPanelOpen, setNotificationPanelOpen] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  const [suppliers, setSuppliers] = useState([]);
  const [suppliersLoading, setSuppliersLoading] = useState(false);
  const [purchaseForm, setPurchaseForm] = useState({ product_id: '', quantity: '', unit_cost: '' });
  const [saleForm, setSaleForm] = useState({ product_id: '', quantity: '', unit_price: '' });

  const username = localStorage.getItem('username');
  const isAdmin = userType === 'admin';

  // Fetch unread notification count
  useEffect(() => {
    fetchUnreadCount();
    // Poll for new notifications every 30 seconds
    const interval = setInterval(fetchUnreadCount, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchUnreadCount = async () => {
    try {
      const response = await fetch(
        'http://localhost:8000/notifications/unread-count',
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
            'Content-Type': 'application/json'
          }
        }
      );
      if (response.ok) {
        const data = await response.json();
        setUnreadCount(data.unread_count);
      }
    } catch (error) {
      console.error('Error fetching unread count:', error);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, [refreshTrigger]);

  useEffect(() => {
    if (isAdmin && (activeTab === 'suppliers' || activeTab === 'overview')) {
      loadPendingSuppliers();
    }
  }, [isAdmin, activeTab]);

  const loadPendingSuppliers = async () => {
    if (!isAdmin) return;
    try {
      setSuppliersLoading(true);
      const data = await api.getPendingSuppliers();
      setSuppliers(data || []);
    } catch (err) {
      console.error('Failed to load pending suppliers:', err);
      setSuppliers([]);
    } finally {
      setSuppliersLoading(false);
    }
  };

  const handleSupplierDecision = async (supplierId, status) => {
    try {
      await api.approveSupplier(supplierId, status);
      await loadPendingSuppliers();
      setActiveTab('suppliers');
    } catch (err) {
      setError(err.message || 'Failed to update supplier status');
    }
  };

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const [dashboard, summary] = await Promise.all([
        api.getDashboard(),
        api.getDashboardSummary()
      ]);
      setDashboardData(dashboard);
      setSummaryData(summary);
      setError('');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = () => {
    setRefreshTrigger(prev => prev + 1);
  };

  const handleProductAdded = () => {
    handleRefresh();
    setActiveTab('products');
  };

  const handleTransaction = async (type, event) => {
    event.preventDefault();
    try {
      setLoading(true);
      const form = type === 'purchase' ? purchaseForm : saleForm;
      const payload = {
        product_id: Number(form.product_id),
        quantity: Number(form.quantity),
        ...(type === 'purchase' ? { unit_cost: Number(form.unit_cost) } : { unit_price: Number(form.unit_price) })
      };
      if (type === 'purchase') {
        await api.recordPurchase(payload);
        setPurchaseForm({ product_id: '', quantity: '', unit_cost: '' });
      } else {
        await api.recordSale(payload);
        setSaleForm({ product_id: '', quantity: '', unit_price: '' });
      }
      setError('');
      await loadDashboardData();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const profitLossProducts = summaryData?.profit_loss?.products || [];
  const chartProducts = profitLossProducts.filter(product => product.profit_loss !== null);
  const chartMax = Math.max(...chartProducts.map(product => Math.abs(product.profit_loss)), 1);

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div className="header-content">
          <h1>📦 Smart Inventory Management</h1>
          <div className="user-info">
            <span>Welcome, {username}</span>
            <button 
              className="notification-btn"
              onClick={() => setNotificationPanelOpen(!notificationPanelOpen)}
              title="Notifications"
            >
              🔔 
              {unreadCount > 0 && <span className="badge">{unreadCount}</span>}
            </button>
            <button onClick={onLogout} className="logout-btn">Logout</button>
          </div>
        </div>
      </header>

      <nav className="dashboard-nav">
        <button
          className={`nav-btn ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          📊 Overview
        </button>
        <button
          className={`nav-btn ${activeTab === 'products' ? 'active' : ''}`}
          onClick={() => setActiveTab('products')}
        >
          📋 Products
        </button>
        <button
          className={`nav-btn ${activeTab === 'add' ? 'active' : ''}`}
          onClick={() => setActiveTab('add')}
        >
          ➕ Add Product
        </button>
        {isAdmin && (
          <button
            className={`nav-btn ${activeTab === 'suppliers' ? 'active' : ''}`}
            onClick={() => setActiveTab('suppliers')}
          >
            🧾 Supplier Approvals
          </button>
        )}
        <button
          className={`nav-btn ${activeTab === 'alerts' ? 'active' : ''}`}
          onClick={() => setActiveTab('alerts')}
        >
          ⚠️ Alerts
        </button>
        {isAdmin && (
          <button
            className={`nav-btn ${activeTab === 'profit-loss' ? 'active' : ''}`}
            onClick={() => setActiveTab('profit-loss')}
          >
            📈 Profit & Loss
          </button>
        )}
      </nav>

      <main className="dashboard-content">
        {error && <div className="error-message">{error}</div>}

        {activeTab === 'overview' && (
          <div className="overview-section">
            <button className="refresh-btn" onClick={handleRefresh} disabled={loading}>
              🔄 Refresh
            </button>

            {loading ? (
              <div className="loading">Loading dashboard data...</div>
            ) : dashboardData && summaryData ? (
              <>
                {/* Key Metrics Cards */}
                <div className="metrics-grid">
                  <div className="metric-card">
                    <h3>📦 Total Products</h3>
                    <p className="metric-value">{dashboardData.total_products}</p>
                  </div>

                  <div className="metric-card">
                    <h3>📊 Total Stock</h3>
                    <p className="metric-value">{dashboardData.total_stock}</p>
                  </div>

                  <div className="metric-card">
                    <h3>💰 Inventory Value</h3>
                    <p className="metric-value">
                      ₹{summaryData.inventory_metrics.inventory_value.toLocaleString('en-IN', {
                        maximumFractionDigits: 2
                      })}
                    </p>
                  </div>

                  <div className="metric-card financial-card">
                    <h3>📈 Estimated Profit / Loss</h3>
                    <p className={`metric-value ${summaryData.profit_loss.estimated_gross_profit < 0 ? 'loss-value' : 'profit-value'}`}>
                      {summaryData.profit_loss.estimated_gross_profit === null
                        ? 'N/A'
                        : `₹${summaryData.profit_loss.estimated_gross_profit.toLocaleString('en-IN', { maximumFractionDigits: 2 })}`}
                    </p>
                    <small>{summaryData.profit_loss.cost_coverage_percent}% cost coverage</small>
                  </div>

                  <div className="metric-card financial-card">
                    <h3>📉 Inventory Cost</h3>
                    <p className="metric-value">
                      {summaryData.profit_loss.costed_products === 0
                        ? 'N/A'
                        : `₹${summaryData.profit_loss.inventory_cost.toLocaleString('en-IN', { maximumFractionDigits: 2 })}`}
                    </p>
                    <small>Based on supplier costs</small>
                  </div>

                  <div className="metric-card highlight-warning">
                    <h3>⚠️ Low Stock</h3>
                    <p className="metric-value">{dashboardData.low_stock_products}</p>
                  </div>

                  <div className="metric-card highlight-danger">
                    <h3>🟠 Expiring Soon</h3>
                    <p className="metric-value">{dashboardData.expiring_soon_products}</p>
                  </div>

                  <div className="metric-card highlight-critical">
                    <h3>💀 Expired</h3>
                    <p className="metric-value">{dashboardData.expired_products}</p>
                  </div>

                  <div className="metric-card">
                    <h3>🔮 7-Day Forecast</h3>
                    <p className="metric-value">{dashboardData.predicted_7_day_demand}</p>
                  </div>
                </div>

                {/* Alerts Section */}
                <div className="alerts-section">
                  <h2>🚨 Critical Alerts</h2>

                  {summaryData.alerts.low_stock_count > 0 && (
                    <div className="alert-category">
                      <h3>📉 Low Stock Products ({summaryData.alerts.low_stock_count})</h3>
                      <div className="alert-items">
                        {summaryData.alerts.low_stock_products.map(product => (
                          <div key={product.id} className="alert-item warning">
                            <div className="alert-content">
                              <strong>{product.name}</strong>
                              <p>Current: {product.current_stock} | Minimum: {product.minimum_stock}</p>
                              <p className="deficit">Deficit: {product.deficit} units</p>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {summaryData.alerts.expiry_alerts_count > 0 && (
                    <div className="alert-category">
                      <h3>🟠 Expiry Alerts ({summaryData.alerts.expiry_alerts_count})</h3>
                      <div className="alert-items">
                        {summaryData.alerts.expiry_alerts.map(product => (
                          <div
                            key={product.id}
                            className={`alert-item ${product.severity === 'CRITICAL' ? 'critical' : 'warning'}`}
                          >
                            <div className="alert-content">
                              <strong>{product.name}</strong>
                              <p>Expiry: {product.expiry_date}</p>
                              <p>{product.days_until_expiry} days {product.status === 'EXPIRED' ? '(EXPIRED)' : 'until expiry'}</p>
                              <p>Stock: {product.current_stock} units</p>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {summaryData.alerts.low_stock_count === 0 && summaryData.alerts.expiry_alerts_count === 0 && (
                    <div className="no-alerts">✅ All systems normal!</div>
                  )}
                </div>
              </>
            ) : null}
          </div>
        )}

        {activeTab === 'products' && (
          <ProductList onProductUpdated={handleRefresh} />
        )}

        {activeTab === 'add' && (
          <AddProduct onProductAdded={handleProductAdded} />
        )}

        {isAdmin && activeTab === 'suppliers' && (
          <div className="suppliers-approval-section">
            <h2>Supplier registration approvals</h2>
            {suppliersLoading ? (
              <div className="loading">Loading supplier requests...</div>
            ) : suppliers.length === 0 ? (
              <div className="no-alerts">✅ No pending supplier registrations.</div>
            ) : (
              <div className="suppliers-list">
                {suppliers.map(supplier => (
                  <div key={supplier.supplier_id} className="supplier-card">
                    <div className="supplier-card-header">
                      <div>
                        <h3>{supplier.company_name}</h3>
                        <p>{supplier.contact_person}</p>
                      </div>
                      <span className="status-badge pending">Pending</span>
                    </div>

                    <div className="supplier-meta-grid">
                      <div><strong>Supplier ID:</strong> {supplier.supplier_id}</div>
                      <div><strong>Email:</strong> {supplier.email}</div>
                      <div><strong>Phone:</strong> {supplier.phone}</div>
                      <div><strong>GST:</strong> {supplier.gst_number}</div>
                      <div className="full-width"><strong>Address:</strong> {supplier.address}</div>
                    </div>

                    <div className="supplier-actions">
                      <button className="approve-btn" onClick={() => handleSupplierDecision(supplier.supplier_id, 'approved')}>
                        Approve
                      </button>
                      <button className="reject-btn" onClick={() => handleSupplierDecision(supplier.supplier_id, 'rejected')}>
                        Reject
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'alerts' && (
          <Alerts />
        )}

        {isAdmin && activeTab === 'profit-loss' && summaryData && (
          <div className="profit-loss-section">
            <div className="section-heading">
              <div>
                <h2>Product Profit & Loss</h2>
                <p>Estimated gross profit based on current stock and recorded supplier costs.</p>
              </div>
              <button className="refresh-btn" onClick={handleRefresh} disabled={loading}>🔄 Refresh</button>
            </div>
            <div className="profit-summary-strip">
              <span>Sales value: <strong>₹{summaryData.profit_loss.potential_sales_value.toLocaleString('en-IN')}</strong></span>
              <span>Inventory cost: <strong>{summaryData.profit_loss.costed_products ? `₹${summaryData.profit_loss.inventory_cost.toLocaleString('en-IN')}` : 'N/A'}</strong></span>
              <span>Coverage: <strong>{summaryData.profit_loss.cost_coverage_percent}%</strong></span>
            </div>
            <div className="transaction-controls">
              <form onSubmit={(event) => handleTransaction('purchase', event)} className="transaction-form purchase-form">
                <h3>Record Purchase</h3>
                <select value={purchaseForm.product_id} onChange={(event) => setPurchaseForm({ ...purchaseForm, product_id: event.target.value })} required>
                  <option value="">Select product</option>
                  {profitLossProducts.map(product => <option key={`buy-${product.product_id}`} value={product.product_id}>{product.product_name}</option>)}
                </select>
                <input type="number" min="1" placeholder="Quantity" value={purchaseForm.quantity} onChange={(event) => setPurchaseForm({ ...purchaseForm, quantity: event.target.value })} required />
                <input type="number" min="0.01" step="0.01" placeholder="Unit cost" value={purchaseForm.unit_cost} onChange={(event) => setPurchaseForm({ ...purchaseForm, unit_cost: event.target.value })} required />
                <button type="submit" disabled={loading}>Add purchase</button>
              </form>
              <form onSubmit={(event) => handleTransaction('sale', event)} className="transaction-form sale-form">
                <h3>Record Sale</h3>
                <select value={saleForm.product_id} onChange={(event) => setSaleForm({ ...saleForm, product_id: event.target.value })} required>
                  <option value="">Select product</option>
                  {profitLossProducts.map(product => <option key={`sell-${product.product_id}`} value={product.product_id}>{product.product_name}</option>)}
                </select>
                <input type="number" min="1" placeholder="Quantity" value={saleForm.quantity} onChange={(event) => setSaleForm({ ...saleForm, quantity: event.target.value })} required />
                <input type="number" min="0.01" step="0.01" placeholder="Selling price" value={saleForm.unit_price} onChange={(event) => setSaleForm({ ...saleForm, unit_price: event.target.value })} required />
                <button type="submit" disabled={loading}>Add sale</button>
              </form>
            </div>
            <div className="profit-chart-panel">
              <div className="chart-heading">
                <div>
                  <h3>Profit / Loss by Product</h3>
                  <p>Bars extend right for profit and left for loss.</p>
                </div>
                <div className="chart-legend">
                  <span><i className="legend-dot profit-dot"></i>Profit</span>
                  <span><i className="legend-dot loss-dot"></i>Loss</span>
                </div>
              </div>
              {chartProducts.length === 0 ? (
                <div className="chart-empty-state">
                  <strong>Graph unavailable</strong>
                  <span>Add a supplier mapping or purchase order cost to calculate product profit and loss.</span>
                </div>
              ) : (
                <div className="profit-chart" role="img" aria-label="Product profit and loss bar graph">
                  {chartProducts.map(product => {
                    const value = product.profit_loss;
                    const width = `${(Math.abs(value) / chartMax) * 50}%`;
                    return (
                      <div className="chart-row" key={`chart-${product.product_id}`}>
                        <span className="chart-product-name" title={product.product_name}>{product.product_name}</span>
                        <div className="chart-track">
                          <div className={`chart-bar ${value >= 0 ? 'chart-profit' : 'chart-loss'}`} style={{ width }}>
                            <span>₹{Math.abs(value).toLocaleString('en-IN')}</span>
                          </div>
                        </div>
                        <span className={`chart-value ${value >= 0 ? 'profit-text' : 'loss-text'}`}>{value >= 0 ? '+' : '-'}₹{Math.abs(value).toLocaleString('en-IN')}</span>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
            <div className="profit-loss-table-wrap">
              <table className="profit-loss-table">
                <thead>
                  <tr>
                    <th>Product</th>
                    <th>Stock</th>
                    <th>Sell / Unit</th>
                    <th>Cost / Unit</th>
                    <th>Profit / Loss</th>
                    <th>Margin</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {summaryData.profit_loss.products.map(product => (
                    <tr key={product.product_id}>
                      <td><strong>{product.product_name}</strong><small>{product.basis || product.cost_source || 'Supplier cost not recorded'}</small></td>
                      <td>{product.current_stock}</td>
                      <td>₹{product.selling_price.toLocaleString('en-IN')}</td>
                      <td>{product.unit_cost === null ? 'N/A' : `₹${product.unit_cost.toLocaleString('en-IN')}`}</td>
                      <td className={product.profit_loss === null ? '' : product.profit_loss >= 0 ? 'profit-text' : 'loss-text'}>
                        {product.profit_loss === null ? 'N/A' : `₹${product.profit_loss.toLocaleString('en-IN')}`}
                      </td>
                      <td>{product.margin_percent === null ? 'N/A' : `${product.margin_percent}%`}</td>
                      <td><span className={`profit-status ${product.status.toLowerCase().replace(' ', '-')}`}>{product.status}</span></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="transaction-history-section">
              <div className="section-heading">
                <div>
                  <h3>Transaction History</h3>
                  <p>Latest purchase and sale records used in the analysis.</p>
                </div>
                <strong>{summaryData.profit_loss.transactions.total_purchases + summaryData.profit_loss.transactions.total_sales} records</strong>
              </div>
              <div className="profit-loss-table-wrap">
                <table className="profit-loss-table history-table">
                  <thead>
                    <tr>
                      <th>Date</th>
                      <th>Type</th>
                      <th>Product</th>
                      <th>Quantity</th>
                      <th>Unit Amount</th>
                      <th>Total</th>
                    </tr>
                  </thead>
                  <tbody>
                    {summaryData.profit_loss.transactions.history.length === 0 ? (
                      <tr><td colSpan="6" className="history-empty">No purchase or sale history recorded.</td></tr>
                    ) : summaryData.profit_loss.transactions.history.map(transaction => (
                      <tr key={`${transaction.type}-${transaction.id}`}>
                        <td>{transaction.transaction_date ? new Date(transaction.transaction_date).toLocaleString('en-IN') : 'N/A'}</td>
                        <td><span className={`transaction-type ${transaction.type.toLowerCase()}`}>{transaction.type}</span></td>
                        <td>{transaction.product_name}</td>
                        <td>{transaction.quantity}</td>
                        <td>₹{transaction.unit_amount.toLocaleString('en-IN')}</td>
                        <td className={transaction.type === 'SALE' ? 'profit-text' : 'loss-text'}>₹{transaction.total_amount.toLocaleString('en-IN')}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
      </main>

      <NotificationCenter 
        isOpen={notificationPanelOpen}
        onClose={() => setNotificationPanelOpen(false)}
      />
    </div>
  );
}

export default Dashboard;
