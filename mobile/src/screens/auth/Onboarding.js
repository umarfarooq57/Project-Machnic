/**
 * Onboarding Screen — Swipeable intro slides.
 */
import React, { useState, useRef } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, FlatList, Dimensions } from 'react-native';

const { width } = Dimensions.get('window');

const slides = [
  { id: '1', emoji: '🔧', title: 'Roadside Assistance', description: 'Get instant help from verified mechanics wherever you are.' },
  { id: '2', emoji: '📍', title: 'Live Tracking', description: 'Track your mechanic in real-time as they head to your location.' },
  { id: '3', emoji: '💳', title: 'Easy Payments', description: 'Pay securely through the app. Use promo codes for discounts!' },
  { id: '4', emoji: '🚨', title: 'Emergency SOS', description: 'One-tap SOS alerts admins and your emergency contacts instantly.' },
];

export default function Onboarding({ navigation }) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const flatListRef = useRef(null);

  const handleNext = () => {
    if (currentIndex < slides.length - 1) {
      flatListRef.current?.scrollToIndex({ index: currentIndex + 1 });
    } else {
      navigation.replace('Login');
    }
  };

  const renderSlide = ({ item }) => (
    <View style={[styles.slide, { width }]}>
      <Text style={styles.emoji}>{item.emoji}</Text>
      <Text style={styles.slideTitle}>{item.title}</Text>
      <Text style={styles.slideDescription}>{item.description}</Text>
    </View>
  );

  return (
    <View style={styles.container}>
      <FlatList
        ref={flatListRef}
        data={slides}
        horizontal
        pagingEnabled
        showsHorizontalScrollIndicator={false}
        renderItem={renderSlide}
        keyExtractor={(item) => item.id}
        onMomentumScrollEnd={(e) => {
          setCurrentIndex(Math.round(e.nativeEvent.contentOffset.x / width));
        }}
      />

      <View style={styles.footer}>
        <View style={styles.dots}>
          {slides.map((_, i) => (
            <View key={i} style={[styles.dot, i === currentIndex && styles.dotActive]} />
          ))}
        </View>

        <TouchableOpacity style={styles.nextBtn} onPress={handleNext}>
          <Text style={styles.nextBtnText}>
            {currentIndex === slides.length - 1 ? 'Get Started' : 'Next'}
          </Text>
        </TouchableOpacity>

        {currentIndex < slides.length - 1 && (
          <TouchableOpacity onPress={() => navigation.replace('Login')}>
            <Text style={styles.skip}>Skip</Text>
          </TouchableOpacity>
        )}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0f0f23' },
  slide: { flex: 1, justifyContent: 'center', alignItems: 'center', padding: 40 },
  emoji: { fontSize: 72, marginBottom: 24 },
  slideTitle: { fontSize: 28, fontWeight: '800', color: '#f9fafb', textAlign: 'center' },
  slideDescription: { fontSize: 16, color: '#9ca3af', textAlign: 'center', marginTop: 12, lineHeight: 24 },
  footer: { alignItems: 'center', paddingBottom: 60, paddingHorizontal: 32 },
  dots: { flexDirection: 'row', gap: 8, marginBottom: 24 },
  dot: { width: 8, height: 8, borderRadius: 4, backgroundColor: '#374151' },
  dotActive: { backgroundColor: '#6366f1', width: 24 },
  nextBtn: {
    backgroundColor: '#6366f1', borderRadius: 14, paddingVertical: 16,
    paddingHorizontal: 48, alignItems: 'center', width: '100%',
  },
  nextBtnText: { color: '#fff', fontWeight: '700', fontSize: 16 },
  skip: { color: '#6b7280', marginTop: 16, fontSize: 14 },
});
