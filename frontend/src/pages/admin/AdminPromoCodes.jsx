/**
 * Admin Promo Codes — CRUD management.
 */
import { useEffect, useState } from 'react';
import { useAdminStore } from '../../store/adminStore';
import { Link } from 'react-router-dom';

export default function AdminPromoCodes() {
    const { promoCodes, loading, fetchPromoCodes, createPromoCode, deletePromoCode } = useAdminStore();
    const [showForm, setShowForm] = useState(false);
    const [form, setForm] = useState({
        code: '', discount_type: 'percentage', discount_value: '',
        min_order_amount: '0', usage_limit: '0',
        valid_from: '', valid_until: '',
    });

    useEffect(() => { fetchPromoCodes(); }, []);

    const handleCreate = async (e) => {
        e.preventDefault();
        await createPromoCode(form);
        setShowForm(false);
        setForm({ code: '', discount_type: 'percentage', discount_value: '', min_order_amount: '0', usage_limit: '0', valid_from: '', valid_until: '' });
    };

    return (
        <div className="admin-dashboard animate-fadeIn" style={{ padding: 'var(--space-6)', maxWidth: 1400, margin: '0 auto' }}>
            <div className="flex justify-between items-center mb-6" style={{ flexWrap: 'wrap', gap: 'var(--space-4)' }}>
                <div>
                    <h1>Promo Codes</h1>
                    <p>Manage discount codes and coupons</p>
                </div>
                <div className="flex gap-3">
                    <Link to="/admin" className="btn btn-secondary">← Dashboard</Link>
                    <button className="btn btn-primary" onClick={() => setShowForm(!showForm)}>
                        {showForm ? 'Cancel' : '+ New Code'}
                    </button>
                </div>
            </div>

            {/* Create Form */}
            {showForm && (
                <form className="card mb-6" onSubmit={handleCreate} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-4)', padding: 'var(--space-6)' }}>
                    <div className="form-group" style={{ marginBottom: 0 }}>
                        <label className="label">Code</label>
                        <input className="input" placeholder="e.g. SAVE20" required value={form.code} onChange={e => setForm({ ...form, code: e.target.value.toUpperCase() })} />
                    </div>
                    <div className="form-group" style={{ marginBottom: 0 }}>
                        <label className="label">Discount Type</label>
                        <select className="select" value={form.discount_type} onChange={e => setForm({ ...form, discount_type: e.target.value })}>
                            <option value="percentage">Percentage (%)</option>
                            <option value="flat">Flat Amount ($)</option>
                        </select>
                    </div>
                    <div className="form-group" style={{ marginBottom: 0 }}>
                        <label className="label">Discount Value</label>
                        <input className="input" type="number" step="0.01" required value={form.discount_value} onChange={e => setForm({ ...form, discount_value: e.target.value })} />
                    </div>
                    <div className="form-group" style={{ marginBottom: 0 }}>
                        <label className="label">Min Order ($)</label>
                        <input className="input" type="number" step="0.01" value={form.min_order_amount} onChange={e => setForm({ ...form, min_order_amount: e.target.value })} />
                    </div>
                    <div className="form-group" style={{ marginBottom: 0 }}>
                        <label className="label">Valid From</label>
                        <input className="input" type="datetime-local" required value={form.valid_from} onChange={e => setForm({ ...form, valid_from: e.target.value })} />
                    </div>
                    <div className="form-group" style={{ marginBottom: 0 }}>
                        <label className="label">Valid Until</label>
                        <input className="input" type="datetime-local" required value={form.valid_until} onChange={e => setForm({ ...form, valid_until: e.target.value })} />
                    </div>
                    <div style={{ gridColumn: '1 / -1' }}>
                        <button className="btn btn-success" type="submit">Create Promo Code</button>
                    </div>
                </form>
            )}

            {/* List */}
            {loading ? (
                <div className="flex justify-center p-8"><div className="loader" /></div>
            ) : (
                <div className="card" style={{ overflowX: 'auto' }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                        <thead>
                            <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
                                {['Code', 'Type', 'Value', 'Used', 'Valid Until', 'Status', 'Actions'].map(h => (
                                    <th key={h} style={{ textAlign: 'left', padding: 'var(--space-3) var(--space-4)', color: 'var(--text-muted)', fontSize: 'var(--font-size-sm)' }}>{h}</th>
                                ))}
                            </tr>
                        </thead>
                        <tbody>
                            {promoCodes.map(pc => (
                                <tr key={pc.id} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                                    <td style={{ padding: 'var(--space-3) var(--space-4)', fontWeight: 600, fontFamily: 'monospace', letterSpacing: 1 }}>{pc.code}</td>
                                    <td style={{ padding: 'var(--space-3) var(--space-4)' }}>{pc.discount_type}</td>
                                    <td style={{ padding: 'var(--space-3) var(--space-4)' }}>{pc.discount_type === 'percentage' ? `${pc.discount_value}%` : `$${pc.discount_value}`}</td>
                                    <td style={{ padding: 'var(--space-3) var(--space-4)' }}>{pc.times_used}{pc.usage_limit > 0 ? `/${pc.usage_limit}` : ''}</td>
                                    <td style={{ padding: 'var(--space-3) var(--space-4)', color: 'var(--text-secondary)' }}>{new Date(pc.valid_until).toLocaleDateString()}</td>
                                    <td style={{ padding: 'var(--space-3) var(--space-4)' }}>
                                        <span className={`badge badge-${pc.is_valid ? 'success' : 'error'}`}>{pc.is_valid ? 'Active' : 'Expired'}</span>
                                    </td>
                                    <td style={{ padding: 'var(--space-3) var(--space-4)' }}>
                                        <button className="btn btn-accent btn-sm" onClick={() => deletePromoCode(pc.id)}>Delete</button>
                                    </td>
                                </tr>
                            ))}
                            {promoCodes.length === 0 && (
                                <tr><td colSpan={7} style={{ textAlign: 'center', padding: 'var(--space-8)', color: 'var(--text-muted)' }}>No promo codes.</td></tr>
                            )}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
}
