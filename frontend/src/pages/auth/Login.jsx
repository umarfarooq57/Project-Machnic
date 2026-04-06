/**
 * Login page component.
 */
import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import toast from 'react-hot-toast';

function Login() {
    const navigate = useNavigate();
    const { login, isLoading, error, clearError } = useAuthStore();
    const [formData, setFormData] = useState({
        email: '',
        password: '',
    });

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData((prev) => ({ ...prev, [name]: value }));
        if (error) clearError();
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!formData.email || !formData.password) {
            toast.error('Please fill in all fields');
            return;
        }

        const result = await login(formData.email, formData.password);

        if (result.success) {
            toast.success('Welcome back!');
            navigate('/dashboard');
        } else {
            toast.error(result.error || 'Login failed');
        }
    };

    return (
        <>
            <h2 className="auth-title">Welcome Back</h2>

            {error && typeof error === 'string' && (
                <div className="auth-error">{error}</div>
            )}

            <form className="auth-form" onSubmit={handleSubmit}>
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
                    <label className="label" htmlFor="password">Password</label>
                    <input
                        type="password"
                        id="password"
                        name="password"
                        className="input"
                        placeholder="••••••••"
                        value={formData.password}
                        onChange={handleChange}
                        autoComplete="current-password"
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
                            Signing in...
                        </>
                    ) : (
                        'Sign In'
                    )}
                </button>
            </form>

            <p className="auth-link mt-6">
                Don't have an account?{' '}
                <Link to="/signup">Create one</Link>
            </p>
        </>
    );
}

export default Login;
