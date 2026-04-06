/**
 * Service Request Screen — select vehicle, service, describe issue, apply promo.
 */
import React, { useState, useEffect } from 'react';
import {
  View, Text, TextInput, TouchableOpacity, StyleSheet,
  ScrollView, Alert, ActivityIndicator,
} from 'react-native';
import * as Location from 'expo-location';
import api from '../../services/api';
import { useRequestStore } from '../../store/requestStore';

export default function ServiceRequest({ navigation }) {
  const [vehicleTypes, setVehicleTypes] = useState([]);
  const [serviceTypes, setServiceTypes] = useState([]);
  const [selectedVehicle, setSelectedVehicle] = useState(null);
  const [selectedService, setSelectedService] = useState(null);
  const [description, setDescription] = useState('');
  const [urgency, setUrgency] = useState('medium');
  const [promoCode, setPromoCode] = useState('');
  const [promoResult, setPromoResult] = useState(null);
  const [location, setLocation] = useState(null);

  const { createRequest, applyPromoCode, loading, error } = useRequestStore();

  useEffect(() => {
    (async () => {
      try {
        const [vRes, sRes] = await Promise.all([
          api.get('/helpers/vehicle-types/'),
          api.get('/helpers/service-types/'),
        ]);
        setVehicleTypes(vRes.data.results || vRes.data);
        setServiceTypes(sRes.data.results || sRes.data);
      } catch { /* use fallbacks */ }

      const loc = await Location.getCurrentPositionAsync({});
      setLocation(loc.coords);
    })();
  }, []);

  const handleApplyPromo = async () => {
    if (!promoCode.trim()) return;
    const basePrice = selectedService
      ? serviceTypes.find(s => s.id === selectedService)?.base_price || 100
      : 100;
    const result = await applyPromoCode(promoCode, basePrice);
    if (result) {
      setPromoResult(result);
      Alert.alert('Promo Applied', `Discount: $${result.discount_amount}`);
    } else {
      Alert.alert('Invalid', 'Promo code is invalid or expired.');
    }
  };

  const handleSubmit = async () => {
    if (!selectedVehicle) return Alert.alert('Error', 'Select a vehicle type');
    if (!description.trim()) return Alert.alert('Error', 'Describe your issue');
    if (!location) return Alert.alert('Error', 'Location not available');

    const data = {
      vehicle_type: selectedVehicle,
      service_type: selectedService,
      issue_description: description,
      user_latitude: location.latitude,
      user_longitude: location.longitude,
      urgency,
    };
    const result = await createRequest(data);
    if (result) {
      navigation.navigate('Active', { requestId: result.request?.id || result.id });
    }
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.title}>Request Mechanic</Text>

      {/* Vehicle Type */}
      <Text style={styles.label}>Vehicle Type</Text>
      <View style={styles.chipRow}>
        {vehicleTypes.map(v => (
          <TouchableOpacity
            key={v.id}
            style={[styles.chip, selectedVehicle === v.id && styles.chipActive]}
            onPress={() => setSelectedVehicle(v.id)}
          >
            <Text style={[styles.chipText, selectedVehicle === v.id && styles.chipTextActive]}>
              {v.name}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      {/* Service Type */}
      <Text style={styles.label}>Service Needed</Text>
      <View style={styles.chipRow}>
        {serviceTypes.map(s => (
          <TouchableOpacity
            key={s.id}
            style={[styles.chip, selectedService === s.id && styles.chipActive]}
            onPress={() => setSelectedService(s.id)}
          >
            <Text style={[styles.chipText, selectedService === s.id && styles.chipTextActive]}>
              {s.name}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      {/* Description */}
      <Text style={styles.label}>Describe the Issue</Text>
      <TextInput
        style={styles.textArea}
        multiline
        numberOfLines={4}
        placeholder="e.g. Flat tire on the highway, right rear..."
        placeholderTextColor="#6b7280"
        value={description}
        onChangeText={setDescription}
      />

      {/* Urgency */}
      <Text style={styles.label}>Urgency</Text>
      <View style={styles.chipRow}>
        {['low', 'medium', 'high'].map(u => (
          <TouchableOpacity
            key={u}
            style={[styles.chip, urgency === u && styles.chipActive]}
            onPress={() => setUrgency(u)}
          >
            <Text style={[styles.chipText, urgency === u && styles.chipTextActive]}>
              {u.charAt(0).toUpperCase() + u.slice(1)}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      {/* Promo Code */}
      <Text style={styles.label}>Promo Code (optional)</Text>
      <View style={styles.promoRow}>
        <TextInput
          style={[styles.input, { flex: 1 }]}
          placeholder="Enter code"
          placeholderTextColor="#6b7280"
          autoCapitalize="characters"
          value={promoCode}
          onChangeText={setPromoCode}
        />
        <TouchableOpacity style={styles.promoBtn} onPress={handleApplyPromo}>
          <Text style={styles.promoBtnText}>Apply</Text>
        </TouchableOpacity>
      </View>
      {promoResult && (
        <Text style={styles.promoSuccess}>
          ✅ Discount: ${promoResult.discount_amount} → Final: ${promoResult.final_amount}
        </Text>
      )}

      {error ? <Text style={styles.error}>{error}</Text> : null}

      <TouchableOpacity style={styles.submitBtn} onPress={handleSubmit} disabled={loading}>
        {loading ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <Text style={styles.submitBtnText}>Find Mechanic</Text>
        )}
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0f0f23' },
  content: { padding: 24, paddingBottom: 48 },
  title: { fontSize: 28, fontWeight: '800', color: '#f9fafb', marginBottom: 24 },
  label: { fontSize: 14, fontWeight: '600', color: '#9ca3af', marginBottom: 8, marginTop: 16 },
  chipRow: { flexDirection: 'row', flexWrap: 'wrap', gap: 8 },
  chip: {
    paddingHorizontal: 16, paddingVertical: 10, borderRadius: 12,
    backgroundColor: 'rgba(255,255,255,0.05)', borderWidth: 1, borderColor: 'rgba(255,255,255,0.1)',
  },
  chipActive: { backgroundColor: '#6366f1', borderColor: '#6366f1' },
  chipText: { color: '#9ca3af', fontWeight: '600', fontSize: 13 },
  chipTextActive: { color: '#fff' },
  textArea: {
    backgroundColor: 'rgba(255,255,255,0.05)', borderWidth: 1, borderColor: 'rgba(255,255,255,0.1)',
    borderRadius: 12, padding: 14, color: '#f9fafb', fontSize: 15, textAlignVertical: 'top',
    minHeight: 100,
  },
  input: {
    backgroundColor: 'rgba(255,255,255,0.05)', borderWidth: 1, borderColor: 'rgba(255,255,255,0.1)',
    borderRadius: 12, padding: 14, color: '#f9fafb', fontSize: 15,
  },
  promoRow: { flexDirection: 'row', gap: 10 },
  promoBtn: {
    backgroundColor: '#f97316', paddingHorizontal: 20, borderRadius: 12,
    justifyContent: 'center',
  },
  promoBtnText: { color: '#fff', fontWeight: '700' },
  promoSuccess: { color: '#10b981', fontSize: 13, marginTop: 6 },
  error: { color: '#ef4444', marginTop: 8 },
  submitBtn: {
    backgroundColor: '#6366f1', borderRadius: 16, paddingVertical: 18,
    alignItems: 'center', marginTop: 32,
  },
  submitBtnText: { color: '#fff', fontWeight: '700', fontSize: 17 },
});
