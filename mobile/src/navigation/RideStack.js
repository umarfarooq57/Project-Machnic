import React from 'react';
import { createStackNavigator } from '@react-navigation/stack';
import ActiveRide from '../screens/ride/ActiveRide';
import Tracking from '../screens/ride/Tracking';
import Rating from '../screens/ride/Rating';

const Stack = createStackNavigator();

export default function RideStack() {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      <Stack.Screen name="ActiveRide" component={ActiveRide} />
      <Stack.Screen name="Tracking" component={Tracking} />
      <Stack.Screen name="Rating" component={Rating} />
    </Stack.Navigator>
  );
}
