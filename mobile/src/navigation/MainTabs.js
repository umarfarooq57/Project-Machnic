/**
 * Main Tab Navigator — Home, Request, Payments, Notifications, Profile.
 * Uses Ionicons for tab icons and a premium dark theme.
 */
import React from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Ionicons } from '@expo/vector-icons';
import HomeScreen from '../screens/home/HomeScreen';
import ServiceRequest from '../screens/home/RideRequest';
import PaymentScreen from '../screens/payments/PaymentScreen';
import NotificationScreen from '../screens/notifications/NotificationScreen';
import ProfileScreen from '../screens/profile/ProfileScreen';
import { useNotificationStore } from '../store/notificationStore';

const Tab = createBottomTabNavigator();

export default function MainTabs() {
  const unreadCount = useNotificationStore((s) => s.unreadCount);

  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        headerShown: false,
        tabBarStyle: {
          backgroundColor: '#0c0c1d',
          borderTopColor: 'rgba(255,255,255,0.06)',
          paddingBottom: 8,
          paddingTop: 8,
          height: 64,
        },
        tabBarActiveTintColor: '#818cf8',
        tabBarInactiveTintColor: '#4b5563',
        tabBarIcon: ({ color, size }) => {
          const icons = {
            Home: 'home',
            Request: 'construct',
            Payments: 'card',
            Notifications: 'notifications',
            Profile: 'person',
          };
          return <Ionicons name={icons[route.name]} size={size} color={color} />;
        },
      })}
    >
      <Tab.Screen name="Home" component={HomeScreen} />
      <Tab.Screen name="Request" component={ServiceRequest} />
      <Tab.Screen name="Payments" component={PaymentScreen} />
      <Tab.Screen
        name="Notifications"
        component={NotificationScreen}
        options={{
          tabBarBadge: unreadCount > 0 ? unreadCount : undefined,
          tabBarBadgeStyle: { backgroundColor: '#ef4444', fontSize: 10 },
        }}
      />
      <Tab.Screen name="Profile" component={ProfileScreen} />
    </Tab.Navigator>
  );
}
