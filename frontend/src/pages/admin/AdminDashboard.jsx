/**
 * Admin Dashboard — Premium dark-themed analytics overview.
 */
import { useEffect } from 'react';
import { useAdminStore } from '../../store/adminStore';
import { Link } from 'react-router-dom';
import './AdminDashboard.css';

function StatCard({ icon, label, value, accent }) {
    return (
        <div className={`admin-stat-card admin-stat-card--${accent}`}>
            <div className="admin-stat-card__icon">{icon}</div>
            <div className="admin-stat-card__info">
                <span className="admin-stat-card__value">{value ?? '–'}</span>
                <span className="admin-stat-card__label">{label}</span>
            </div>
        </div>
    );
}

function MiniBarChart({ data }) {
    if (!data || data.length === 0) return <p className="text-muted">No data yet.</p>;
    const max = Math.max(...data.map(d => Number(d.revenue) || 0), 1);
    return (
        <div className="admin-chart">
            {data.slice(-14).map((d, i) => (
                <div className="admin-chart__bar-wrap" key={i} title={`${d.date}: $${d.revenue}`}>
                    <div
                        className="admin-chart__bar"
                        style={{ height: `${(Number(d.revenue) / max) * 100}%` }}
                    />
                    <span className="admin-chart__label">
                        {new Date(d.date).getDate()}
                    </span>
                </div>
            ))}
        </div>
    );
}

export default function AdminDashboard() {
    const { stats, revenueReport, loading, fetchDashboardStats, fetchRevenueReport } =
        useAdminStore();

    useEffect(() => {
        fetchDashboardStats();
        fetchRevenueReport(30);
    }, []);

    return (
        <div className="admin-dashboard animate-fadeIn">
            <div className="admin-dashboard__header">
                <div>
                    <h1>Admin Dashboard</h1>
                    <p>Platform overview and analytics</p>
                </div>
                <div className="admin-dashboard__actions">
                    <Link to="/admin/users" className="btn btn-secondary">Manage Users</Link>
                    <Link to="/admin/helpers" className="btn btn-secondary">Verify Helpers</Link>
                    <Link to="/admin/promo-codes" className="btn btn-primary">Promo Codes</Link>
                </div>
            </div>

            {loading && !stats ? (
                <div className="flex justify-center p-8"><div className="loader" /></div>
            ) : (
                <>
                    <div className="admin-stats-grid">
                        <StatCard icon="👥" label="Total Users" value={stats?.total_users} accent="primary" />
                        <StatCard icon="🔧" label="Total Helpers" value={stats?.total_helpers} accent="accent" />
                        <StatCard icon="✅" label="Verified Helpers" value={stats?.verified_helpers} accent="success" />
                        <StatCard icon="⏳" label="Pending Verification" value={stats?.pending_helpers} accent="warning" />
                        <StatCard icon="📋" label="Active Requests" value={stats?.active_requests} accent="info" />
                        <StatCard icon="🏁" label="Completed" value={stats?.completed_requests} accent="success" />
                        <StatCard icon="💰" label="Total Revenue" value={stats?.total_revenue ? `$${Number(stats.total_revenue).toLocaleString()}` : '$0'} accent="accent" />
                        <StatCard icon="📊" label="Today Revenue" value={stats?.today_revenue ? `$${Number(stats.today_revenue).toLocaleString()}` : '$0'} accent="primary" />
                    </div>

                    <div className="admin-dashboard__section">
                        <h3>Revenue (Last 30 Days)</h3>
                        <div className="card">
                            <MiniBarChart data={revenueReport} />
                        </div>
                    </div>

                    <div className="admin-dashboard__section">
                        <h3>Quick Links</h3>
                        <div className="admin-quick-links">
                            <Link to="/admin/helpers" className="admin-quick-link card">
                                <span className="admin-quick-link__icon">🛡️</span>
                                <span>Helper Verification ({stats?.pending_helpers || 0} pending)</span>
                            </Link>
                            <Link to="/admin/disputes" className="admin-quick-link card">
                                <span className="admin-quick-link__icon">⚠️</span>
                                <span>Open Disputes ({stats?.open_disputes || 0})</span>
                            </Link>
                            <Link to="/admin/promo-codes" className="admin-quick-link card">
                                <span className="admin-quick-link__icon">🎟️</span>
                                <span>Promo Codes</span>
                            </Link>
                        </div>
                    </div>
                </>
            )}
        </div>
    );
}
