/**
 * Chat Page - Real-time messaging between user and helper.
 */
import { useEffect, useState, useRef } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useChatStore } from '../../store/chatStore';
import { useAuthStore } from '../../store/authStore';
import './Chat.css';

function ChatPage() {
    const { roomId } = useParams();
    const { messages, fetchMessages, sendMessage, addMessage, setTypingIndicator, isTyping, typingUser } = useChatStore();
    const { user } = useAuthStore();
    const [newMessage, setNewMessage] = useState('');
    const [ws, setWs] = useState(null);
    const messagesEndRef = useRef(null);

    useEffect(() => {
        fetchMessages(roomId);

        // Setup WebSocket
        const wsUrl = `${import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws'}/chat/${roomId}/`;
        const socket = new WebSocket(wsUrl);

        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.type === 'message') {
                addMessage(data.message);
            } else if (data.type === 'typing') {
                setTypingIndicator(data.is_typing, data.user_name);
            }
        };

        setWs(socket);
        return () => socket.close();
    }, [roomId]);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const handleSend = async (e) => {
        e.preventDefault();
        if (!newMessage.trim()) return;

        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: 'message', content: newMessage }));
        } else {
            await sendMessage(roomId, newMessage);
        }

        setNewMessage('');
    };

    const handleTyping = () => {
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: 'typing', is_typing: true }));
            setTimeout(() => {
                ws.send(JSON.stringify({ type: 'typing', is_typing: false }));
            }, 2000);
        }
    };

    return (
        <div className="chat-page animate-fadeIn">
            <div className="chat-header">
                <Link to="/dashboard" className="back-btn">←</Link>
                <div className="chat-title">
                    <h2>💬 Chat</h2>
                    {isTyping && <span className="typing-indicator">{typingUser} is typing...</span>}
                </div>
            </div>

            <div className="messages-container">
                {messages.map((msg) => (
                    <div
                        key={msg.id}
                        className={`message ${msg.sender?.id === user?.id ? 'own' : 'other'}`}
                    >
                        <div className="message-bubble">
                            <p>{msg.content}</p>
                            <span className="message-time">
                                {new Date(msg.sent_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                            </span>
                        </div>
                    </div>
                ))}
                <div ref={messagesEndRef} />
            </div>

            <form className="chat-input-form" onSubmit={handleSend}>
                <input
                    type="text"
                    className="input chat-input"
                    placeholder="Type a message..."
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    onKeyDown={handleTyping}
                />
                <button type="submit" className="btn btn-primary">Send</button>
            </form>
        </div>
    );
}

export default ChatPage;
