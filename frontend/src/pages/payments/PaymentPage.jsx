/**
 * Payment Page - Complete payment for a service.
 */
import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useRequestStore } from '../../store/requestStore';
import api from '../../api/client';
import toast from 'react-hot-toast';
import './Payment.css';

function PaymentPage() {
    const { requestId } = useParams();
    const navigate = useNavigate();
    const { activeRequest, fetchRequest } = useRequestStore();
    const [paymentMethod, setPaymentMethod] = useState('card');
    const [isLoading, setIsLoading] = useState(false);

    useEffect(() => {
        fetchRequest(requestId);
    }, [requestId]);

    const handlePayment = async () => {
        setIsLoading(true);
        try {
            const response = await api.post('/payments/create/', {
                request_id: requestId,
                payment_method: paymentMethod,
            });

            if (paymentMethod === 'wallet') {
                toast.success('Payment completed!');
                navigate('/dashboard');
            } else {
                // For card payments, would integrate with Stripe Elements
                toast.success('Payment intent created. Stripe integration ready.');
                navigate('/dashboard');
            }
        } catch (error) {
            toast.error(error.response?.data?.error || 'Payment failed');
        }
        setIsLoading(false);
    };

    if (!activeRequest) {
        return (
            <div className="loading-state" style={{ height: '50vh' }}>
                <div className="loader"></div>
            </div>
        );
    }

    const amount = activeRequest.final_price || activeRequest.estimated_price || 0;

    return (
        <div className="payment-page animate-fadeIn">
            <div className="page-header">
                <h1>💳 Complete Payment</h1>
                <p>Pay for your roadside assistance service.</p>
            </div>

            <div className="payment-container">
                {/* Order Summary */}
                <div className="payment-card card">
                    <h3>Order Summary</h3>
                    <div className="order-details">
                        <div className="order-row">
                            <span>Service Type</span>
                            <span>{activeRequest.vehicle_type?.name}</span>
                        </div>
                        <div className="order-row">
                            <span>Helper</span>
                            <span>{activeRequest.helper?.user?.full_name}</span>
                        </div>
                        <div className="order-row total">
                            <span>Total</span>
                            <span className="amount">${parseFloat(amount).toFixed(2)}</span>
                        </div>
                    </div>
                </div>

                {/* Payment Method */}
                <div className="payment-card card">
                    <h3>Payment Method</h3>
                    <div className="payment-methods">
                        <div
                            className={`payment-option ${paymentMethod === 'card' ? 'selected' : ''}`}
                            onClick={() => setPaymentMethod('card')}
                        >
                            <span className="payment-icon">💳</span>
                            <div>
                                <h4>Credit/Debit Card</h4>
                                <p>Pay securely with Stripe</p>
                            </div>
                        </div>
                        <div
                            className={`payment-option ${paymentMethod === 'wallet' ? 'selected' : ''}`}
                            onClick={() => setPaymentMethod('wallet')}
                        >
                            <span className="payment-icon">👛</span>
                            <div>
                                <h4>App Wallet</h4>
                                <p>Pay from your balance</p>
                            </div>
                        </div>
                        <div
                            className={`payment-option ${paymentMethod === 'cash' ? 'selected' : ''}`}
                            onClick={() => setPaymentMethod('cash')}
                        >
                            <span className="payment-icon">💵</span>
                            <div>
                                <h4>Cash</h4>
                                <p>Pay the helper directly</p>
                            </div>
                        </div>
                    </div>
                </div>

                <button
                    className="btn btn-accent btn-lg w-full"
                    onClick={handlePayment}
                    disabled={isLoading}
                >
                    {isLoading ? 'Processing...' : `Pay $${parseFloat(amount).toFixed(2)}`}
                </button>
            </div>
        </div>
    );
}

export default PaymentPage;
