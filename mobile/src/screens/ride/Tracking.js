/**
 * Tracking Screen — Real-time map tracking of the mechanic.
 */
import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, ActivityIndicator } from 'react-native';
import MapView, { Marker, Polyline } from 'react-native-maps';
import { useRequestStore } from '../../store/requestStore';

export default function Tracking({ route }) {
  const requestId = route?.params?.requestId;
  const { activeRequest, fetchActiveRequest } = useRequestStore();

  useEffect(() => {
    if (requestId) {
      fetchActiveRequest(requestId);
      const interval = setInterval(() => fetchActiveRequest(requestId), 3000);
      return () => clearInterval(interval);
    }
  }, [requestId]);

  const userCoord = activeRequest ? {
    latitude: activeRequest.user_latitude || 24.86,
    longitude: activeRequest.user_longitude || 67.00,
  } : null;

  const helperCoord = activeRequest?.helper_latitude ? {
    latitude: activeRequest.helper_latitude,
    longitude: activeRequest.helper_longitude,
  } : null;

  if (!userCoord) {
    return (
      <View style={styles.loading}>
        <ActivityIndicator size="large" color="#6366f1" />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <MapView
        style={StyleSheet.absoluteFillObject}
        region={{
          ...userCoord,
          latitudeDelta: 0.03,
          longitudeDelta: 0.03,
        }}
      >
        <Marker coordinate={userCoord} title="You" pinColor="#6366f1" />
        {helperCoord && <Marker coordinate={helperCoord} title="Mechanic" pinColor="#f97316" />}
        {helperCoord && <Polyline coordinates={[helperCoord, userCoord]} strokeColor="#6366f1" strokeWidth={3} />}
      </MapView>

      <View style={styles.panel}>
        <Text style={styles.status}>{activeRequest?.status === 'en_route' ? '🚗 Mechanic on the way' : '📍 Live Tracking'}</Text>
        {activeRequest?.helper_name && (
          <Text style={styles.helperName}>{activeRequest.helper_name}</Text>
        )}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  loading: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#0f0f23' },
  panel: {
    position: 'absolute', top: 60, left: 16, right: 16,
    backgroundColor: 'rgba(15, 15, 35, 0.9)', borderRadius: 16, padding: 16,
  },
  status: { color: '#f9fafb', fontSize: 16, fontWeight: '700' },
  helperName: { color: '#9ca3af', fontSize: 14, marginTop: 4 },
});
