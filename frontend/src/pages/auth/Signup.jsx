/**
 * Signup page component.
 */
import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import toast from 'react-hot-toast';

function Signup() {
    const navigate = useNavigate();
    const { register, isLoading, error, clearError } = useAuthStore();
    const [formData, setFormData] = useState({
        full_name: '',
        email: '',
        phone: '',
        password: '',
        password_confirm: '',
    });

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData((prev) => ({ ...prev, [name]: value }));
        if (error) clearError();
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (formData.password !== formData.password_confirm) {
            toast.error('Passwords do not match');
            return;
        }

        if (formData.password.length < 8) {
            toast.error('Password must be at least 8 characters');
            return;
        }

        const result = await register(formData);

        if (result.success) {
            toast.success('Account created successfully!');
            navigate('/dashboard');
        } else {
            const errorMsg = Object.values(result.error || {})[0];
            toast.error(Array.isArray(errorMsg) ? errorMsg[0] : 'Registration failed');
        }
    };

    return (
        <>
            <h2 className="auth-title">Create Account</h2>

            <form className="auth-form" onSubmit={handleSubmit}>
                <div className="form-group">
                    <label className="label" htmlFor="full_name">Full Name</label>
                    <input
                        type="text"
                        id="full_name"
                        name="full_name"
                        className="input"
                        placeholder="John Doe"
                        value={formData.full_name}
                        onChange={handleChange}
                        required
                    />
                </div>

                <div className="form-group">
                    <label className="label" htmlFor="email">Email</label>
                    <input
                        type="email"
                        id="email"
                        name="email"
                        className="input"
                        placeholder="you@example.com"
                        value={formData.email}
                        onChange={handleChange}
                        autoComplete="email"
                        required
                    />
                </div>

                <div className="form-group">
                    <label className="label" htmlFor="phone">Phone (optional)</label>
                    <input
                        type="tel"
                        id="phone"
                        name="phone"
                        className="input"
                        placeholder="+1 234 567 8900"
                        value={formData.phone}
                        onChange={handleChange}
                    />
                </div>

                <div className="form-group">
                    <label className="label" htmlFor="password">Password</label>
                    <input
                        type="password"
                        id="password"
                        name="password"
                        className="input"
                        placeholder="••••••••"
                        value={formData.password}
                        onChange={handleChange}
                        autoComplete="new-password"
                        required
                    />
                </div>

                <div className="form-group">
                    <label className="label" htmlFor="password_confirm">Confirm Password</label>
                    <input
                        type="password"
                        id="password_confirm"
                        name="password_confirm"
                        className="input"
                        placeholder="••••••••"
                        value={formData.password_confirm}
                        onChange={handleChange}
                        autoComplete="new-password"
                        required
                    />
                </div>

                <button
                    type="submit"
                    className="btn btn-primary btn-lg w-full"
                    disabled={isLoading}
                >
                    {isLoading ? (
                        <>
                            <span className="loader loader-sm"></span>
                            Creating account...
                        </>
                    ) : (
                        'Create Account'
                    )}
                </button>
            </form>

            <p className="auth-link mt-6">
                Already have an account?{' '}
                <Link to="/login">Sign in</Link>
            </p>
        </>
    );
}

export default Signup;
