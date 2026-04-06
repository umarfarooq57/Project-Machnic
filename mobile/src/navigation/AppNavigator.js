/**
 * App Navigator — Combines MainTabs with ride-related stack screens.
 */
import React from 'react';
import { createStackNavigator } from '@react-navigation/stack';
import MainTabs from './MainTabs';
import ActiveRide from '../screens/ride/ActiveRide';
import Tracking from '../screens/ride/Tracking';
import Rating from '../screens/ride/Rating';
import ChatScreen from '../screens/chat/ChatScreen';
import RideChat from '../screens/ride/RideChat';

const Stack = createStackNavigator();

export default function AppNavigator() {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      <Stack.Screen name="MainTabs" component={MainTabs} />
      <Stack.Screen name="Active" component={ActiveRide} />
      <Stack.Screen name="Tracking" component={Tracking} />
      <Stack.Screen name="Rating" component={Rating} />
      <Stack.Screen name="Chat" component={ChatScreen} />
      <Stack.Screen name="RideChat" component={RideChat} />
    </Stack.Navigator>
  );
}
