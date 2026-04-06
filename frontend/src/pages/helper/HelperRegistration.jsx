/**
 * Helper Registration page - Form to become a helper.
 */
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import api from '../../api/client';
import toast from 'react-hot-toast';
import './Helper.css';

function HelperRegistration() {
    const navigate = useNavigate();
    const { user } = useAuthStore();
    const [isLoading, setIsLoading] = useState(false);
    const [vehicleTypes, setVehicleTypes] = useState([]);
    const [serviceTypes, setServiceTypes] = useState([]);
    const [formData, setFormData] = useState({
        bio: '',
        experience_years: 1,
        vehicle_types: [],
        service_types: [],
        hourly_rate: 50,
    });

    useEffect(() => {
        if (user?.is_helper) {
            navigate('/helper/dashboard');
            return;
        }
        fetchTypes();
    }, [user]);

    const fetchTypes = async () => {
        try {
            const [vTypes, sTypes] = await Promise.all([
                api.get('/helpers/vehicle-types/'),
                api.get('/helpers/service-types/'),
            ]);
            setVehicleTypes(vTypes.data);
            setServiceTypes(sTypes.data);
        } catch (error) {
            console.error('Failed to fetch types:', error);
        }
    };

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData((prev) => ({ ...prev, [name]: value }));
    };

    const toggleSelection = (type, id) => {
        setFormData((prev) => ({
            ...prev,
            [type]: prev[type].includes(id)
                ? prev[type].filter((i) => i !== id)
                : [...prev[type], id],
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (formData.vehicle_types.length === 0) {
            toast.error('Please select at least one vehicle type');
            return;
        }

        if (formData.service_types.length === 0) {
            toast.error('Please select at least one service type');
            return;
        }

        setIsLoading(true);
        try {
            await api.post('/helpers/register/', formData);
            toast.success('Registration successful! Welcome, Helper!');
            // Refresh user data
            window.location.reload();
        } catch (error) {
            const msg = error.response?.data?.error || 'Registration failed';
            toast.error(msg);
        }
        setIsLoading(false);
    };

    return (
        <div className="helper-registration animate-fadeIn">
            <div className="page-header">
                <h1>🔧 Become a Helper</h1>
                <p>Join our network and earn money by helping stranded drivers.</p>
            </div>

            {/* Benefits */}
            <div className="benefits-grid">
                {[
                    { icon: '💰', title: 'Earn Money', desc: 'Set your own rates and earn on your schedule' },
                    { icon: '📍', title: 'Work Nearby', desc: 'Get matched with users in your area' },
                    { icon: '⭐', title: 'Build Reputation', desc: 'Earn ratings and grow your client base' },
                    { icon: '🕐', title: 'Flexible Hours', desc: 'Work when it suits you' },
                ].map((benefit) => (
                    <div key={benefit.title} className="benefit-card card">
                        <span className="benefit-icon">{benefit.icon}</span>
                        <h4>{benefit.title}</h4>
                        <p>{benefit.desc}</p>
                    </div>
                ))}
            </div>

            {/* Registration Form */}
            <form className="registration-form card" onSubmit={handleSubmit}>
                <h3>Registration Details</h3>

                <div className="form-group">
                    <label className="label">Bio / Introduction</label>
                    <textarea
                        name="bio"
                        className="input"
                        rows="3"
                        placeholder="Tell users about your experience and skills..."
                        value={formData.bio}
                        onChange={handleChange}
                        required
                    />
                </div>

                <div className="form-row">
                    <div className="form-group">
                        <label className="label">Years of Experience</label>
                        <input
                            type="number"
                            name="experience_years"
                            className="input"
                            min="0"
                            max="50"
                            value={formData.experience_years}
                            onChange={handleChange}
                        />
                    </div>
                    <div className="form-group">
                        <label className="label">Hourly Rate ($)</label>
                        <input
                            type="number"
                            name="hourly_rate"
                            className="input"
                            min="10"
                            max="500"
                            value={formData.hourly_rate}
                            onChange={handleChange}
                        />
                    </div>
                </div>

                <div className="form-group">
                    <label className="label">Vehicle Types You Can Service</label>
                    <div className="selection-grid">
                        {vehicleTypes.map((type) => (
                            <div
                                key={type.id}
                                className={`selection-item ${formData.vehicle_types.includes(type.id) ? 'selected' : ''}`}
                                onClick={() => toggleSelection('vehicle_types', type.id)}
                            >
                                <span>{type.icon}</span>
                                <span>{type.name}</span>
                            </div>
                        ))}
                    </div>
                </div>

                <div className="form-group">
                    <label className="label">Services You Offer</label>
                    <div className="selection-grid">
                        {serviceTypes.map((type) => (
                            <div
                                key={type.id}
                                className={`selection-item ${formData.service_types.includes(type.id) ? 'selected' : ''}`}
                                onClick={() => toggleSelection('service_types', type.id)}
                            >
                                <span>{type.name}</span>
                            </div>
                        ))}
                    </div>
                </div>

                <button type="submit" className="btn btn-accent btn-lg w-full" disabled={isLoading}>
                    {isLoading ? 'Registering...' : '🚀 Register as Helper'}
                </button>
            </form>
        </div>
    );
}

export default HelperRegistration;
