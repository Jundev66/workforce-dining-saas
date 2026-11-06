import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { useIsOnline } from '../offline/offlineManager';
import { colors } from '../theme/colors';

export function OfflineBanner() {
  const isOnline = useIsOnline();

  if (isOnline) {
    return null;
  }

  return (
    <View style={styles.banner} testID="offline-banner">
      <Text style={styles.text}>
        📡 Modo sin conexión: los registros se guardan en el dispositivo y se sincronizarán automáticamente al volver la red.
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  banner: {
    backgroundColor: '#b45309', // Amber-700
    paddingVertical: 6,
    paddingHorizontal: 12,
    alignItems: 'center',
    justifyContent: 'center',
  },
  text: {
    color: '#ffffff',
    fontSize: 12,
    fontWeight: '600',
    textAlign: 'center',
  },
});
