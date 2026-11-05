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
    textTransform: 'uppercase',
  },
});
