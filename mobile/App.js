import { NavigationContainer } from '@react-navigation/native';
import AuthStack from './src/navigation/AuthStack';
import AppTabs from './src/navigation/AppTabs';
import { useAuthStore } from './src/store/authStore';
import React, { useEffect } from 'react';

export default function App() {
  const { user, autoLogin } = useAuthStore();

  useEffect(() => {
    autoLogin();
  }, []);

  return (
    <NavigationContainer>
      {user ? <AppTabs /> : <AuthStack />}
    </NavigationContainer>
  );
}
