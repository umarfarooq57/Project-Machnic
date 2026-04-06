/**
 * Loader — Full-screen loading overlay.
 */
import React from 'react';
import { View, ActivityIndicator, StyleSheet } from 'react-native';

export default function Loader() {
  return (
    <View style={styles.overlay}>
      <ActivityIndicator size="large" color="#6366f1" />
    </View>
  );
}

const styles = StyleSheet.create({
  overlay: {
    ...StyleSheet.absoluteFillObject,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'rgba(0, 0, 0, 0.4)',
    zIndex: 50,
  },
});
