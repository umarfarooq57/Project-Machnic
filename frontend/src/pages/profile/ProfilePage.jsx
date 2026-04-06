/**
 * Profile Page - User profile management.
 */
import { useState } from 'react';
import { useAuthStore } from '../../store/authStore';
import api from '../../api/client';
import toast from 'react-hot-toast';
import './Profile.css';

function ProfilePage() {
    const { user, updateProfile, logout } = useAuthStore();
    const [isEditing, setIsEditing] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [formData, setFormData] = useState({
        full_name: user?.full_name || '',
        phone: user?.phone || '',
    });

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData((prev) => ({ ...prev, [name]: value }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsLoading(true);

        const result = await updateProfile(formData);

        if (result.success) {
            toast.success('Profile updated!');
            setIsEditing(false);
        } else {
            toast.error('Failed to update profile');
        }
        setIsLoading(false);
    };

    const handleDeleteAccount = async () => {
        if (confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
            try {
                await api.delete('/auth/account/');
                toast.success('Account deleted');
                logout();
            } catch (error) {
                toast.error('Failed to delete account');
            }
        }
    };

    return (
        <div className="profile-page animate-fadeIn">
            <div className="page-header">
                <h1>Profile Settings</h1>
                <p>Manage your account information.</p>
            </div>

            <div className="profile-content">
                {/* Avatar Section */}
                <div className="profile-card card">
                    <div className="profile-avatar-section">
                        <div className="profile-avatar">
                            {user?.profile_image ? (
                                <img src={user.profile_image} alt={user.full_name} />
                            ) : (
                                <span>{user?.full_name?.charAt(0) || 'U'}</span>
                            )}
                        </div>
                        <div className="profile-info">
                            <h2>{user?.full_name}</h2>
                            <p>{user?.email}</p>
                            {user?.is_helper && <span className="badge badge-primary">Helper</span>}
                        </div>
                    </div>
                </div>

                {/* Edit Form */}
                <div className="profile-card card">
                    <div className="card-header">
                        <h3>Personal Information</h3>
                        {!isEditing && (
                            <button className="btn btn-secondary btn-sm" onClick={() => setIsEditing(true)}>
                                Edit
                            </button>
                        )}
                    </div>

                    {isEditing ? (
                        <form onSubmit={handleSubmit}>
                            <div className="form-group">
                                <label className="label">Full Name</label>
                                <input
                                    type="text"
                                    name="full_name"
                                    className="input"
                                    value={formData.full_name}
                                    onChange={handleChange}
                                    required
                                />
                            </div>
                            <div className="form-group">
                                <label className="label">Phone</label>
                                <input
                                    type="tel"
                                    name="phone"
                                    className="input"
                                    value={formData.phone}
                                    onChange={handleChange}
                                />
                            </div>
                            <div className="form-actions">
                                <button type="button" className="btn btn-secondary" onClick={() => setIsEditing(false)}>
                                    Cancel
                                </button>
                                <button type="submit" className="btn btn-primary" disabled={isLoading}>
                                    {isLoading ? 'Saving...' : 'Save Changes'}
                                </button>
                            </div>
                        </form>
                    ) : (
                        <div className="profile-fields">
                            <div className="profile-field">
                                <span className="field-label">Full Name</span>
                                <span className="field-value">{user?.full_name}</span>
                            </div>
                            <div className="profile-field">
                                <span className="field-label">Email</span>
                                <span className="field-value">{user?.email}</span>
                            </div>
                            <div className="profile-field">
                                <span className="field-label">Phone</span>
                                <span className="field-value">{user?.phone || 'Not set'}</span>
                            </div>
                        </div>
                    )}
                </div>

                {/* Danger Zone */}
                <div className="profile-card card danger-zone">
                    <h3>Danger Zone</h3>
                    <p>Once you delete your account, there is no going back.</p>
                    <button className="btn btn-secondary" onClick={handleDeleteAccount}>
                        Delete Account
                    </button>
                </div>
            </div>
        </div>
    );
}

export default ProfilePage;
