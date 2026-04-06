/**
 * Active Ride Screen — Shows live request status, mechanic info, map, cancel option.
 */
import React, { useEffect, useState } from 'react';
import {
  View, Text, TouchableOpacity, StyleSheet, ActivityIndicator,
} from 'react-native';
import MapView, { Marker } from 'react-native-maps';
import { useRequestStore } from '../../store/requestStore';

const STATUS_LABELS = {
  pending: '⏳ Searching for mechanic…',
  accepted: '✅ Mechanic accepted!',
  en_route: '🚗 Mechanic is on the way',
  arrived: '📍 Mechanic has arrived',
  in_progress: '🔧 Service in progress',
  completed: '🏁 Service completed',
  cancelled: '❌ Cancelled',
};

export default function ActiveRide({ route, navigation }) {
  const requestId = route?.params?.requestId;
  const { activeRequest, fetchActiveRequest, cancelRequest, loading } = useRequestStore();
  const [polling, setPolling] = useState(null);

  useEffect(() => {
    if (requestId) {
      fetchActiveRequest(requestId);
      const interval = setInterval(() => fetchActiveRequest(requestId), 5000);
      setPolling(interval);
      return () => clearInterval(interval);
    }
  }, [requestId]);

  useEffect(() => {
    if (activeRequest?.status === 'completed') {
      if (polling) clearInterval(polling);
      navigation.navigate('Rating', { requestId: activeRequest.id });
    }
  }, [activeRequest?.status]);

  const handleCancel = async () => {
    if (activeRequest) {
      await cancelRequest(activeRequest.id);
      navigation.goBack();
    }
  };

  if (loading && !activeRequest) {
    return (
      <View style={styles.loading}>
        <ActivityIndicator size="large" color="#6366f1" />
        <Text style={styles.loadingText}>Loading request…</Text>
      </View>
    );
  }

  const req = activeRequest;
  const helperLat = req?.helper_latitude || req?.user_latitude || 24.86;
  const helperLng = req?.helper_longitude || req?.user_longitude || 67.00;
  const userLat = req?.user_latitude || 24.86;
  const userLng = req?.user_longitude || 67.00;

  return (
    <View style={styles.container}>
      <MapView
        style={StyleSheet.absoluteFillObject}
        initialRegion={{
          latitude: userLat,
          longitude: userLng,
          latitudeDelta: 0.02,
          longitudeDelta: 0.02,
        }}
      >
        <Marker coordinate={{ latitude: userLat, longitude: userLng }} title="Your Location" pinColor="#6366f1" />
        {req?.helper && (
          <Marker coordinate={{ latitude: helperLat, longitude: helperLng }} title="Mechanic" pinColor="#f97316" />
        )}
      </MapView>

      <View style={styles.panel}>
        <Text style={styles.status}>{STATUS_LABELS[req?.status] || req?.status}</Text>

        {req?.helper_name && (
          <View style={styles.helperInfo}>
            <Text style={styles.helperName}>🔧 {req.helper_name}</Text>
            {req.helper_rating && <Text style={styles.helperRating}>⭐ {req.helper_rating}</Text>}
          </View>
        )}

        {req?.estimated_price && (
          <Text style={styles.price}>Estimated: ${req.estimated_price}</Text>
        )}

        {['pending', 'accepted', 'en_route'].includes(req?.status) && (
          <TouchableOpacity style={styles.cancelBtn} onPress={handleCancel}>
            <Text style={styles.cancelBtnText}>Cancel Request</Text>
          </TouchableOpacity>
        )}

        {req?.status === 'arrived' && (
          <TouchableOpacity
            style={styles.chatBtn}
            onPress={() => navigation.navigate('Chat', { requestId: req.id })}
          >
            <Text style={styles.chatBtnText}>💬 Chat with Mechanic</Text>
          </TouchableOpacity>
        )}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  loading: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#0f0f23' },
  loadingText: { color: '#9ca3af', marginTop: 12 },
  panel: {
    position: 'absolute', bottom: 0, left: 0, right: 0,
    backgroundColor: 'rgba(15, 15, 35, 0.95)',
    borderTopLeftRadius: 24, borderTopRightRadius: 24,
    padding: 24, paddingBottom: 40,
  },
  status: { fontSize: 18, fontWeight: '700', color: '#f9fafb', marginBottom: 12 },
  helperInfo: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 8 },
  helperName: { color: '#f9fafb', fontSize: 16, fontWeight: '600' },
  helperRating: { color: '#f59e0b', fontSize: 15 },
  price: { color: '#10b981', fontSize: 16, fontWeight: '600', marginBottom: 16 },
  cancelBtn: {
    backgroundColor: '#ef4444', borderRadius: 14, paddingVertical: 14, alignItems: 'center',
  },
  cancelBtnText: { color: '#fff', fontWeight: '700', fontSize: 15 },
  chatBtn: {
    backgroundColor: '#6366f1', borderRadius: 14, paddingVertical: 14, alignItems: 'center',
  },
  chatBtnText: { color: '#fff', fontWeight: '700', fontSize: 15 },
});
