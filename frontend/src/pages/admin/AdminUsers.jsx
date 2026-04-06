/**
 * Admin Users — User management table with search and filters.
 */
import { useEffect, useState } from 'react';
import { useAdminStore } from '../../store/adminStore';
import { Link } from 'react-router-dom';

export default function AdminUsers() {
    const { users, loading, fetchUsers, updateUser } = useAdminStore();
    const [search, setSearch] = useState('');
    const [roleFilter, setRoleFilter] = useState('');

    useEffect(() => {
        fetchUsers({ search, role: roleFilter });
    }, [search, roleFilter]);

    const toggleActive = (user) => {
        updateUser(user.id, { is_active: !user.is_active });
    };

    return (
        <div className="admin-dashboard animate-fadeIn" style={{ padding: 'var(--space-6)', maxWidth: 1400, margin: '0 auto' }}>
            <div className="flex justify-between items-center mb-6" style={{ flexWrap: 'wrap', gap: 'var(--space-4)' }}>
                <div>
                    <h1>User Management</h1>
                    <p>Search, filter, and manage platform users</p>
                </div>
                <Link to="/admin" className="btn btn-secondary">← Dashboard</Link>
            </div>

            {/* Filters */}
            <div className="flex gap-4 mb-6" style={{ flexWrap: 'wrap' }}>
                <input
                    className="input"
                    style={{ maxWidth: 320 }}
                    placeholder="Search by name, email, phone…"
                    value={search}
                    onChange={e => setSearch(e.target.value)}
                />
                <select className="select" style={{ maxWidth: 180 }} value={roleFilter} onChange={e => setRoleFilter(e.target.value)}>
                    <option value="">All Roles</option>
                    <option value="user">User</option>
                    <option value="helper">Helper</option>
                    <option value="admin">Admin</option>
                </select>
            </div>

            {/* Table */}
            {loading ? (
                <div className="flex justify-center p-8"><div className="loader" /></div>
            ) : (
                <div className="card" style={{ overflowX: 'auto' }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                        <thead>
                            <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
                                {['Name', 'Email', 'Role', 'Verified', 'Active', 'Actions'].map(h => (
                                    <th key={h} style={{ textAlign: 'left', padding: 'var(--space-3) var(--space-4)', color: 'var(--text-muted)', fontSize: 'var(--font-size-sm)', fontWeight: 600 }}>{h}</th>
                                ))}
                            </tr>
                        </thead>
                        <tbody>
                            {users.map(user => (
                                <tr key={user.id} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                                    <td style={{ padding: 'var(--space-3) var(--space-4)', fontWeight: 500 }}>{user.full_name}</td>
                                    <td style={{ padding: 'var(--space-3) var(--space-4)', color: 'var(--text-secondary)' }}>{user.email}</td>
                                    <td style={{ padding: 'var(--space-3) var(--space-4)' }}>
                                        <span className={`badge badge-${user.role === 'admin' ? 'primary' : user.role === 'helper' ? 'success' : 'info'}`}>{user.role}</span>
                                    </td>
                                    <td style={{ padding: 'var(--space-3) var(--space-4)' }}>
                                        <span className={`badge badge-${user.is_verified ? 'success' : 'warning'}`}>{user.is_verified ? 'Yes' : 'No'}</span>
                                    </td>
                                    <td style={{ padding: 'var(--space-3) var(--space-4)' }}>
                                        <span className={`badge badge-${user.is_active ? 'success' : 'error'}`}>{user.is_active ? 'Active' : 'Inactive'}</span>
                                    </td>
                                    <td style={{ padding: 'var(--space-3) var(--space-4)' }}>
                                        <button className={`btn btn-sm ${user.is_active ? 'btn-accent' : 'btn-success'}`} onClick={() => toggleActive(user)}>
                                            {user.is_active ? 'Deactivate' : 'Activate'}
                                        </button>
                                    </td>
                                </tr>
                            ))}
                            {users.length === 0 && (
                                <tr>
                                    <td colSpan={6} style={{ textAlign: 'center', padding: 'var(--space-8)', color: 'var(--text-muted)' }}>No users found.</td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
}
