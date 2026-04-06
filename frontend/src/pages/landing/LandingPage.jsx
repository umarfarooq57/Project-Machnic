/**
 * Landing Page — SEO-optimized marketing page for RoadAid Network.
 */
import { Link } from 'react-router-dom';
import './LandingPage.css';

const features = [
    { icon: '🔧', title: 'Instant Mechanic Match', desc: 'Smart algorithm finds the best mechanic near you based on specialty, rating, and distance.' },
    { icon: '📍', title: 'Real-Time Tracking', desc: 'Track your mechanic live on the map from the moment they accept until they arrive.' },
    { icon: '💳', title: 'Flexible Payments', desc: 'Pay with card, cash, or your in-app wallet. Apply promo codes for instant discounts.' },
    { icon: '⭐', title: 'Verified & Rated', desc: 'Every mechanic is verified and community-rated so you always get quality service.' },
    { icon: '🛡️', title: 'SOS Safety', desc: 'One-tap SOS button alerts administrators and your emergency contacts instantly.' },
    { icon: '💬', title: 'In-App Chat', desc: 'Communicate directly with your mechanic through our built-in real-time chat.' },
];

const steps = [
    { num: '01', title: 'Describe Your Issue', desc: 'Tell us what\'s wrong — flat tire, dead battery, engine trouble, or anything else.' },
    { num: '02', title: 'Get Matched', desc: 'Our smart algorithm finds the nearest qualified mechanic and dispatches them to you.' },
    { num: '03', title: 'Track & Relax', desc: 'Watch your mechanic approach in real-time and communicate via in-app chat.' },
    { num: '04', title: 'Pay & Rate', desc: 'Pay securely and rate your experience to help the community.' },
];

export default function LandingPage() {
    return (
        <div className="landing">
            {/* Hero */}
            <section className="landing-hero">
                <div className="landing-hero__bg" />
                <div className="landing-hero__content container">
                    <span className="landing-hero__badge">🚗 #1 Roadside Assistance Platform</span>
                    <h1 className="landing-hero__title">
                        Roadside Help,<br /><span className="landing-hero__accent">In Minutes.</span>
                    </h1>
                    <p className="landing-hero__subtitle">
                        Connect with verified mechanics near you instantly. From flat tires to engine trouble — we've got you covered 24/7.
                    </p>
                    <div className="landing-hero__cta">
                        <Link to="/signup" className="btn btn-primary btn-lg">Get Started Free</Link>
                        <Link to="/login" className="btn btn-secondary btn-lg">Sign In</Link>
                    </div>
                    <div className="landing-hero__stats">
                        <div className="landing-hero__stat">
                            <span className="landing-hero__stat-value">5K+</span>
                            <span className="landing-hero__stat-label">Mechanics</span>
                        </div>
                        <div className="landing-hero__stat">
                            <span className="landing-hero__stat-value">50K+</span>
                            <span className="landing-hero__stat-label">Rescues</span>
                        </div>
                        <div className="landing-hero__stat">
                            <span className="landing-hero__stat-value">4.9★</span>
                            <span className="landing-hero__stat-label">Rating</span>
                        </div>
                    </div>
                </div>
            </section>

            {/* Features */}
            <section className="landing-section container" id="features">
                <h2 className="landing-section__title">Why RoadAid?</h2>
                <p className="landing-section__subtitle">Everything you need for roadside peace of mind.</p>
                <div className="landing-features">
                    {features.map((f, i) => (
                        <div key={i} className="landing-feature card animate-slideUp" style={{ animationDelay: `${i * 80}ms` }}>
                            <span className="landing-feature__icon">{f.icon}</span>
                            <h4>{f.title}</h4>
                            <p>{f.desc}</p>
                        </div>
                    ))}
                </div>
            </section>

            {/* How It Works */}
            <section className="landing-section container" id="how-it-works">
                <h2 className="landing-section__title">How It Works</h2>
                <p className="landing-section__subtitle">Get help in 4 simple steps.</p>
                <div className="landing-steps">
                    {steps.map((s, i) => (
                        <div key={i} className="landing-step">
                            <span className="landing-step__num">{s.num}</span>
                            <h4>{s.title}</h4>
                            <p>{s.desc}</p>
                        </div>
                    ))}
                </div>
            </section>

            {/* CTA */}
            <section className="landing-cta">
                <div className="container text-center">
                    <h2>Ready to Never Be Stranded Again?</h2>
                    <p>Join thousands of drivers who trust RoadAid for instant roadside assistance.</p>
                    <Link to="/signup" className="btn btn-primary btn-lg" style={{ marginTop: 'var(--space-6)' }}>
                        Sign Up Now — It's Free
                    </Link>
                </div>
            </section>

            {/* Footer */}
            <footer className="landing-footer container">
                <p style={{ color: 'var(--text-muted)', textAlign: 'center' }}>
                    © {new Date().getFullYear()} RoadAid Network. All rights reserved.
                </p>
            </footer>
        </div>
    );
}
