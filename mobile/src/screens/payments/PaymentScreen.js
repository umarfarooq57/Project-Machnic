/**
 * Payment Screen — Wallet balance, pay for service, promo code.
 */
import React, { useState, useEffect } from 'react';
import {
  View, Text, TextInput, TouchableOpacity, StyleSheet, Alert, ScrollView,
} from 'react-native';
import api from '../../services/api';

export default function PaymentScreen({ navigation }) {
  const [wallet, setWallet] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [topUpAmount, setTopUpAmount] = useState('');

  useEffect(() => {
    fetchWallet();
    fetchTransactions();
  }, []);

  const fetchWallet = async () => {
    try {
      const res = await api.get('/payments/wallet/');
      setWallet(res.data);
    } catch { /* silent */ }
  };

  const fetchTransactions = async () => {
    try {
      const res = await api.get('/payments/history/');
      setTransactions(res.data.results || res.data);
    } catch { /* silent */ }
  };

  const handleTopUp = async () => {
    const amt = parseFloat(topUpAmount);
    if (!amt || amt <= 0) return Alert.alert('Error', 'Enter a valid amount');
    try {
      await api.post('/payments/wallet/top-up/', { amount: amt });
      Alert.alert('Success', `$${amt} added to wallet`);
      setTopUpAmount('');
      fetchWallet();
    } catch (e) {
      Alert.alert('Error', e.response?.data?.detail || 'Top-up failed');
    }
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.title}>Payments</Text>

      {/* Wallet Card */}
      <View style={styles.walletCard}>
        <Text style={styles.walletLabel}>Wallet Balance</Text>
        <Text style={styles.walletAmount}>
          ${wallet?.balance ? parseFloat(wallet.balance).toFixed(2) : '0.00'}
        </Text>
      </View>

      {/* Top Up */}
      <Text style={styles.label}>Top Up Wallet</Text>
      <View style={styles.topUpRow}>
        <TextInput
          style={[styles.input, { flex: 1 }]}
          placeholder="Amount"
          placeholderTextColor="#6b7280"
          keyboardType="decimal-pad"
          value={topUpAmount}
          onChangeText={setTopUpAmount}
        />
        <TouchableOpacity style={styles.topUpBtn} onPress={handleTopUp}>
          <Text style={styles.topUpBtnText}>Top Up</Text>
        </TouchableOpacity>
      </View>

      {/* Transaction History */}
      <Text style={[styles.label, { marginTop: 24 }]}>Recent Transactions</Text>
      {transactions.length === 0 ? (
        <Text style={styles.empty}>No transactions yet.</Text>
      ) : (
        transactions.slice(0, 20).map((txn, i) => (
          <View key={txn.id || i} style={styles.txnRow}>
            <View style={{ flex: 1 }}>
              <Text style={styles.txnType}>{txn.transaction_type || 'payment'}</Text>
              <Text style={styles.txnDate}>
                {new Date(txn.created_at).toLocaleDateString()}
              </Text>
            </View>
            <Text style={[styles.txnAmount, txn.transaction_type === 'refund' && { color: '#10b981' }]}>
              {txn.transaction_type === 'refund' ? '+' : '-'}${parseFloat(txn.amount || 0).toFixed(2)}
            </Text>
          </View>
        ))
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0f0f23' },
  content: { padding: 24, paddingBottom: 48 },
  title: { fontSize: 28, fontWeight: '800', color: '#f9fafb', marginBottom: 24 },
  walletCard: {
    backgroundColor: '#6366f1', borderRadius: 20, padding: 28,
    marginBottom: 24, alignItems: 'center',
  },
  walletLabel: { color: 'rgba(255,255,255,0.7)', fontSize: 14, fontWeight: '600' },
  walletAmount: { color: '#fff', fontSize: 42, fontWeight: '800', marginTop: 4 },
  label: { color: '#9ca3af', fontSize: 14, fontWeight: '600', marginBottom: 10 },
  input: {
    backgroundColor: 'rgba(255,255,255,0.05)', borderWidth: 1, borderColor: 'rgba(255,255,255,0.1)',
    borderRadius: 12, padding: 14, color: '#f9fafb', fontSize: 15,
  },
  topUpRow: { flexDirection: 'row', gap: 10 },
  topUpBtn: {
    backgroundColor: '#10b981', paddingHorizontal: 24, borderRadius: 12,
    justifyContent: 'center',
  },
  topUpBtnText: { color: '#fff', fontWeight: '700' },
  empty: { color: '#6b7280', fontStyle: 'italic', marginTop: 8 },
  txnRow: {
    flexDirection: 'row', alignItems: 'center',
    backgroundColor: 'rgba(255,255,255,0.03)', borderRadius: 12,
    padding: 14, marginBottom: 8,
  },
  txnType: { color: '#f9fafb', fontWeight: '600', textTransform: 'capitalize' },
  txnDate: { color: '#6b7280', fontSize: 12, marginTop: 2 },
  txnAmount: { color: '#ef4444', fontSize: 16, fontWeight: '700' },
});
