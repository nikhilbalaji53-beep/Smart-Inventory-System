import { useState } from 'react';
import { api } from './api';
import './SupplierLogin.css';

function SupplierLogin({ onLoginSuccess }) {
  const [isLogin, setIsLogin] = useState(true);
  const [supplierId, setSupplierId] = useState('');
  const [email, setEmail] = useState('');
  const [companyName, setCompanyName] = useState('');
  const [password, setPassword] = useState('');
  const [phone, setPhone] = useState('');
  const [address, setAddress] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (isLogin) {
        // Supplier Login
        const response = await api.supplierLogin(supplierId || email, password);
        if (response.access_token) {
          localStorage.setItem('supplier_token', response.access_token);
          localStorage.setItem('supplier_id', response.supplier_id);
          localStorage.setItem('company_name', response.company_name);
          localStorage.setItem('is_approved', response.is_approved);
          localStorage.setItem('user_type', 'supplier');
          
          if (rememberMe) {
            localStorage.setItem('remember_supplier', supplierId || email);
          }
          
          onLoginSuccess();
        } else {
          setError(response.detail || 'Login failed');
        }
      } else {
        // Supplier Registration
        const response = await api.supplierRegister(
          supplierId,
          email,
          companyName,
          password,
          phone,
          address
        );
        
        if (response.id) {
          setError('');
          setIsLogin(true);
          setSupplierId('');
          setEmail('');
          setCompanyName('');
          setPassword('');
          setPhone('');
          setAddress('');
          alert('Registration successful! Awaiting admin approval. Please login to check status.');
        } else {
          setError(response.detail || 'Registration failed');
        }
      }
    } catch (err) {
      setError(err.message || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleForgotPassword = () => {
    alert('Password reset feature coming soon. Please contact admin.');
  };

  return (
    <div className="supplier-login-container">
      <div className="supplier-login-box">
        <div className="supplier-logo">
          <h1>SMART INVENTORY SYSTEM</h1>
          <p>Supplier Portal</p>
        </div>

        {error && <div className="error-message">{error}</div>}

        <form onSubmit={handleSubmit}>
          {isLogin ? (
            // Login Form
            <>
              <div className="form-group">
                <label>Supplier ID / Email</label>
                <input
                  type="text"
                  value={supplierId || email}
                  onChange={(e) => setSupplierId(e.target.value) || setEmail(e.target.value)}
                  required
                  placeholder="Enter Supplier ID or Email"
                  className="login-input"
                />
              </div>

              <div className="form-group">
                <label>Password</label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  placeholder="••••••••••••••"
                  className="login-input"
                />
              </div>

              <div className="remember-forgot">
                <div className="remember-me">
                  <input
                    type="checkbox"
                    id="rememberMe"
                    checked={rememberMe}
                    onChange={(e) => setRememberMe(e.target.checked)}
                  />
                  <label htmlFor="rememberMe">Remember Me</label>
                </div>
              </div>

              <button type="submit" disabled={loading} className="login-button">
                {loading ? 'Logging in...' : 'LOGIN'}
              </button>

              <div className="forgot-password">
                <button
                  type="button"
                  onClick={handleForgotPassword}
                  className="forgot-password-link"
                >
                  Forgot Password?
                </button>
              </div>
            </>
          ) : (
            // Registration Form
            <>
              <div className="form-group">
                <label>Supplier ID</label>
                <input
                  type="text"
                  value={supplierId}
                  onChange={(e) => setSupplierId(e.target.value)}
                  required
                  placeholder="Enter unique Supplier ID (3-50 characters)"
                  className="login-input"
                />
              </div>

              <div className="form-group">
                <label>Company Name</label>
                <input
                  type="text"
                  value={companyName}
                  onChange={(e) => setCompanyName(e.target.value)}
                  required
                  placeholder="Enter your company name"
                  className="login-input"
                />
              </div>

              <div className="form-group">
                <label>Email</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  placeholder="Enter your email"
                  className="login-input"
                />
              </div>

              <div className="form-group">
                <label>Password</label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  placeholder="Enter password (min 8 chars with uppercase, lowercase, digit, special char)"
                  className="login-input"
                />
              </div>

              <div className="form-group">
                <label>Phone</label>
                <input
                  type="tel"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  placeholder="Enter phone number"
                  className="login-input"
                />
              </div>

              <div className="form-group">
                <label>Address</label>
                <textarea
                  value={address}
                  onChange={(e) => setAddress(e.target.value)}
                  placeholder="Enter company address"
                  className="login-input"
                  rows="3"
                />
              </div>

              <button type="submit" disabled={loading} className="login-button">
                {loading ? 'Registering...' : 'REGISTER'}
              </button>
            </>
          )}
        </form>

        <div className="toggle-auth">
          {isLogin ? (
            <>
              Don't have an account?{' '}
              <button
                type="button"
                onClick={() => {
                  setIsLogin(false);
                  setError('');
                }}
                className="toggle-button"
              >
                Register here
              </button>
            </>
          ) : (
            <>
              Already have an account?{' '}
              <button
                type="button"
                onClick={() => {
                  setIsLogin(true);
                  setError('');
                }}
                className="toggle-button"
              >
                Login here
              </button>
            </>
          )}
        </div>

        <div className="portal-info">
          <p>📦 Manage your product supplies</p>
          <p>📊 Track order status</p>
          <p>💬 Communicate with inventory managers</p>
        </div>
      </div>
    </div>
  );
}

export default SupplierLogin;
