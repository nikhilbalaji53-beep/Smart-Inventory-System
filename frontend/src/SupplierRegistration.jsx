import { useState } from 'react';
import { api } from './api';
import './SupplierRegistration.css';

function SupplierRegistration({ onRegistrationSuccess, onSwitchToLogin }) {
  const [formData, setFormData] = useState({
    companyName: '',
    contactPerson: '',
    email: '',
    phone: '',
    address: '',
    gstNumber: '',
    password: '',
    confirmPassword: ''
  });

  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);
  const [passwordStrength, setPasswordStrength] = useState('');

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));

    // Update password strength indicator
    if (name === 'password') {
      setPasswordStrength(getPasswordStrength(value));
    }
  };

  const getPasswordStrength = (password) => {
    if (!password) return '';
    
    let strength = 0;
    if (password.length >= 8) strength++;
    if (password.length >= 12) strength++;
    if (/[a-z]/.test(password) && /[A-Z]/.test(password)) strength++;
    if (/\d/.test(password)) strength++;
    if (/[!@#$%^&*]/.test(password)) strength++;

    if (strength <= 1) return 'weak';
    if (strength <= 2) return 'fair';
    if (strength <= 3) return 'good';
    if (strength <= 4) return 'strong';
    return 'very-strong';
  };

  const validateForm = () => {
    if (!formData.companyName.trim()) {
      setError('Company name is required');
      return false;
    }
    if (!formData.contactPerson.trim()) {
      setError('Contact person name is required');
      return false;
    }
    if (!formData.email.trim() || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      setError('Valid email address is required');
      return false;
    }
    if (!formData.phone.trim() || !/^\d{10}$/.test(formData.phone.replace(/\D/g, ''))) {
      setError('Valid phone number (10 digits) is required');
      return false;
    }
    if (!formData.address.trim()) {
      setError('Address is required');
      return false;
    }
    if (!formData.gstNumber.trim()) {
      setError('GST/Business registration number is required');
      return false;
    }
    if (!formData.password || formData.password.length < 8) {
      setError('Password must be at least 8 characters long');
      return false;
    }
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return false;
    }

    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    if (!validateForm()) {
      setLoading(false);
      return;
    }

    try {
      // Generate supplier ID from company name (simplified)
      const supplierId = `sup_${Date.now()}_${Math.random().toString(36).substr(2, 5)}`;

      // Debug log the request data
      console.log('Submitting registration with data:', {
        supplier_id: supplierId,
        email: formData.email,
        company_name: formData.companyName,
        contact_person: formData.contactPerson,
        password: '***',
        phone: formData.phone,
        address: formData.address,
        gst_number: formData.gstNumber
      });

      const response = await api.supplierRegister(
        supplierId,
        formData.email,
        formData.companyName,
        formData.password,
        formData.phone,
        formData.address,
        formData.contactPerson,
        formData.gstNumber
      );

      console.log('Registration response:', response);

      if (response.error) {
        setError(`Registration failed: ${response.error}`);
      } else if (response.detail) {
        setError(`Registration failed: ${response.detail}`);
      } else if (response.supplier_id || response.id) {
        setSuccess('✅ Registration successful! Your account has been created. Please log in with your credentials.');
        
        // Store the registered supplier ID for auto-fill on login
        localStorage.setItem('registered_supplier_id', supplierId);
        localStorage.setItem('registered_supplier_email', formData.email);

        // Reset form
        setFormData({
          companyName: '',
          contactPerson: '',
          email: '',
          phone: '',
          address: '',
          gstNumber: '',
          password: '',
          confirmPassword: ''
        });

        // Redirect to login after 2 seconds
        setTimeout(() => {
          onSwitchToLogin();
        }, 2000);
      } else {
        setError('Registration failed. Please try again.');
      }
    } catch (err) {
      console.error('Registration error:', err);
      setError(err.message || 'An error occurred during registration');
    } finally {
      setLoading(false);
    }
  };

  const getStrengthColor = () => {
    switch (passwordStrength) {
      case 'weak': return '#ff4444';
      case 'fair': return '#ffaa00';
      case 'good': return '#4da6ff';
      case 'strong': return '#66cc66';
      case 'very-strong': return '#00aa00';
      default: return '#cccccc';
    }
  };

  return (
    <div className="registration-shell">
      <div className="registration-card">
        <div className="registration-header">
          <h1 className="registration-title">🚚 SUPPLIER REGISTRATION</h1>
          <p className="registration-subtitle">Join our supplier network and start managing orders</p>
        </div>

        <form onSubmit={handleSubmit} className="registration-form">
          {error && <div className="registration-error">{error}</div>}
          {success && <div className="registration-success">{success}</div>}

          {/* Company Name */}
          <div className="field-group full-width">
            <label htmlFor="companyName">Company / Supplier Name</label>
            <input
              id="companyName"
              name="companyName"
              type="text"
              value={formData.companyName}
              onChange={handleInputChange}
              placeholder="Enter company name"
              required
            />
          </div>

          {/* Contact Person */}
          <div className="field-group full-width">
            <label htmlFor="contactPerson">Contact Person</label>
            <input
              id="contactPerson"
              name="contactPerson"
              type="text"
              value={formData.contactPerson}
              onChange={handleInputChange}
              placeholder="Enter contact person name"
              required
            />
          </div>

          {/* Email and Phone - Side by side */}
          <div className="field-row">
            <div className="field-group">
              <label htmlFor="email">Email</label>
              <input
                id="email"
                name="email"
                type="email"
                value={formData.email}
                onChange={handleInputChange}
                placeholder="your@email.com"
                required
              />
            </div>

            <div className="field-group">
              <label htmlFor="phone">Phone Number</label>
              <input
                id="phone"
                name="phone"
                type="tel"
                value={formData.phone}
                onChange={handleInputChange}
                placeholder="10-digit phone number"
                maxLength="15"
                required
              />
            </div>
          </div>

          {/* Address */}
          <div className="field-group full-width">
            <label htmlFor="address">Address</label>
            <textarea
              id="address"
              name="address"
              value={formData.address}
              onChange={handleInputChange}
              placeholder="Enter complete supplier address"
              rows="2"
              required
            />
          </div>

          {/* GST Number */}
          <div className="field-group full-width">
            <label htmlFor="gstNumber">Business / GST Registration Number</label>
            <input
              id="gstNumber"
              name="gstNumber"
              type="text"
              value={formData.gstNumber}
              onChange={handleInputChange}
              placeholder="e.g., 27AABCT1234H1Z0"
              required
            />
          </div>

          {/* Password */}
          <div className="field-group full-width">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              name="password"
              type="password"
              value={formData.password}
              onChange={handleInputChange}
              placeholder="Create a secure password"
              required
            />
            {formData.password && (
              <div className="password-strength-container">
                <div className="password-strength-bar">
                  <div
                    className={`password-strength-fill strength-${passwordStrength}`}
                    style={{
                      width: passwordStrength === 'weak' ? '20%' :
                             passwordStrength === 'fair' ? '40%' :
                             passwordStrength === 'good' ? '60%' :
                             passwordStrength === 'strong' ? '80%' :
                             '100%'
                    }}
                  />
                </div>
                <span className={`password-strength-text strength-${passwordStrength}`}>
                  Strength: {passwordStrength.charAt(0).toUpperCase() + passwordStrength.slice(1)}
                </span>
              </div>
            )}
          </div>

          {/* Confirm Password */}
          <div className="field-group full-width">
            <label htmlFor="confirmPassword">Confirm Password</label>
            <input
              id="confirmPassword"
              name="confirmPassword"
              type="password"
              value={formData.confirmPassword}
              onChange={handleInputChange}
              placeholder="Confirm your password"
              required
            />
            {formData.confirmPassword && formData.password !== formData.confirmPassword && (
              <div className="password-mismatch">❌ Passwords do not match</div>
            )}
            {formData.confirmPassword && formData.password === formData.confirmPassword && (
              <div className="password-match">✅ Passwords match</div>
            )}
          </div>

          {/* Submit Button */}
          <button type="submit" className="registration-button" disabled={loading}>
            {loading ? 'Creating Account...' : 'CREATE ACCOUNT'}
          </button>
        </form>

        {/* Login Link */}
        <div className="registration-footer">
          <p>Already registered?</p>
          <button
            type="button"
            className="login-link"
            onClick={onSwitchToLogin}
            disabled={loading}
          >
            [ LOGIN ]
          </button>
        </div>
      </div>
    </div>
  );
}

export default SupplierRegistration;
