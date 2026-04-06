/**
 * Ride Chat Screen — Chat accessible from ride stack.
 */
import React from 'react';
import ChatScreen from '../chat/ChatScreen';

export default function RideChat({ route, navigation }) {
  return <ChatScreen route={route} navigation={navigation} />;
}
