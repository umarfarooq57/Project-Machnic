/**
 * Profile Screen — User info, edit name/phone, emergency contacts, logout.
 */
import React, { useState } from 'react';
import {
  View, Text, TextInput, TouchableOpacity, StyleSheet, ScrollView, Alert,
} from 'react-native';
import { useAuthStore } from '../../store/authStore';

export default function ProfileScreen({ navigation }) {
  const { user, updateProfile, logout, loading } = useAuthStore();
  const [editing, setEditing] = useState(false);
  const [fullName, setFullName] = useState(user?.full_name || '');
  const [phone, setPhone] = useState(user?.phone || '');

  const handleSave = async () => {
    await updateProfile({ full_name: fullName, phone });
    setEditing(false);
    Alert.alert('Success', 'Profile updated.');
  };

  const handleLogout = () => {
    Alert.alert('Logout', 'Are you sure?', [
      { text: 'Cancel', style: 'cancel' },
      { text: 'Logout', style: 'destructive', onPress: logout },
    ]);
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.title}>Profile</Text>

      {/* Avatar Placeholder */}
      <View style={styles.avatar}>
        <Text style={styles.avatarText}>{(user?.full_name || 'U')[0].toUpperCase()}</Text>
      </View>

      {/* Info Fields */}
      <View style={styles.card}>
        <Text style={styles.label}>Full Name</Text>
        {editing ? (
          <TextInput style={styles.input} value={fullName} onChangeText={setFullName} />
        ) : (
          <Text style={styles.value}>{user?.full_name || '—'}</Text>
        )}

        <Text style={styles.label}>Email</Text>
        <Text style={styles.value}>{user?.email || '—'}</Text>

        <Text style={styles.label}>Phone</Text>
        {editing ? (
          <TextInput style={styles.input} value={phone} onChangeText={setPhone} keyboardType="phone-pad" />
        ) : (
          <Text style={styles.value}>{user?.phone || 'Not set'}</Text>
        )}

        <Text style={styles.label}>Role</Text>
        <Text style={styles.value}>{user?.role || 'user'}</Text>

        <Text style={styles.label}>Verified</Text>
        <Text style={[styles.value, { color: user?.is_verified ? '#10b981' : '#f59e0b' }]}>
          {user?.is_verified ? 'Yes ✓' : 'No'}
        </Text>
      </View>

      {editing ? (
        <View style={styles.editBtns}>
          <TouchableOpacity style={styles.saveBtn} onPress={handleSave} disabled={loading}>
            <Text style={styles.saveBtnText}>{loading ? 'Saving…' : 'Save'}</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.cancelEditBtn} onPress={() => setEditing(false)}>
            <Text style={styles.cancelEditBtnText}>Cancel</Text>
          </TouchableOpacity>
        </View>
      ) : (
        <TouchableOpacity style={styles.editBtn} onPress={() => setEditing(true)}>
          <Text style={styles.editBtnText}>✏️ Edit Profile</Text>
        </TouchableOpacity>
      )}

      <TouchableOpacity style={styles.logoutBtn} onPress={handleLogout}>
        <Text style={styles.logoutBtnText}>Logout</Text>
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0f0f23' },
  content: { padding: 24, paddingBottom: 48, alignItems: 'center' },
  title: { fontSize: 28, fontWeight: '800', color: '#f9fafb', marginBottom: 24, alignSelf: 'flex-start' },
  avatar: {
    width: 80, height: 80, borderRadius: 40, backgroundColor: '#6366f1',
    justifyContent: 'center', alignItems: 'center', marginBottom: 24,
  },
  avatarText: { color: '#fff', fontSize: 32, fontWeight: '800' },
  card: {
    backgroundColor: 'rgba(255,255,255,0.04)', borderRadius: 20,
    padding: 20, width: '100%', marginBottom: 20,
  },
  label: { color: '#6b7280', fontSize: 12, fontWeight: '600', marginTop: 12, marginBottom: 4 },
  value: { color: '#f9fafb', fontSize: 16, fontWeight: '500' },
  input: {
    backgroundColor: 'rgba(255,255,255,0.05)', borderWidth: 1, borderColor: 'rgba(255,255,255,0.1)',
    borderRadius: 10, padding: 10, color: '#f9fafb', fontSize: 15,
  },
  editBtn: {
    backgroundColor: 'rgba(99, 102, 241, 0.15)', borderRadius: 14,
    paddingVertical: 14, paddingHorizontal: 24, width: '100%', alignItems: 'center',
  },
  editBtnText: { color: '#818cf8', fontWeight: '700', fontSize: 15 },
  editBtns: { flexDirection: 'row', gap: 10, width: '100%' },
  saveBtn: {
    flex: 1, backgroundColor: '#10b981', borderRadius: 14,
    paddingVertical: 14, alignItems: 'center',
  },
  saveBtnText: { color: '#fff', fontWeight: '700' },
  cancelEditBtn: {
    flex: 1, backgroundColor: 'rgba(255,255,255,0.05)', borderRadius: 14,
    paddingVertical: 14, alignItems: 'center',
  },
  cancelEditBtnText: { color: '#9ca3af', fontWeight: '600' },
  logoutBtn: {
    marginTop: 20, backgroundColor: 'rgba(239, 68, 68, 0.15)', borderRadius: 14,
    paddingVertical: 14, width: '100%', alignItems: 'center',
  },
  logoutBtnText: { color: '#ef4444', fontWeight: '700', fontSize: 15 },
});
