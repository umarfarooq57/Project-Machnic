/**
 * Profile — Wrapper for backward compatibility with AppTabs import.
 */
import React from 'react';
import ProfileScreen from '../profile/ProfileScreen';

export default function Profile(props) {
  return <ProfileScreen {...props} />;
}
