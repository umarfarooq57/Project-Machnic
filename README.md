# RoadAid Network

Real-time hyper-local mechanic and roadside assistance platform.

## 🚗 Features

- **User Registration & Authentication** - JWT-based auth with email verification
- **Breakdown Reporting** - Quick request creation with geolocation
- **Nearby Helper Matching** - Automatically find and notify nearby helpers
- **Real-time Tracking** - Live ETA updates and location tracking
- **In-app Chat** - WebSocket-based messaging between users and helpers
- **Payment Integration** - Stripe for card payments, wallet, and cash options
- **Rating System** - Post-service ratings for quality assurance
- **Push Notifications** - FCM for real-time alerts

## 🛠️ Tech Stack

### Backend
- Django 5.0 + Django REST Framework
- Django Channels (WebSockets)
- PostgreSQL + PostGIS
- Redis (caching & Celery broker)
- Celery (background tasks)
- JWT Authentication
- Stripe Payments
- Firebase Cloud Messaging

### Frontend
- React 18 + Vite
- React Router v6
- Zustand (state management)
- Leaflet (maps)
- Stripe React SDK

## 📁 Project Structure

```
roadaid-network/
├── backend/
│   ├── apps/
│   │   ├── users/       # Authentication & user management
│   │   ├── helpers/     # Helper profiles & services
│   │   ├── requests/    # Service request handling
│   │   ├── chat/        # Real-time messaging
│   │   ├── notifications/ # Push & in-app notifications
│   │   └── payments/    # Payment processing
│   ├── core/           # Shared utilities & mixins
│   ├── roadaid/        # Django project settings
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/        # API client
│   │   ├── components/ # Reusable components
│   │   ├── pages/      # Page components
│   │   └── store/      # Zustand stores
│   └── package.json
└── docker-compose.yml
```

## 🚀 Getting Started

### Prerequisites
- Python 3.12+
- Node.js 20+
- PostgreSQL 16+
- Redis 7+

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env with your settings

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

### Docker Setup

```bash
# Run entire stack
docker-compose up -d

# View logs
docker-compose logs -f
```

## 📡 API Endpoints

### Authentication
- `POST /api/v1/auth/register/` - User registration
- `POST /api/v1/auth/login/` - Login (JWT)
- `POST /api/v1/auth/logout/` - Logout
- `GET /api/v1/auth/profile/` - Get profile

### Helpers
- `POST /api/v1/helpers/register/` - Register as helper
- `POST /api/v1/helpers/availability/` - Toggle availability
- `GET /api/v1/helpers/nearby/` - Find nearby helpers

### Requests
- `POST /api/v1/requests/` - Create request
- `GET /api/v1/requests/{id}/` - Get request details
- `POST /api/v1/requests/{id}/accept/` - Accept request
- `POST /api/v1/requests/{id}/status/` - Update status

### Chat
- `GET /api/v1/chat/request/{id}/` - Get chat room
- `POST /api/v1/chat/{id}/send/` - Send message

### Payments
- `POST /api/v1/payments/create/` - Create payment
- `POST /api/v1/payments/confirm/{id}/` - Confirm payment

## 🔌 WebSocket Endpoints

- `ws://localhost:8000/ws/requests/{request_id}/` - Request updates
- `ws://localhost:8000/ws/chat/{room_id}/` - Chat messages
- `ws://localhost:8000/ws/notifications/` - User notifications

## 📄 License

MIT License
"# Project-Machnic" 
