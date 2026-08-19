import React, { useState, useEffect } from 'react';
import { 
  Search, 
  Bell, 
  Plus,
  Loader
} from 'lucide-react';

export const Header = ({ unreadCount = 0, onNotificationClick, onAddProductClick }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [isSearchOpen, setIsSearchOpen] = useState(false);

  // Handle Cmd/Ctrl + K shortcut
  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setIsSearchOpen(true);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  return (
    <div className="sticky top-0 z-30 h-16 bg-white/80 backdrop-blur-md border-b border-slate-200 flex items-center px-6 gap-4">
      {/* Left: Search */}
      <div className="flex-1 max-w-md">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400" size={18} />
          <input
            type="text"
            placeholder="Search products, categories..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onFocus={() => setIsSearchOpen(true)}
            onBlur={() => setTimeout(() => setIsSearchOpen(false), 200)}
            className="w-full pl-10 pr-4 py-2 bg-slate-50 border border-slate-300 rounded-lg text-sm placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all"
          />
          <div className="absolute right-3 top-1/2 transform -translate-y-1/2 text-xs text-slate-400 pointer-events-none hidden sm:block">
            ⌘K
          </div>
        </div>

        {/* Search results dropdown */}
        {isSearchOpen && searchQuery && (
          <div className="absolute top-full left-0 right-0 mt-2 bg-white border border-slate-200 rounded-lg shadow-lg p-2 z-50">
            <div className="text-sm text-slate-500 p-3">
              Searching for "{searchQuery}"...
            </div>
          </div>
        )}
      </div>

      {/* Right: Actions */}
      <div className="flex items-center gap-3">
        {/* Notification Bell */}
        <button
          onClick={onNotificationClick}
          className="relative p-2 rounded-lg hover:bg-slate-100 transition-colors"
        >
          <Bell size={20} className="text-slate-600" />
          {unreadCount > 0 && (
            <span className="absolute top-1 right-1 w-5 h-5 bg-rose-500 text-white text-xs font-bold rounded-full flex items-center justify-center">
              {unreadCount > 9 ? '9+' : unreadCount}
            </span>
          )}
        </button>

        {/* Add Product Button */}
        <button
          onClick={onAddProductClick}
          className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 transition-colors shadow-sm"
        >
          <Plus size={18} />
          <span className="hidden sm:inline">New Product</span>
        </button>
      </div>
    </div>
  );
};

export default Header;
