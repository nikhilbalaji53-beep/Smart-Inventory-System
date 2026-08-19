import React, { useState } from 'react';
import { 
  LayoutDashboard, 
  Package, 
  AlertTriangle, 
  Settings, 
  LogOut, 
  ChevronDown,
  Menu,
  X
} from 'lucide-react';

export const Sidebar = ({ activeTab, onTabChange, onLogout, username }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);

  const navItems = [
    { id: 'overview', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'products', label: 'Products', icon: Package },
    { id: 'alerts', label: 'Alerts', icon: AlertTriangle },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  const handleNavClick = (tab) => {
    onTabChange(tab);
    setIsOpen(false);
  };

  return (
    <>
      {/* Mobile menu button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed top-4 left-4 z-50 lg:hidden p-2 rounded-lg hover:bg-slate-100"
      >
        {isOpen ? <X size={24} /> : <Menu size={24} />}
      </button>

      {/* Overlay for mobile */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setIsOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div
        className={`fixed left-0 top-0 h-screen w-64 bg-slate-900 text-slate-300 z-40 transition-transform duration-300 lg:translate-x-0 ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        } flex flex-col`}
      >
        {/* Brand/Logo */}
        <div className="px-6 py-8 border-b border-slate-700">
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <Package size={24} className="text-indigo-400" />
            <span>Inventory Pro</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">Smart Inventory System</p>
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto px-3 py-6 space-y-2">
          {navItems.map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              onClick={() => handleNavClick(id)}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg font-medium transition-all ${
                activeTab === id
                  ? 'bg-indigo-600/10 text-indigo-400 border-r-2 border-indigo-500'
                  : 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-200'
              }`}
            >
              <Icon size={20} />
              <span>{label}</span>
            </button>
          ))}
        </nav>

        {/* User Profile Section */}
        <div className="border-t border-slate-700 p-4">
          <div className="relative">
            <button
              onClick={() => setShowUserMenu(!showUserMenu)}
              className="w-full flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-slate-800/50 transition-colors"
            >
              <div className="w-10 h-10 rounded-full bg-indigo-600 flex items-center justify-center text-white font-bold text-sm">
                {username?.charAt(0).toUpperCase() || 'U'}
              </div>
              <div className="flex-1 text-left min-w-0">
                <p className="text-sm font-medium text-white truncate">{username || 'User'}</p>
                <p className="text-xs text-slate-400">Admin</p>
              </div>
              <ChevronDown size={16} />
            </button>

            {/* User dropdown menu */}
            {showUserMenu && (
              <div className="absolute bottom-full left-0 right-0 mb-2 bg-slate-800 border border-slate-700 rounded-lg shadow-lg overflow-hidden">
                <button
                  onClick={() => {
                    onLogout();
                    setShowUserMenu(false);
                  }}
                  className="w-full flex items-center gap-2 px-4 py-3 text-sm text-slate-300 hover:bg-slate-700 hover:text-white transition-colors"
                >
                  <LogOut size={16} />
                  <span>Logout</span>
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  );
};

export default Sidebar;
