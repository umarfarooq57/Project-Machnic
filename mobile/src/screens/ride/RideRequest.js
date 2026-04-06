/**
 * Ride Request Screen — Alias for ServiceRequest from ride stack.
 */
import React from 'react';
import ServiceRequest from '../home/RideRequest';

export default function RideRequest({ route, navigation }) {
  return <ServiceRequest route={route} navigation={navigation} />;
}
