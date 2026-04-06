/**
 * Admin Helpers — Helper verification queue.
 */
import { useEffect } from 'react';
import { useAdminStore } from '../../store/adminStore';
import { Link } from 'react-router-dom';

export default function AdminHelpers() {
    const { helpers, loading, fetchHelpers, verifyHelper } = useAdminStore();

    useEffect(() => {
        fetchHelpers();
    }, []);

    const statusBadge = (s) => {
        const map = { pending: 'warning', verified: 'success', rejected: 'error', suspended: 'error' };
        return `badge badge-${map[s] || 'info'}`;
    };

    return (
        <div className="admin-dashboard animate-fadeIn" style={{ padding: 'var(--space-6)', maxWidth: 1400, margin: '0 auto' }}>
            <div className="flex justify-between items-center mb-6" style={{ flexWrap: 'wrap', gap: 'var(--space-4)' }}>
                <div>
                    <h1>Helper Verification</h1>
                    <p>Review and manage helper applications</p>
                </div>
                <Link to="/admin" className="btn btn-secondary">← Dashboard</Link>
            </div>

            {loading ? (
                <div className="flex justify-center p-8"><div className="loader" /></div>
            ) : (
                <div className="grid gap-4" style={{ gridTemplateColumns: 'repeat(auto-fill, minmax(360px, 1fr))' }}>
                    {helpers.map(helper => (
                        <div key={helper.id} className="card" style={{ padding: 'var(--space-5)' }}>
                            <div className="flex justify-between items-start mb-4">
                                <div>
                                    <h4 style={{ marginBottom: 4 }}>{helper.user_name}</h4>
                                    <p style={{ fontSize: 'var(--font-size-sm)' }}>{helper.user_email}</p>
                                </div>
                                <span className={statusBadge(helper.verification_status)}>{helper.verification_status}</span>
                            </div>
                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-2)', marginBottom: 'var(--space-4)', fontSize: 'var(--font-size-sm)', color: 'var(--text-secondary)' }}>
                                <div>🏪 {helper.shop_name || 'N/A'}</div>
                                <div>📅 {helper.experience_years}y experience</div>
                                <div>⭐ {helper.rating_avg || '0.0'} rating</div>
                                <div>🔧 {helper.total_jobs || 0} jobs</div>
                            </div>
                            {helper.verification_status === 'pending' && (
                                <div className="flex gap-2">
                                    <button className="btn btn-success btn-sm" onClick={() => verifyHelper(helper.id, 'approve')}>✅ Approve</button>
                                    <button className="btn btn-accent btn-sm" onClick={() => verifyHelper(helper.id, 'reject')}>❌ Reject</button>
                                </div>
                            )}
                            {helper.verification_status === 'verified' && (
                                <button className="btn btn-accent btn-sm" onClick={() => verifyHelper(helper.id, 'suspend')}>⏸️ Suspend</button>
                            )}
                        </div>
                    ))}
                    {helpers.length === 0 && (
                        <p style={{ color: 'var(--text-muted)', padding: 'var(--space-8)' }}>No helpers found.</p>
                    )}
                </div>
            )}
        </div>
    );
}
