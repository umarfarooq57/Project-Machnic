/**
 * App Tabs — Simple wrapper that delegates to AppNavigator.
 * Kept for backward compatibility with App.js import.
 */
import React from 'react';
import AppNavigator from './AppNavigator';

export default function AppTabs() {
  return <AppNavigator />;
}
