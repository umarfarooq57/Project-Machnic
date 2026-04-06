/**
 * Create Request page - Form to create a new service request.
 */
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useRequestStore } from '../../store/requestStore';
import { useAuthStore } from '../../store/authStore';
import api from '../../api/client';
import toast from 'react-hot-toast';
import './Request.css';

function CreateRequest() {
    const navigate = useNavigate();
    const { createRequest, isLoading } = useRequestStore();
    const { user, updateLocation } = useAuthStore();
    const [vehicleTypes, setVehicleTypes] = useState([]);
    const [locations, setLocations] = useState([]);
    const [location, setLocation] = useState(null);
    const [useManualLocation, setUseManualLocation] = useState(false);
    const [formData, setFormData] = useState({
        vehicle_type: '',
        issue_description: '',
        urgency: 'medium',
        service_location: '',
    });

    useEffect(() => {
        fetchVehicleTypes();
        fetchLocations();
        getCurrentLocation();
    }, []);

    const fetchVehicleTypes = async () => {
        try {
            const response = await api.get('/helpers/vehicle-types/');
            setVehicleTypes(response.data.results || response.data);
        } catch (error) {
            console.error('Failed to fetch vehicle types:', error);
            toast.error('Could not load vehicle types');
        }
    };

    const fetchLocations = async () => {
        try {
            const response = await api.get('/helpers/locations/');
            setLocations(response.data.results || response.data);
        } catch (error) {
            console.error('Failed to fetch locations:', error);
        }
    };

    const getCurrentLocation = () => {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    const { latitude, longitude } = position.coords;
                    setLocation({ latitude, longitude });
                    if (updateLocation) {
                        updateLocation(latitude, longitude);
                    }
                },
                (error) => {
                    console.warn('Geolocation failed:', error);
                    setUseManualLocation(true);
                    toast('Location not available. Please select your city.', { icon: '📍' });
                }
            );
        } else {
            setUseManualLocation(true);
            toast('Geolocation not supported. Please select your city.', { icon: '📍' });
        }
    };

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData((prev) => ({ ...prev, [name]: value }));
    };

    const handleLocationSelect = (loc) => {
        setFormData((prev) => ({ ...prev, service_location: loc.id }));
        // Use location's coordinates as fallback
        if (!location && loc.latitude && loc.longitude) {
            setLocation({ latitude: loc.latitude, longitude: loc.longitude });
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        // Validate location
        let userLat = location?.latitude;
        let userLon = location?.longitude;

        // If no GPS location, use selected city's coordinates
        if (!userLat || !userLon) {
            const selectedLoc = locations.find(l => l.id == formData.service_location);
            if (selectedLoc) {
                userLat = selectedLoc.latitude;
                userLon = selectedLoc.longitude;
            }
        }

        if (!userLat || !userLon) {
            toast.error('Please enable location or select a city');
            return;
        }

        if (!formData.vehicle_type) {
            toast.error('Please select a vehicle type');
            return;
        }

        if (!formData.issue_description.trim()) {
            toast.error('Please describe the issue');
            return;
        }

        try {
            const result = await createRequest({
                vehicle_type: formData.vehicle_type,
                issue_description: formData.issue_description,
                urgency: formData.urgency,
                user_latitude: userLat,
                user_longitude: userLon,
            });

            if (result.success) {
                toast.success('Request created! Searching for helpers...');
                navigate(`/request/${result.request.id}`);
            } else {
                const errorMsg = result.error?.detail || result.error?.message || 'Failed to create request';
                toast.error(typeof errorMsg === 'string' ? errorMsg : JSON.stringify(errorMsg));
            }
        } catch (error) {
            console.error('Request creation error:', error);
            toast.error('An error occurred. Please try again.');
        }
    };

    return (
        <div className="create-request animate-fadeIn">
            <div className="page-header">
                <h1>🚨 Get Help Now</h1>
                <p>Describe your issue and we'll connect you with nearby helpers.</p>
            </div>

            <form className="request-form card" onSubmit={handleSubmit}>
                {/* Location Status */}
                <div className="location-status">
                    {location ? (
                        <div className="location-found">
                            <span className="status-icon">📍</span>
                            <span>Location detected</span>
                        </div>
                    ) : (
                        <div className="location-pending">
                            <span className="status-icon">📍</span>
                            <span>Select your location below</span>
                        </div>
                    )}
                </div>

                {/* Location Selector */}
                {locations.length > 0 && (
                    <div className="form-group">
                        <label className="label">Your City / Area</label>
                        <div className="location-grid">
                            {locations.map((loc) => (
                                <div
                                    key={loc.id}
                                    className={`location-option ${formData.service_location == loc.id ? 'selected' : ''}`}
                                    onClick={() => handleLocationSelect(loc)}
                                >
                                    <span className="location-icon">{loc.is_nationwide ? '🇵🇰' : '🏙️'}</span>
                                    <div className="location-text">
                                        <span className="location-name">{loc.name}</span>
                                        {loc.name_urdu && <span className="location-urdu">{loc.name_urdu}</span>}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Vehicle Type */}
                <div className="form-group">
                    <label className="label">Vehicle Type</label>
                    {vehicleTypes.length === 0 ? (
                        <div className="loading-placeholder">
                            <div className="loader loader-sm"></div>
                            <span>Loading vehicle types...</span>
                        </div>
                    ) : (
                        <div className="vehicle-grid">
                            {vehicleTypes.map((type) => (
                                <div
                                    key={type.id}
                                    className={`vehicle-option ${formData.vehicle_type == type.id ? 'selected' : ''}`}
                                    onClick={() => setFormData((prev) => ({ ...prev, vehicle_type: type.id }))}
                                >
                                    <span className="vehicle-icon">{type.icon}</span>
                                    <span className="vehicle-name">{type.name}</span>
                                    <span className="vehicle-price">Rs. {type.base_price}</span>
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                {/* Issue Description */}
                <div className="form-group">
                    <label className="label" htmlFor="issue_description">Describe Your Issue</label>
                    <textarea
                        id="issue_description"
                        name="issue_description"
                        className="input"
                        rows="4"
                        placeholder="E.g., Flat tire on the highway, need help changing it..."
                        value={formData.issue_description}
                        onChange={handleChange}
                        required
                    />
                </div>

                {/* Urgency */}
                <div className="form-group">
                    <label className="label">Urgency Level</label>
                    <div className="urgency-options">
                        {[
                            { value: 'low', label: 'Low', desc: 'Can wait', icon: '🟢' },
                            { value: 'medium', label: 'Medium', desc: 'Need soon', icon: '🟡' },
                            { value: 'high', label: 'High', desc: 'Urgent', icon: '🟠' },
                            { value: 'emergency', label: 'Emergency', desc: 'Safety risk', icon: '🔴' },
                        ].map((option) => (
                            <div
                                key={option.value}
                                className={`urgency-option ${formData.urgency === option.value ? 'selected' : ''}`}
                                onClick={() => setFormData((prev) => ({ ...prev, urgency: option.value }))}
                            >
                                <span className="urgency-icon">{option.icon}</span>
                                <div className="urgency-text">
                                    <span className="urgency-label">{option.label}</span>
                                    <span className="urgency-desc">{option.desc}</span>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                <button
                    type="submit"
                    className="btn btn-accent btn-lg w-full"
                    disabled={isLoading || vehicleTypes.length === 0}
                >
                    {isLoading ? (
                        <>
                            <span className="loader loader-sm"></span>
                            Creating Request...
                        </>
                    ) : (
                        <>🚨 Request Help</>
                    )}
                </button>
            </form>
        </div>
    );
}

export default CreateRequest;
