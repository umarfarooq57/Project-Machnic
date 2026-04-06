/**
 * Home Screen — Map with location + Request Service button + SOS.
 */
import React, { useEffect, useState } from 'react';
import {
  View, Text, TouchableOpacity, StyleSheet, Alert, ActivityIndicator,
} from 'react-native';
import MapView, { Marker } from 'react-native-maps';
import * as Location from 'expo-location';
import { useRequestStore } from '../../store/requestStore';

export default function HomeScreen({ navigation }) {
  const [location, setLocation] = useState(null);
  const [errorMsg, setErrorMsg] = useState(null);
  const { triggerSOS } = useRequestStore();

  useEffect(() => {
    (async () => {
      const { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== 'granted') {
        setErrorMsg('Location permission denied');
        return;
      }
      const loc = await Location.getCurrentPositionAsync({});
      setLocation(loc.coords);
    })();
  }, []);

  const handleSOS = async () => {
    Alert.alert('🚨 SOS Alert', 'Send emergency SOS to admins and your emergency contacts?', [
      { text: 'Cancel', style: 'cancel' },
      {
        text: 'Send SOS', style: 'destructive', onPress: async () => {
          if (!location) return Alert.alert('Error', 'Location not available');
          const result = await triggerSOS(location.latitude, location.longitude, 'Emergency!');
          if (result) {
            Alert.alert('SOS Sent', 'Admins and emergency contacts have been notified.');
          }
        },
      },
    ]);
  };

  return (
    <View style={styles.container}>
      {location ? (
        <MapView
          style={StyleSheet.absoluteFillObject}
          initialRegion={{
            latitude: location.latitude,
            longitude: location.longitude,
            latitudeDelta: 0.01,
            longitudeDelta: 0.01,
          }}
        >
          <Marker coordinate={location} title="You are here" />
        </MapView>
      ) : (
        <View style={styles.loading}>
          {errorMsg ? (
            <Text style={styles.errorText}>{errorMsg}</Text>
          ) : (
            <ActivityIndicator size="large" color="#6366f1" />
          )}
        </View>
      )}

      {/* Bottom Action Panel */}
      <View style={styles.bottomPanel}>
        <TouchableOpacity
          style={styles.requestBtn}
          onPress={() => navigation.navigate('Request')}
        >
          <Text style={styles.requestBtnText}>🔧  Request Service</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.sosBtn} onPress={handleSOS}>
          <Text style={styles.sosBtnText}>🚨 SOS</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  loading: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#0f0f23' },
  errorText: { color: '#ef4444', fontSize: 16 },
  bottomPanel: {
    position: 'absolute', bottom: 0, left: 0, right: 0,
    flexDirection: 'row', alignItems: 'center', gap: 12,
    padding: 20, paddingBottom: 36,
    backgroundColor: 'rgba(15, 15, 35, 0.95)',
    borderTopLeftRadius: 24, borderTopRightRadius: 24,
  },
  requestBtn: {
    flex: 1, paddingVertical: 16, borderRadius: 16,
    backgroundColor: '#6366f1', alignItems: 'center',
  },
  requestBtnText: { color: '#fff', fontWeight: '700', fontSize: 16 },
  sosBtn: {
    width: 60, height: 60, borderRadius: 30,
    backgroundColor: '#ef4444', alignItems: 'center', justifyContent: 'center',
  },
  sosBtnText: { color: '#fff', fontWeight: '800', fontSize: 14 },
});
