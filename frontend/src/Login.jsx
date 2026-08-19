import { useState } from 'react';
import { api } from './api';
import './Login.css';
import SupplierRegistration from './SupplierRegistration';

function Login({ onLoginSuccess }) {
  const [showRegistration, setShowRegistration] = useState(false);
  const [portal, setPortal] = useState('admin');
  const [identifier, setIdentifier] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      let response;

      if (portal === 'admin') {
        response = await api.login(identifier, password);
        if (response.access_token) {
          localStorage.removeItem('supplier_token');
          localStorage.removeItem('supplier_id');
          localStorage.removeItem('company_name');
          localStorage.removeItem('is_approved');
          localStorage.setItem('token', response.access_token);
          localStorage.setItem('username', response.username || identifier);
          localStorage.setItem('user_type', 'admin');
          if (response.is_admin !== undefined) {
            localStorage.setItem('is_admin', String(response.is_admin));
          }
          if (rememberMe) {
            localStorage.setItem('remembered_admin', identifier);
          }
          onLoginSuccess('admin');
          return;
        }
      } else {
        response = await api.supplierLogin(identifier, password);
        if (response.access_token) {
          localStorage.removeItem('token');
          localStorage.removeItem('username');
          localStorage.removeItem('is_admin');
          localStorage.setItem('supplier_token', response.access_token);
          localStorage.setItem('supplier_id', response.supplier_id || identifier);
          localStorage.setItem('company_name', response.company_name || '');
          localStorage.setItem('user_type', 'supplier');
          if (response.is_approved !== undefined) {
            localStorage.setItem('is_approved', String(response.is_approved));
          }
          if (rememberMe) {
            localStorage.setItem('remembered_supplier', identifier);
          }
          onLoginSuccess('supplier');
          return;
        }
      }

      setError(response?.detail || 'Login failed. Please check your credentials.');
    } catch (err) {
      setError(err.message || 'An error occurred while logging in.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {showRegistration ? (
        <SupplierRegistration
          onRegistrationSuccess={onLoginSuccess}
          onSwitchToLogin={() => setShowRegistration(false)}
        />
      ) : (
        <div className="login-shell">
          <div className="login-card">
            <div className="brand-panel">
              <div className="brand-content">
                <div className="brand-title">SMART INVENTORY</div>
                <div className="brand-title secondary">MANAGEMENT SYSTEM</div>

                <div className="feature-list">
                  <div className="feature-item">📦 Stock Management</div>
                  <div className="feature-item">📊 Prediction</div>
                  <div className="feature-item">🔔 Automated Alerts</div>
                </div>

                <div className="illustration-box">
                  <div className="illustration-pill"></div>
                  <div className="illustration-bar bar-one"></div>
                  <div className="illustration-bar bar-two"></div>
                  <div className="illustration-bar bar-three"></div>
                </div>
              </div>
            </div>

            <div className="form-panel">
              <div className="welcome-text">Welcome Back</div>

              <div className="portal-toggle" role="tablist" aria-label="Portal switcher">
                <button
                  type="button"
                  className={portal === 'admin' ? 'portal-btn active' : 'portal-btn'}
                  onClick={() => setPortal('admin')}
                >
                  ADMIN
                </button>
                <button
                  type="button"
                  className={portal === 'supplier' ? 'portal-btn active' : 'portal-btn'}
                  onClick={() => setPortal('supplier')}
                >
                  SUPPLIER
                </button>
              </div>

              <form onSubmit={handleSubmit} className="login-form">
                {error && <div className="error-message">{error}</div>}

                <div className="field-group">
                  <label htmlFor="identifier">{portal === 'admin' ? 'Email / Username' : 'Email / Supplier ID'}</label>
                  <input
                    id="identifier"
                    type="text"
                    value={identifier}
                    onChange={(e) => setIdentifier(e.target.value)}
                    placeholder={portal === 'admin' ? 'Enter email or username' : 'Enter supplier ID or email'}
                    required
                  />
                </div>

                <div className="field-group">
                  <label htmlFor="password">Password</label>
                  <input
                    id="password"
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••••••••"
                    required
                  />
                </div>

                <label className="remember-row">
                  <input
                    type="checkbox"
                    checked={rememberMe}
                    onChange={(e) => setRememberMe(e.target.checked)}
                  />
                  <span>Remember Me</span>
                </label>

                <button type="submit" className="login-button" disabled={loading}>
                  {loading ? 'Logging in...' : 'LOGIN'}
                </button>
              </form>

              <div className="login-footer">
                <button type="button" className="forgot-link" onClick={() => setError('Password reset is not available yet. Please contact the admin.')}>Forgot Password?</button>
                
                {portal === 'supplier' && (
                  <button type="button" className="register-link" onClick={() => setShowRegistration(true)}>
                    Create Account
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

export default Login;
