import { useState, useEffect } from 'react'
import './App.css'
import Login from './Login'
import Dashboard from './Dashboard'
import SupplierDashboard from './SupplierDashboard'

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [userType, setUserType] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const adminToken = localStorage.getItem('token')
    const supplierToken = localStorage.getItem('supplier_token')

    if (adminToken) {
      setUserType('admin')
      setIsLoggedIn(true)
    } else if (supplierToken) {
      setUserType('supplier')
      setIsLoggedIn(true)
    }

    setLoading(false)
  }, [])

  const handleLoginSuccess = (role) => {
    setUserType(role)
    setIsLoggedIn(true)
  }

  const handleLogout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('username')
    localStorage.removeItem('is_admin')
    localStorage.removeItem('supplier_token')
    localStorage.removeItem('supplier_id')
    localStorage.removeItem('company_name')
    localStorage.removeItem('is_approved')
    localStorage.removeItem('user_type')
    setIsLoggedIn(false)
    setUserType(null)
  }

  if (loading) {
    return <div className="loading-screen">Loading...</div>
  }

  if (isLoggedIn) {
    if (userType === 'supplier') {
      return <SupplierDashboard onLogout={handleLogout} />
    }
    return <Dashboard onLogout={handleLogout} userType={userType} />
  }

  return <Login onLoginSuccess={handleLoginSuccess} />
}

export default App
