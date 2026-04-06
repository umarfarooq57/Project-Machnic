# Project-Machnic Mobile App

## Overview
A full-featured React Native (Expo) mobile app for Project-Machnic, supporting ride requests, real-time tracking, chat, payments, notifications, and user profile management.

---

## Features
- **Authentication:** Login, register, onboarding (Zustand + SecureStore)
- **Home:** Map with current location, request ride
- **Ride:** Request, active ride tracking, chat, rating
- **Payments:** Card input, payment (Stripe integration ready)
- **Notifications:** Push notifications (Expo Notifications)
- **Profile:** View and logout
- **Navigation:** Auth stack, main tabs, ride stack

---

## Folder Structure
```
mobile/
  App.js
  src/
    navigation/
      AuthStack.js
      AppTabs.js
      MainTabs.js
      RideStack.js
      AppNavigator.js
    screens/
      auth/
        Login.js
        Register.js
        Onboarding.js
      home/
        HomeScreen.js
      ride/
        RideRequest.js
        ActiveRide.js
        RideChat.js
        Tracking.js
        Rating.js
      payments/
        PaymentScreen.js
      notifications/
        NotificationScreen.js
      profile/
        Profile.js
    store/
      authStore.js
```

---

## Usage
1. **Install dependencies:**
   ```sh
   cd mobile
   npm install
   expo install react-native-maps expo-location expo-notifications zustand axios @react-navigation/native @react-navigation/stack @react-navigation/bottom-tabs @expo/vector-icons expo-secure-store
   ```
2. **Start the app:**
   ```sh
   expo start
   ```
3. **Configure backend API:**
   - Edit `src/store/authStore.js` and set `API_URL` to your backend endpoint.

---

## Integration
- **Auth:** JWT-based, stored in SecureStore
- **API:** All requests go to backend Django endpoints
- **Push:** Expo Notifications (register device on login)
- **Payments:** Stripe integration (add publishable key)

---

## Deployment
- Build for iOS/Android using Expo EAS
- Configure environment variables for production endpoints

---

## Next Steps
- Connect all TODOs to backend endpoints
- Add real-time WebSocket for chat/ride updates
- Polish UI/UX and test on devices

---

For any issues, see the code comments and TODOs in each file.
