import { useState, useEffect } from 'react';
import { api } from './api';
import { playAlertSound, showDesktopNotification, requestNotificationPermissions } from './utils/audioNotification';
import './Alerts.css';

function Alerts() {
  const [activeTab, setActiveTab] = useState('stock');
  const [stockAlerts, setStockAlerts] = useState(null);
  const [expiryAlerts, setExpiryAlerts] = useState(null);
  const [expiringProducts, setExpiringProducts] = useState(null);
  const [expiredProducts, setExpiredProducts] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [hasPlayedSound, setHasPlayedSound] = useState(false);

  useEffect(() => {
    // Request notification permissions on component mount
    requestNotificationPermissions();
    loadAlerts();
  }, []);

  const loadAlerts = async () => {
    try {
      setLoading(true);
      const [stock, expiry, expiring, expired] = await Promise.all([
        api.getAlerts(),
        api.getExpiryAlerts(),
        api.getExpiringProducts(),
        api.getExpiredProducts()
      ]);

      setStockAlerts(stock);
      setExpiryAlerts(expiry);
      setExpiringProducts(expiring);
      setExpiredProducts(expired);
      setError('');

      // Check for critical alerts and trigger sound/notification
      const hasCriticalAlerts = 
        (stock?.alerts?.some(a => a.severity === 'CRITICAL') || false) ||
        (expiry?.alerts?.some(a => a.severity === 'CRITICAL') || false) ||
        (expiring?.alerts?.some(a => a.severity === 'CRITICAL') || false) ||
        (expired?.alerts?.some(a => a.severity === 'CRITICAL') || false);

      if (hasCriticalAlerts && !hasPlayedSound) {
        // Play critical alert sound
        playAlertSound('critical');
        setHasPlayedSound(true);

        // Count critical products
        const criticalCount = 
          (stock?.alerts?.filter(a => a.severity === 'CRITICAL').length || 0) +
          (expiry?.alerts?.filter(a => a.severity === 'CRITICAL').length || 0) +
          (expiring?.alerts?.filter(a => a.severity === 'CRITICAL').length || 0) +
          (expired?.alerts?.filter(a => a.severity === 'CRITICAL').length || 0);

        // Show desktop notification
        showDesktopNotification(`⚠️ CRITICAL ALERT`, {
          body: `${criticalCount} product(s) in critical position!`,
          tag: 'critical-alert',
          requireInteraction: true
        });
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const AlertCard = ({ alert, type = 'stock' }) => {
    const isWarning = alert.severity === 'WARNING';
    const isCritical = alert.severity === 'CRITICAL';

    return (
      <div className={`alert-card ${isCritical ? 'critical' : 'warning'}`}>
        <div className="alert-icon">
          {isCritical ? '🚨' : '⚠️'}
        </div>
        <div className="alert-details">
          <h4>{alert.product_name}</h4>

          {type === 'stock' && (
            <>
              <p><strong>Current Stock:</strong> {alert.current_stock} units</p>
              <p><strong>Minimum Required:</strong> {alert.minimum_stock} units</p>
              <p><strong>Deficit:</strong> <span className="deficit">{alert.minimum_stock - alert.current_stock} units</span></p>
              <p><strong>7-Day Forecast:</strong> {alert.predicted_7_day_demand} units</p>
              <p><strong>Recommended Reorder:</strong> <span className="reorder">{alert.recommended_reorder_qty} units</span></p>
              <div className="alert-reasons">
                {alert.reasons.map((reason, idx) => (
                  <span key={idx} className="reason-badge">{reason}</span>
                ))}
              </div>
            </>
          )}

          {type === 'expiry' && (
            <>
              <p><strong>Expiry Date:</strong> {alert.expiry_date}</p>
              <p><strong>Days Until Expiry:</strong> <span className={alert.days_until_expiry < 0 ? 'expired' : 'warning'}>{alert.days_until_expiry}</span></p>
              <p><strong>Current Stock:</strong> {alert.current_stock} units</p>
              <p><strong>Status:</strong> <span className="status-badge">{alert.status}</span></p>
            </>
          )}
        </div>
        <div className="alert-severity">
          {alert.severity}
        </div>
      </div>
    );
  };

  if (loading) return <div className="loading">Loading alerts...</div>;

  // Count critical alerts
  const criticalStockCount = stockAlerts?.alerts?.filter(a => a.severity === 'CRITICAL').length || 0;
  const criticalExpiryCount = expiryAlerts?.alerts?.filter(a => a.severity === 'CRITICAL').length || 0;
  const criticalExpiringCount = expiringProducts?.alerts?.filter(a => a.severity === 'CRITICAL').length || 0;
  const criticalExpiredCount = expiredProducts?.alerts?.filter(a => a.severity === 'CRITICAL').length || 0;
  const totalCritical = criticalStockCount + criticalExpiryCount + criticalExpiringCount + criticalExpiredCount;
  const hasCriticalAlerts = totalCritical > 0;

  return (
    <div className="alerts-container">
      <div className="alerts-header">
        <div className="header-left">
          <h2>🚨 System Alerts</h2>
          {hasCriticalAlerts && (
            <div className="critical-badge">
              <span className="pulse">🔴</span>
              <span className="critical-text">{totalCritical} CRITICAL</span>
            </div>
          )}
        </div>
        <div className="header-right">
          <button 
            className="sound-btn"
            onClick={() => playAlertSound('critical')}
            title="Play alert sound"
          >
            🔊 Play Alert
          </button>
          <button 
            className="refresh-btn"
            onClick={loadAlerts}
            title="Refresh alerts"
          >
            🔄 Refresh
          </button>
        </div>
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="alerts-tabs">
        <button
          className={`tab-btn ${activeTab === 'stock' ? 'active' : ''}`}
          onClick={() => setActiveTab('stock')}
        >
          📉 Low Stock Alerts ({stockAlerts?.count || 0})
        </button>
        <button
          className={`tab-btn ${activeTab === 'expiry' ? 'active' : ''}`}
          onClick={() => setActiveTab('expiry')}
        >
          🟠 Expiry Alerts ({expiryAlerts?.count || 0})
        </button>
        <button
          className={`tab-btn ${activeTab === 'expiring' ? 'active' : ''}`}
          onClick={() => setActiveTab('expiring')}
        >
          ⏰ Expiring Soon ({expiringProducts?.count || 0})
        </button>
        <button
          className={`tab-btn ${activeTab === 'expired' ? 'active' : ''}`}
          onClick={() => setActiveTab('expired')}
        >
          💀 Expired ({expiredProducts?.count || 0})
        </button>
      </div>

      <div className="alerts-content">
        {activeTab === 'stock' && (
          <div className="tab-content">
            <h3>Low Stock Products</h3>
            {stockAlerts?.count === 0 ? (
              <div className="no-alerts">✅ No low stock alerts!</div>
            ) : (
              <div className="alerts-grid">
                {stockAlerts?.alerts.map(alert => (
                  <AlertCard key={alert.product_id} alert={alert} type="stock" />
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'expiry' && (
          <div className="tab-content">
            <h3>Expiry Alerts</h3>
            {expiryAlerts?.count === 0 ? (
              <div className="no-alerts">✅ No expiry alerts!</div>
            ) : (
              <div className="alerts-grid">
                {expiryAlerts?.alerts.map(alert => (
                  <AlertCard key={alert.product_id} alert={alert} type="expiry" />
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'expiring' && (
          <div className="tab-content">
            <h3>Products Expiring in Next 7 Days</h3>
            {expiringProducts?.count === 0 ? (
              <div className="no-alerts">✅ No products expiring soon!</div>
            ) : (
              <div className="product-list">
                {expiringProducts?.products.map(product => (
                  <div key={product.product_id} className="product-item warning">
                    <div className="product-info">
                      <h4>{product.product_name}</h4>
                      <p><strong>Category:</strong> {product.category}</p>
                      <p><strong>Expiry Date:</strong> {product.expiry_date}</p>
                      <p><strong>Days Until Expiry:</strong> {product.days_until_expiry}</p>
                      <p><strong>Current Stock:</strong> {product.current_stock} units</p>
                      <p><strong>Price:</strong> ₹{product.price.toFixed(2)}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'expired' && (
          <div className="tab-content">
            <h3>Expired Products</h3>
            {expiredProducts?.count === 0 ? (
              <div className="no-alerts">✅ No expired products!</div>
            ) : (
              <div className="product-list">
                {expiredProducts?.products.map(product => (
                  <div key={product.product_id} className="product-item critical">
                    <div className="product-info">
                      <h4>{product.product_name}</h4>
                      <p><strong>Category:</strong> {product.category}</p>
                      <p><strong>Expiry Date:</strong> {product.expiry_date}</p>
                      <p><strong>Days Since Expiry:</strong> {product.days_expired}</p>
                      <p><strong>Current Stock:</strong> {product.current_stock} units</p>
                      <p><strong>Price:</strong> ₹{product.price.toFixed(2)}</p>
                      <p className="warning-text">⚠️ Remove from inventory immediately</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      <button className="refresh-alerts-btn" onClick={loadAlerts}>
        🔄 Refresh Alerts
      </button>
    </div>
  );
}

export default Alerts;
