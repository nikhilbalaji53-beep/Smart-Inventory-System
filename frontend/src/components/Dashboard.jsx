import React, { useState, useEffect } from 'react';
import { 
  Package, 
  TrendingUp, 
  AlertCircle, 
  Calendar,
  BarChart3,
  RefreshCw,
  Loader
} from 'lucide-react';
import { api } from '../api';

const MetricCard = ({ icon: Icon, label, value, subtitle, trend, color = 'indigo' }) => {
  const colorClasses = {
    indigo: 'bg-indigo-50 text-indigo-600',
    emerald: 'bg-emerald-50 text-emerald-600',
    amber: 'bg-amber-50 text-amber-600',
    rose: 'bg-rose-50 text-rose-600',
  };

  return (
    <div className="card p-6 flex flex-col">
      <div className="flex items-start justify-between mb-4">
        <div>
          <p className="text-sm font-medium text-slate-500 mb-2">{label}</p>
          <h3 className="text-3xl font-bold text-slate-900">{value}</h3>
          {subtitle && <p className="text-xs text-slate-400 mt-1">{subtitle}</p>}
        </div>
        <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${colorClasses[color]}`}>
          <Icon size={24} />
        </div>
      </div>
      {trend && (
        <div className="flex items-center gap-1 text-xs">
          <TrendingUp size={14} className="text-emerald-600" />
          <span className="text-emerald-600">{trend}</span>
        </div>
      )}
    </div>
  );
};

const AlertBanner = ({ alerts }) => {
  if (!alerts || alerts.length === 0) {
    return (
      <div className="card p-6 bg-emerald-50 border-emerald-200">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-emerald-100 flex items-center justify-center">
            <CheckCircle size={20} className="text-emerald-600" />
          </div>
          <div>
            <p className="font-medium text-emerald-900">All Systems Normal</p>
            <p className="text-sm text-emerald-700">No critical alerts at this time</p>
          </div>
        </div>
      </div>
    );
  }

  const criticalCount = alerts.filter(a => a.severity === 'CRITICAL').length;

  return (
    <div className="card p-6 bg-rose-50 border-rose-200">
      <div className="flex items-start gap-4">
        <div className="w-10 h-10 rounded-lg bg-rose-100 flex items-center justify-center flex-shrink-0">
          <AlertCircle size={20} className="text-rose-600" />
        </div>
        <div className="flex-1 min-w-0">
          <p className="font-semibold text-rose-900">{criticalCount} Critical Alert{criticalCount !== 1 ? 's' : ''}</p>
          <p className="text-sm text-rose-700 mt-1">
            {criticalCount} product{criticalCount !== 1 ? 's' : ''} require immediate attention
          </p>
        </div>
        <button className="px-4 py-2 bg-rose-600 text-white rounded-lg font-medium hover:bg-rose-700 transition-colors text-sm flex-shrink-0">
          Review
        </button>
      </div>
    </div>
  );
};

export const Dashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [summaryData, setSummaryData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadDashboardData();
  }, []);

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

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="flex flex-col items-center gap-3">
          <Loader size={32} className="text-indigo-600 animate-spin" />
          <p className="text-slate-500">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  const metrics = dashboardData && summaryData ? [
    {
      icon: Package,
      label: 'Total Products',
      value: dashboardData.total_products,
      color: 'indigo',
      trend: '↑ 2 new this month'
    },
    {
      icon: TrendingUp,
      label: 'Inventory Value',
      value: `₹${summaryData.inventory_metrics.inventory_value.toLocaleString('en-IN', { maximumFractionDigits: 0 })}`,
      color: 'emerald',
    },
    {
      icon: AlertCircle,
      label: 'Low Stock Items',
      value: dashboardData.low_stock_products,
      subtitle: 'Need reordering',
      color: 'amber',
    },
    {
      icon: Calendar,
      label: 'Expiring Soon',
      value: dashboardData.expiring_soon_products,
      subtitle: 'Within 7 days',
      color: 'rose',
    },
    {
      icon: BarChart3,
      label: '7-Day Forecast',
      value: dashboardData.predicted_7_day_demand,
      subtitle: 'Predicted demand',
      color: 'indigo',
    },
    {
      icon: Package,
      label: 'Expired Items',
      value: dashboardData.expired_products,
      subtitle: 'Require disposal',
      color: 'rose',
    }
  ] : [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Dashboard</h1>
          <p className="text-slate-500 mt-1">Welcome back! Here's your inventory overview.</p>
        </div>
        <button
          onClick={loadDashboardData}
          className="p-2 rounded-lg hover:bg-slate-100 transition-colors"
          title="Refresh dashboard"
        >
          <RefreshCw size={20} className="text-slate-600" />
        </button>
      </div>

      {/* Error message */}
      {error && (
        <div className="card p-4 bg-rose-50 border-rose-200">
          <p className="text-sm text-rose-700">{error}</p>
        </div>
      )}

      {/* Metric Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {metrics.map((metric, idx) => (
          <MetricCard key={idx} {...metric} />
        ))}
      </div>

      {/* Alerts and Activity Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Critical Alerts */}
        <div className="lg:col-span-1">
          <h2 className="text-lg font-semibold text-slate-900 mb-4">Status</h2>
          <AlertBanner alerts={summaryData?.alerts?.low_stock_products || []} />
        </div>

        {/* Recent Activity */}
        <div className="lg:col-span-2">
          <h2 className="text-lg font-semibold text-slate-900 mb-4">Low Stock Products</h2>
          <div className="card divide-y divide-slate-200 overflow-hidden">
            {summaryData?.alerts?.low_stock_products && summaryData.alerts.low_stock_products.length > 0 ? (
              summaryData.alerts.low_stock_products.slice(0, 5).map((product) => (
                <div key={product.id} className="p-4 hover:bg-slate-50 transition-colors">
                  <div className="flex items-center justify-between">
                    <div className="flex-1 min-w-0">
                      <h4 className="font-medium text-slate-900 truncate">{product.name}</h4>
                      <p className="text-sm text-slate-500">Stock: {product.current_stock} / {product.minimum_stock}</p>
                    </div>
                    <div className="flex items-center gap-2 flex-shrink-0">
                      <span className="badge-warning">Low</span>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="p-6 text-center text-slate-500">
                <p className="text-sm">No low stock items</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
