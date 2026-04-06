/**
 * Login Screen — Premium dark-themed login.
 */
import React, { useState } from 'react';
import {
    View, Text, TextInput, TouchableOpacity, StyleSheet, ActivityIndicator,
} from 'react-native';
import { useAuthStore } from '../../store/authStore';

export default function Login({ navigation }) {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const { login, loading, error } = useAuthStore();

    const handleLogin = async () => {
        if (!email.trim() || !password) return;
        await login(email.trim(), password);
    };

    return (
        <View style={styles.container}>
            <View style={styles.header}>
                <Text style={styles.logo}>🔧</Text>
                <Text style={styles.title}>RoadAid</Text>
                <Text style={styles.subtitle}>Sign in to your account</Text>
            </View>

            <View style={styles.form}>
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

                {error ? <Text style={styles.error}>{error}</Text> : null}

                <TouchableOpacity style={styles.loginBtn} onPress={handleLogin} disabled={loading}>
                    {loading ? (
                        <ActivityIndicator color="#fff" />
                    ) : (
                        <Text style={styles.loginBtnText}>Sign In</Text>
                    )}
                </TouchableOpacity>

                <TouchableOpacity onPress={() => navigation.navigate('Register')}>
                    <Text style={styles.link}>
                        Don't have an account? <Text style={styles.linkBold}>Sign Up</Text>
                    </Text>
                </TouchableOpacity>
            </View>
        </View>
    );
}

const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: '#0f0f23', justifyContent: 'center', padding: 32 },
    header: { alignItems: 'center', marginBottom: 40 },
    logo: { fontSize: 48, marginBottom: 8 },
    title: { fontSize: 32, fontWeight: '800', color: '#f9fafb' },
    subtitle: { color: '#9ca3af', fontSize: 15, marginTop: 6 },
    form: { gap: 14 },
    input: {
        backgroundColor: 'rgba(255,255,255,0.05)', borderWidth: 1, borderColor: 'rgba(255,255,255,0.1)',
        borderRadius: 14, padding: 16, color: '#f9fafb', fontSize: 15,
    },
    error: { color: '#ef4444', fontSize: 13, textAlign: 'center' },
    loginBtn: {
        backgroundColor: '#6366f1', borderRadius: 14, paddingVertical: 16,
        alignItems: 'center', marginTop: 8,
    },
    loginBtnText: { color: '#fff', fontWeight: '700', fontSize: 16 },
    link: { color: '#9ca3af', textAlign: 'center', marginTop: 20, fontSize: 14 },
    linkBold: { color: '#818cf8', fontWeight: '700' },
});
