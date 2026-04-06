/**
 * Notification Screen — Real notifications from API.
 */
import React, { useEffect } from 'react';
import {
  View, Text, TouchableOpacity, StyleSheet, FlatList, ActivityIndicator,
} from 'react-native';
import { useNotificationStore } from '../../store/notificationStore';

export default function NotificationScreen() {
  const { notifications, unreadCount, loading, fetchNotifications, markAsRead, markAllRead } =
    useNotificationStore();

  useEffect(() => {
    fetchNotifications();
  }, []);

  const renderItem = ({ item }) => (
    <TouchableOpacity
      style={[styles.card, !item.is_read && styles.cardUnread]}
      onPress={() => markAsRead(item.id)}
    >
      <View style={styles.cardHeader}>
        <Text style={styles.cardTitle}>{item.title}</Text>
        {!item.is_read && <View style={styles.dot} />}
      </View>
      <Text style={styles.cardBody}>{item.body}</Text>
      <Text style={styles.cardTime}>
        {new Date(item.created_at).toLocaleDateString()} • {new Date(item.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
      </Text>
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Notifications</Text>
        {unreadCount > 0 && (
          <TouchableOpacity onPress={markAllRead}>
            <Text style={styles.markAll}>Mark all read</Text>
          </TouchableOpacity>
        )}
      </View>

      {loading ? (
        <ActivityIndicator size="large" color="#6366f1" style={{ marginTop: 40 }} />
      ) : notifications.length === 0 ? (
        <View style={styles.empty}>
          <Text style={styles.emptyText}>🔔 No notifications yet</Text>
        </View>
      ) : (
        <FlatList
          data={notifications}
          keyExtractor={(item) => item.id?.toString()}
          renderItem={renderItem}
          contentContainerStyle={{ paddingBottom: 40 }}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0f0f23', padding: 16 },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16, paddingTop: 8 },
  title: { fontSize: 24, fontWeight: '800', color: '#f9fafb' },
  markAll: { color: '#818cf8', fontWeight: '600', fontSize: 13 },
  card: {
    backgroundColor: 'rgba(255,255,255,0.03)', borderRadius: 14,
    padding: 16, marginBottom: 10,
  },
  cardUnread: { backgroundColor: 'rgba(99, 102, 241, 0.08)', borderLeftWidth: 3, borderLeftColor: '#6366f1' },
  cardHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  cardTitle: { color: '#f9fafb', fontWeight: '700', fontSize: 15, flex: 1 },
  dot: { width: 8, height: 8, borderRadius: 4, backgroundColor: '#6366f1' },
  cardBody: { color: '#9ca3af', fontSize: 13, marginTop: 6 },
  cardTime: { color: '#4b5563', fontSize: 11, marginTop: 8 },
  empty: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  emptyText: { color: '#6b7280', fontSize: 16 },
});
