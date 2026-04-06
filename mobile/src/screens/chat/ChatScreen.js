/**
 * Chat Screen — Simple real-time chat with mechanic via the service request.
 */
import React, { useState, useEffect, useRef } from 'react';
import {
  View, Text, TextInput, TouchableOpacity, StyleSheet,
  FlatList, KeyboardAvoidingView, Platform,
} from 'react-native';
import api from '../../services/api';

export default function ChatScreen({ route }) {
  const requestId = route?.params?.requestId;
  const [messages, setMessages] = useState([]);
  const [text, setText] = useState('');
  const flatListRef = useRef(null);

  useEffect(() => {
    if (requestId) {
      fetchMessages();
      const interval = setInterval(fetchMessages, 3000);
      return () => clearInterval(interval);
    }
  }, [requestId]);

  const fetchMessages = async () => {
    try {
      const res = await api.get(`/chat/${requestId}/messages/`);
      setMessages(res.data.results || res.data);
    } catch { /* silent */ }
  };

  const sendMessage = async () => {
    if (!text.trim()) return;
    try {
      await api.post(`/chat/${requestId}/messages/`, { content: text.trim() });
      setText('');
      fetchMessages();
    } catch { /* silent */ }
  };

  const renderMessage = ({ item }) => {
    const isMe = item.is_sender;
    return (
      <View style={[styles.msgRow, isMe && styles.msgRowMe]}>
        <View style={[styles.bubble, isMe ? styles.bubbleMe : styles.bubbleThem]}>
          <Text style={[styles.msgText, isMe && styles.msgTextMe]}>{item.content}</Text>
          <Text style={styles.msgTime}>
            {new Date(item.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </Text>
        </View>
      </View>
    );
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      keyboardVerticalOffset={90}
    >
      <View style={styles.header}>
        <Text style={styles.headerText}>💬 Chat with Mechanic</Text>
      </View>

      <FlatList
        ref={flatListRef}
        data={messages}
        keyExtractor={(item) => item.id?.toString() || Math.random().toString()}
        renderItem={renderMessage}
        contentContainerStyle={styles.list}
        onContentSizeChange={() => flatListRef.current?.scrollToEnd()}
      />

      <View style={styles.inputBar}>
        <TextInput
          style={styles.input}
          placeholder="Type a message..."
          placeholderTextColor="#6b7280"
          value={text}
          onChangeText={setText}
          onSubmitEditing={sendMessage}
        />
        <TouchableOpacity style={styles.sendBtn} onPress={sendMessage}>
          <Text style={styles.sendBtnText}>➤</Text>
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0f0f23' },
  header: { padding: 16, paddingTop: 50, backgroundColor: 'rgba(26,26,46,0.95)', borderBottomWidth: 1, borderBottomColor: 'rgba(255,255,255,0.05)' },
  headerText: { color: '#f9fafb', fontSize: 18, fontWeight: '700' },
  list: { padding: 16 },
  msgRow: { marginBottom: 8, alignItems: 'flex-start' },
  msgRowMe: { alignItems: 'flex-end' },
  bubble: { maxWidth: '75%', borderRadius: 16, padding: 12 },
  bubbleMe: { backgroundColor: '#6366f1', borderBottomRightRadius: 4 },
  bubbleThem: { backgroundColor: 'rgba(255,255,255,0.08)', borderBottomLeftRadius: 4 },
  msgText: { color: '#d1d5db', fontSize: 14 },
  msgTextMe: { color: '#fff' },
  msgTime: { color: 'rgba(255,255,255,0.4)', fontSize: 10, marginTop: 4, alignSelf: 'flex-end' },
  inputBar: {
    flexDirection: 'row', padding: 12, paddingBottom: 28, gap: 8,
    backgroundColor: 'rgba(26,26,46,0.95)', borderTopWidth: 1, borderTopColor: 'rgba(255,255,255,0.05)',
  },
  input: {
    flex: 1, backgroundColor: 'rgba(255,255,255,0.05)', borderRadius: 20,
    paddingHorizontal: 16, paddingVertical: 10, color: '#f9fafb', fontSize: 14,
  },
  sendBtn: {
    width: 44, height: 44, borderRadius: 22, backgroundColor: '#6366f1',
    justifyContent: 'center', alignItems: 'center',
  },
  sendBtnText: { color: '#fff', fontSize: 18 },
});
