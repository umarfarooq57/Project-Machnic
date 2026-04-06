/**
 * Register Screen — Create account with confirmation.
 */
import React, { useState } from 'react';
import {
  View, Text, TextInput, TouchableOpacity, StyleSheet, ActivityIndicator, Alert,
} from 'react-native';
import { useAuthStore } from '../../store/authStore';

export default function Register({ navigation }) {
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [passwordConfirm, setPasswordConfirm] = useState('');
  const { register, loading, error } = useAuthStore();

  const handleRegister = async () => {
    if (!fullName.trim() || !email.trim() || !password || !passwordConfirm) {
      return Alert.alert('Error', 'Fill in all fields');
    }
    if (password !== passwordConfirm) {
      return Alert.alert('Error', 'Passwords do not match');
    }
    await register(email.trim(), fullName.trim(), password, passwordConfirm);
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Create Account</Text>
        <Text style={styles.subtitle}>Join the RoadAid network</Text>
      </View>

      <View style={styles.form}>
        <TextInput
          style={styles.input}
          placeholder="Full Name"
          placeholderTextColor="#6b7280"
          value={fullName}
          onChangeText={setFullName}
        />
        <TextInput
          style={styles.input}
          placeholder="Email"
          placeholderTextColor="#6b7280"
          autoCapitalize="none"
          keyboardType="email-address"
          value={email}
          onChangeText={setEmail}
        />
        <TextInput
          style={styles.input}
          placeholder="Password"
          placeholderTextColor="#6b7280"
          secureTextEntry
          value={password}
          onChangeText={setPassword}
        />
        <TextInput
          style={styles.input}
          placeholder="Confirm Password"
          placeholderTextColor="#6b7280"
          secureTextEntry
          value={passwordConfirm}
          onChangeText={setPasswordConfirm}
        />

        {error ? <Text style={styles.error}>{error}</Text> : null}

        <TouchableOpacity style={styles.registerBtn} onPress={handleRegister} disabled={loading}>
          {loading ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text style={styles.registerBtnText}>Sign Up</Text>
          )}
        </TouchableOpacity>

        <TouchableOpacity onPress={() => navigation.navigate('Login')}>
          <Text style={styles.link}>
            Already have an account? <Text style={styles.linkBold}>Sign In</Text>
          </Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0f0f23', justifyContent: 'center', padding: 32 },
  header: { alignItems: 'center', marginBottom: 32 },
  title: { fontSize: 28, fontWeight: '800', color: '#f9fafb' },
  subtitle: { color: '#9ca3af', fontSize: 14, marginTop: 6 },
  form: { gap: 14 },
  input: {
    backgroundColor: 'rgba(255,255,255,0.05)', borderWidth: 1, borderColor: 'rgba(255,255,255,0.1)',
    borderRadius: 14, padding: 16, color: '#f9fafb', fontSize: 15,
  },
  error: { color: '#ef4444', fontSize: 13, textAlign: 'center' },
  registerBtn: {
    backgroundColor: '#6366f1', borderRadius: 14, paddingVertical: 16,
    alignItems: 'center', marginTop: 8,
  },
  registerBtnText: { color: '#fff', fontWeight: '700', fontSize: 16 },
  link: { color: '#9ca3af', textAlign: 'center', marginTop: 20, fontSize: 14 },
  linkBold: { color: '#818cf8', fontWeight: '700' },
});
