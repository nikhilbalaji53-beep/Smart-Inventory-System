// Use backend URL consistently
const API_BASE_URL = 'http://localhost:8000';

const getAuthToken = () => {
  return localStorage.getItem('token');
};

const getAuthHeader = () => {
  const token = getAuthToken();
  return {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Bearer ${token}` })
  };
};

export const api = {
  // Admin Authentication
  register: async (username, email, password) => {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, email, password })
    });
    return response.json();
  },

  login: async (username, password) => {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });
    return response.json();
  },

  getCurrentUser: async () => {
    const response = await fetch(`${API_BASE_URL}/auth/me`, {
      headers: getAuthHeader()
    });
    if (!response.ok) throw new Error('Failed to fetch user');
    return response.json();
  },

  // Supplier Authentication
  supplierRegister: async (supplierId, email, companyName, password, phone, address, contactPerson = '', gstNumber = '') => {
    const response = await fetch(`${API_BASE_URL}/supplier/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        supplier_id: supplierId,
        email,
        company_name: companyName,
        contact_person: contactPerson,
        password,
        phone,
        address,
        gst_number: gstNumber
      })
    });
    
    const data = await response.json();
    
    // If response is not ok, ensure error is propagated
    if (!response.ok) {
      console.error(`Registration API error (${response.status}):`, data);
      return data; // Return the error response so frontend can handle it
    }
    
    return data;
  },

  supplierLogin: async (supplierIdOrEmail, password) => {
    const response = await fetch(`${API_BASE_URL}/supplier/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        supplier_id_or_email: supplierIdOrEmail,
        password
      })
    });
    return response.json();
  },

  getSupplierProfile: async () => {
    const token = localStorage.getItem('supplier_token');
    const response = await fetch(`${API_BASE_URL}/supplier/profile`, {
      headers: {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` })
      }
    });
    if (!response.ok) throw new Error('Failed to fetch supplier profile');
    return response.json();
  },

  getSupplierStatus: async (supplierId) => {
    const response = await fetch(`${API_BASE_URL}/supplier/status/${supplierId}`, {
      headers: { 'Content-Type': 'application/json' }
    });
    if (!response.ok) throw new Error('Failed to fetch supplier status');
    return response.json();
  },

  getPendingSuppliers: async () => {
    const response = await fetch(`${API_BASE_URL}/supplier/pending`, {
      headers: { 'Content-Type': 'application/json' }
    });
    if (!response.ok) throw new Error('Failed to fetch pending suppliers');
    return response.json();
  },

  getAllSuppliers: async () => {
    const response = await fetch(`${API_BASE_URL}/supplier/all`, {
      headers: { 'Content-Type': 'application/json' }
    });
    if (!response.ok) throw new Error('Failed to fetch supplier list');
    return response.json();
  },

  approveSupplier: async (supplierId, status = 'approved') => {
    const response = await fetch(`${API_BASE_URL}/supplier/approve/${supplierId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status })
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || 'Failed to update supplier approval');
    }
    return data;
  },

  // Products
  getProducts: async () => {
    const response = await fetch(`${API_BASE_URL}/products/`, {
      headers: getAuthHeader()
    });
    if (!response.ok) throw new Error('Failed to fetch products');
    return response.json();
  },

  getProduct: async (productId) => {
    const response = await fetch(`${API_BASE_URL}/products/${productId}`, {
      headers: getAuthHeader()
    });
    if (!response.ok) throw new Error('Failed to fetch product');
    return response.json();
  },

  createProduct: async (productData) => {
    const response = await fetch(`${API_BASE_URL}/products/`, {
      method: 'POST',
      headers: getAuthHeader(),
      body: JSON.stringify(productData)
    });
    if (!response.ok) throw new Error('Failed to create product');
    return response.json();
  },

  updateProduct: async (productId, productData) => {
    const response = await fetch(`${API_BASE_URL}/products/${productId}`, {
      method: 'PUT',
      headers: getAuthHeader(),
      body: JSON.stringify(productData)
    });
    if (!response.ok) throw new Error('Failed to update product');
    return response.json();
  },

  updateStock: async (productId, quantity) => {
    const response = await fetch(`${API_BASE_URL}/products/${productId}/stock`, {
      method: 'PATCH',
      headers: getAuthHeader(),
      body: JSON.stringify({ quantity })
    });
    if (!response.ok) throw new Error('Failed to update stock');
    return response.json();
  },

  deleteProduct: async (productId) => {
    const response = await fetch(`${API_BASE_URL}/products/${productId}`, {
      method: 'DELETE',
      headers: getAuthHeader()
    });
    if (!response.ok) throw new Error('Failed to delete product');
    return response.json();
  },

  // Dashboard
  getDashboard: async () => {
    const response = await fetch(`${API_BASE_URL}/dashboard/`, {
      headers: getAuthHeader()
    });
    if (!response.ok) throw new Error('Failed to fetch dashboard');
    return response.json();
  },

  getDashboardSummary: async () => {
    const response = await fetch(`${API_BASE_URL}/dashboard/summary`, {
      headers: getAuthHeader()
    });
    if (!response.ok) throw new Error('Failed to fetch dashboard summary');
    return response.json();
  },

  recordPurchase: async (purchaseData) => {
    const response = await fetch(`${API_BASE_URL}/transactions/purchase`, {
      method: 'POST',
      headers: getAuthHeader(),
      body: JSON.stringify(purchaseData)
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Failed to record purchase');
    return data;
  },

  recordSale: async (saleData) => {
    const response = await fetch(`${API_BASE_URL}/transactions/sale`, {
      method: 'POST',
      headers: getAuthHeader(),
      body: JSON.stringify(saleData)
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Failed to record sale');
    return data;
  },

  // Alerts
  getAlerts: async () => {
    const response = await fetch(`${API_BASE_URL}/alerts/`, {
      headers: getAuthHeader()
    });
    if (!response.ok) throw new Error('Failed to fetch alerts');
    return response.json();
  },

  // Expiry
  getExpiryAlerts: async (daysUntilExpiry = 7) => {
    const response = await fetch(`${API_BASE_URL}/expiry/alerts?days_until_expiry=${daysUntilExpiry}`, {
      headers: getAuthHeader()
    });
    if (!response.ok) throw new Error('Failed to fetch expiry alerts');
    return response.json();
  },

  getExpiringProducts: async () => {
    const response = await fetch(`${API_BASE_URL}/expiry/expiring-soon`, {
      headers: getAuthHeader()
    });
    if (!response.ok) throw new Error('Failed to fetch expiring products');
    return response.json();
  },

  getExpiredProducts: async () => {
    const response = await fetch(`${API_BASE_URL}/expiry/expired`, {
      headers: getAuthHeader()
    });
    if (!response.ok) throw new Error('Failed to fetch expired products');
    return response.json();
  },

  // Predictions
  getPredictions: async (productId, days = 7) => {
    const response = await fetch(`${API_BASE_URL}/predictions/${productId}?days=${days}`, {
      headers: getAuthHeader()
    });
    if (!response.ok) throw new Error('Failed to fetch predictions');
    return response.json();
  }
};
