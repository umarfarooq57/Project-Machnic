/**
 * Rating Screen — Rate the mechanic after service completion.
 */
import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, Alert } from 'react-native';
import { useRequestStore } from '../../store/requestStore';

export default function Rating({ route, navigation }) {
  const requestId = route?.params?.requestId;
  const [rating, setRating] = useState(0);
  const [review, setReview] = useState('');
  const { submitRating } = useRequestStore();

  const handleSubmit = async () => {
    if (rating === 0) return Alert.alert('Error', 'Please select a rating');
    await submitRating(requestId, rating, review);
    Alert.alert('Thank You!', 'Your rating has been submitted.');
    navigation.popToTop();
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Rate Your Mechanic</Text>
      <Text style={styles.subtitle}>How was your experience?</Text>

      <View style={styles.stars}>
        {[1, 2, 3, 4, 5].map(star => (
          <TouchableOpacity key={star} onPress={() => setRating(star)}>
            <Text style={[styles.star, star <= rating && styles.starActive]}>★</Text>
          </TouchableOpacity>
        ))}
      </View>

      <Text style={styles.ratingLabel}>
        {['', 'Poor', 'Fair', 'Good', 'Great', 'Excellent'][rating] || 'Tap to rate'}
      </Text>

      <TextInput
        style={styles.textArea}
        multiline
        numberOfLines={4}
        placeholder="Write a review (optional)..."
        placeholderTextColor="#6b7280"
        value={review}
        onChangeText={setReview}
      />

      <TouchableOpacity style={styles.submitBtn} onPress={handleSubmit}>
        <Text style={styles.submitBtnText}>Submit Rating</Text>
      </TouchableOpacity>

      <TouchableOpacity onPress={() => navigation.popToTop()} style={styles.skipBtn}>
        <Text style={styles.skipBtnText}>Skip</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0f0f23', justifyContent: 'center', padding: 32 },
  title: { fontSize: 28, fontWeight: '800', color: '#f9fafb', textAlign: 'center' },
  subtitle: { fontSize: 15, color: '#9ca3af', textAlign: 'center', marginTop: 6, marginBottom: 32 },
  stars: { flexDirection: 'row', justifyContent: 'center', gap: 8, marginBottom: 12 },
  star: { fontSize: 44, color: '#374151' },
  starActive: { color: '#f59e0b' },
  ratingLabel: { textAlign: 'center', color: '#f9fafb', fontSize: 16, fontWeight: '600', marginBottom: 24 },
  textArea: {
    backgroundColor: 'rgba(255,255,255,0.05)', borderWidth: 1, borderColor: 'rgba(255,255,255,0.1)',
    borderRadius: 14, padding: 14, color: '#f9fafb', fontSize: 15, textAlignVertical: 'top',
    minHeight: 100, marginBottom: 24,
  },
  submitBtn: {
    backgroundColor: '#6366f1', borderRadius: 16, paddingVertical: 16, alignItems: 'center',
  },
  submitBtnText: { color: '#fff', fontWeight: '700', fontSize: 16 },
  skipBtn: { marginTop: 16, alignItems: 'center' },
  skipBtnText: { color: '#6b7280', fontSize: 14 },
});
