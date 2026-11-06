import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { colors } from '../theme/colors';

interface BadgeProps {
  status: string;
}

export const Badge: React.FC<BadgeProps> = ({ status }) => {
  const normalized = status.toLowerCase();

  const getStyle = () => {
    switch (normalized) {
      case 'active':
        return {
          bg: colors.successLight,
          text: colors.success,
          label: 'Activo',
        };
      case 'on_leave':
        return {
          bg: colors.warningLight,
          text: colors.warning,
          label: 'Licencia',
        };
      case 'pending':
        return {
          bg: '#fef3c7', // amber-100
          text: '#b45309', // amber-700
          label: 'Pendiente Sync',
        };
      case 'failed_retryable':
        return {
          bg: '#ffedd5', // orange-100
          text: '#c2410c', // orange-700
          label: 'Reintentando...',
        };
      case 'conflict':
      case 'conflict_action_required':
        return {
          bg: '#fee2e2', // red-100
          text: '#b91c1c', // red-700
          label: 'Conflicto (Requiere Acción)',
        };
      case 'blocked_by_dependency':
        return {
          bg: '#f3e8ff', // purple-100
          text: '#7e22ce', // purple-700
          label: 'Bloqueado por Padre',
        };
      case 'synced':
        return {
          bg: colors.successLight,
          text: colors.success,
          label: 'Sincronizado',
        };
      case 'inactive':
      default:
        return {
          bg: colors.dangerLight,
          text: colors.danger,
          label: 'Inactivo',
        };
    }
  };

  const current = getStyle();

  return (
    <View style={[styles.badge, { backgroundColor: current.bg }]}>
      <Text style={[styles.badgeText, { color: current.text }]}>
        {current.label}
      </Text>
    </View>
  );
};

const styles = StyleSheet.create({
  badge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
    alignSelf: 'flex-start',
  },
  badgeText: {
    fontSize: 12,
    fontWeight: '600',
  },
});
