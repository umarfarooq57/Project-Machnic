/**
 * Auth Layout for login/signup pages.
 */
import { Outlet } from 'react-router-dom';
import './AuthLayout.css';

function AuthLayout() {
    return (
        <div className="auth-layout">
            <div className="auth-background">
                <div className="auth-gradient"></div>
                <div className="auth-shapes">
                    <div className="shape shape-1"></div>
                    <div className="shape shape-2"></div>
                    <div className="shape shape-3"></div>
                </div>
            </div>

            <div className="auth-container">
                <div className="auth-header">
                    <div className="auth-logo">
                        <div className="logo-icon">🚗</div>
                        <span className="logo-text">RoadAid Network</span>
                    </div>
                    <p className="auth-tagline">
                        Real-time roadside assistance at your fingertips
                    </p>
                </div>

                <div className="auth-card">
                    <Outlet />
                </div>

                <p className="auth-footer">
                    © 2024 RoadAid Network. All rights reserved.
                </p>
            </div>
        </div>
    );
}

export default AuthLayout;
