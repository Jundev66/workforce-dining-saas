import React, { useState } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
  ActivityIndicator,
} from 'react-native';
import {
  useDiningMetricsQuery,
  useAiForecastQuery,
  useScanMealMutation,
} from '../api/diningApi';
import { useDiningWebSocket } from '../api/useDiningWebSocket';
import { MealScanResult } from '../model/diningTypes';
import { Input } from '../../../shared/components/Input';
import { Button } from '../../../shared/components/Button';
import { colors } from '../../../shared/theme/colors';

export const DiningDashboard: React.FC = () => {
  const [badgeCode, setBadgeCode] = useState('');
  const [mealType, setMealType] = useState<'lunch' | 'breakfast' | 'dinner'>('lunch');
  const [lastResult, setLastResult] = useState<MealScanResult | null>(null);

  const { data: metrics, isLoading: isMetricsLoading } = useDiningMetricsQuery();
  const { data: forecast, isLoading: isForecastLoading } = useAiForecastQuery();
  const scanMutation = useScanMealMutation();
  const { isConnected: isWsConnected, lastLiveScan, clearLastLiveScan } = useDiningWebSocket();

  const handleScan = async () => {
    if (!badgeCode.trim()) return;
    try {
      const result = await scanMutation.mutateAsync({
        badgeCode: badgeCode.trim(),
        mealType,
      });
      setLastResult(result);
      setBadgeCode('');
    } catch (err: any) {
      setLastResult({
        id: 'error',
        status: 'error',
        approved: false,
        employee_id: '',
        employee_name: 'Desconocido',
        department: '',
        meal_type: mealType,
        badge_code: badgeCode,
        message: err.message || 'Error al procesar el escaneo',
        consumed_at: new Date().toISOString(),
      });
    }
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {/* 1. QR Scan Terminal Card */}
      <View style={styles.card} testID="terminal-scan-card">
        <View style={styles.cardHeaderRow}>
          <Text style={styles.cardTitle}>Terminal de Escaneo - Comedor</Text>
          <View
            style={[
              styles.wsStatusBadge,
              isWsConnected ? styles.wsStatusOnline : styles.wsStatusOffline,
            ]}
            testID="ws-status-indicator"
          >
            <View
              style={[
                styles.wsStatusDot,
                { backgroundColor: isWsConnected ? colors.success : colors.textMuted },
              ]}
            />
            <Text
              style={[
                styles.wsStatusText,
                { color: isWsConnected ? colors.success : colors.textMuted },
              ]}
            >
              {isWsConnected ? 'En Vivo' : 'Desconectado'}
            </Text>
          </View>
        </View>

        <Text style={styles.cardSubtitle}>
          Ingresá o escaneá el código de credencial / QR del personal
        </Text>

        {/* Real-time broadcast incoming alert */}
        {lastLiveScan ? (
          <TouchableOpacity
            style={styles.realtimeAlertBanner}
            onPress={clearLastLiveScan}
            activeOpacity={0.8}
            testID="realtime-meal-toast"
          >
            <Text style={styles.realtimeAlertText}>
              🔔 Escaneo en tiempo real: Credencial {lastLiveScan.badge_code} ({lastLiveScan.meal_type})
            </Text>
            <Text style={styles.realtimeAlertDismiss}>✕</Text>
          </TouchableOpacity>
        ) : null}

        <View style={styles.mealTypeSelector}>
          {(['breakfast', 'lunch', 'dinner'] as const).map((type) => (
            <TouchableOpacity
              key={type}
              style={[
                styles.mealTypeBtn,
                mealType === type && styles.mealTypeBtnActive,
              ]}
              onPress={() => setMealType(type)}
            >
              <Text
                style={[
                  styles.mealTypeText,
                  mealType === type && styles.mealTypeTextActive,
                ]}
              >
                {type === 'breakfast' ? 'Desayuno' : type === 'lunch' ? 'Almuerzo' : 'Cena'}
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        <Input
          testID="input-scan-badge"
          label="Código de Credencial / QR"
          placeholder="Ej: QR-001, SEC-990, GOAT-10"
          value={badgeCode}
          onChangeText={setBadgeCode}
          autoCapitalize="characters"
        />

        <Button
          testID="btn-scan-meal"
          title="Verificar y Registrar Ración"
          onPress={handleScan}
          isLoading={scanMutation.isPending}
          disabled={!badgeCode.trim() || scanMutation.isPending}
          style={styles.scanBtn}
        />

        {/* Live Feedback Banner */}
        {lastResult ? (
          <View
            style={[
              styles.feedbackBanner,
              lastResult.approved ? styles.approvedBanner : styles.deniedBanner,
            ]}
            testID="scan-result-banner"
          >
            <Text
              style={[
                styles.feedbackTitle,
                { color: lastResult.approved ? colors.success : colors.danger },
              ]}
            >
              {lastResult.approved ? '✓ RACIÓN AUTORIZADA' : '✕ ACCESO DENEGADO'}
            </Text>
            <Text style={styles.feedbackMsg}>{lastResult.message}</Text>
            {lastResult.employee_name && lastResult.employee_name !== 'Desconocido' ? (
              <Text style={styles.feedbackDetails}>
                Personal: {lastResult.employee_name} ({lastResult.department})
              </Text>
            ) : null}
          </View>
        ) : null}
      </View>

      {/* 2. Real-time Metrics Grid */}
      <View style={styles.metricsGrid}>
        <View style={styles.metricCard}>
          <Text style={styles.metricVal}>
            {isMetricsLoading ? '-' : metrics?.total_meals_today || 0}
          </Text>
          <Text style={styles.metricLabel}>Total Servidas Hoy</Text>
        </View>

        <View style={styles.metricCard}>
          <Text style={[styles.metricVal, { color: colors.primary }]}>
            {isMetricsLoading ? '-' : metrics?.lunch_count || 0}
          </Text>
          <Text style={styles.metricLabel}>Almuerzos</Text>
        </View>

        <View style={styles.metricCard}>
          <Text style={[styles.metricVal, { color: colors.warning }]}>
            {isMetricsLoading ? '-' : metrics?.breakfast_count || 0}
          </Text>
          <Text style={styles.metricLabel}>Desayunos</Text>
        </View>

        <View style={styles.metricCard}>
          <Text style={[styles.metricVal, { color: colors.danger }]}>
            {isMetricsLoading ? '-' : metrics?.rejected_count || 0}
          </Text>
          <Text style={styles.metricLabel}>Rechazos / Duplicados</Text>
        </View>
      </View>

      {/* 3. AI Demand Forecasting Card */}
      <View style={styles.card} testID="ai-forecast-card">
        <View style={styles.aiHeader}>
          <View>
            <Text style={styles.cardTitle}>Pronóstico de Demanda con IA</Text>
            <Text style={styles.cardSubtitle}>
              Optimización de porciones y reducción de mermas
            </Text>
          </View>
          <View style={styles.aiBadge}>
            <Text style={styles.aiBadgeText}>IA Activa</Text>
          </View>
        </View>

        {isForecastLoading ? (
          <ActivityIndicator size="small" color={colors.primary} style={{ marginVertical: 16 }} />
        ) : forecast ? (
          <View style={styles.aiBody}>
            <View style={styles.aiStatRow}>
              <View style={styles.aiStat}>
                <Text style={styles.aiStatNum}>{forecast.forecasted_lunch_headcount}</Text>
                <Text style={styles.aiStatDesc}>Comensales Proyectados</Text>
              </View>

              <View style={styles.aiStat}>
                <Text style={styles.aiStatNum}>{forecast.recommended_food_prep_kg} kg</Text>
                <Text style={styles.aiStatDesc}>Preparación Sugerida</Text>
              </View>

              <View style={styles.aiStat}>
                <Text style={[styles.aiStatNum, { color: colors.success }]}>
                  {Math.round(forecast.confidence_score * 100)}%
                </Text>
                <Text style={styles.aiStatDesc}>Confianza del Modelo</Text>
              </View>
            </View>

            <View style={styles.insightsBox}>
              <Text style={styles.insightsTitle}>Recomendaciones Inteligentes:</Text>
              {forecast.insights.map((insight, idx) => (
                <Text key={idx} style={styles.insightItem}>
                  • {insight}
                </Text>
              ))}
            </View>
          </View>
        ) : null}
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  content: {
    padding: 16,
    paddingBottom: 40,
  },
  card: {
    backgroundColor: colors.surface,
    padding: 20,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: colors.border,
    marginBottom: 16,
  },
  cardHeaderRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 4,
  },
  wsStatusBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
    gap: 5,
  },
  wsStatusOnline: {
    backgroundColor: 'rgba(16, 185, 129, 0.1)',
  },
  wsStatusOffline: {
    backgroundColor: colors.surfaceSubtle,
  },
  wsStatusDot: {
    width: 7,
    height: 7,
    borderRadius: 4,
  },
  wsStatusText: {
    fontSize: 11,
    fontWeight: '600',
  },
  realtimeAlertBanner: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: 'rgba(59, 130, 246, 0.1)',
    borderLeftWidth: 4,
    borderLeftColor: colors.primary,
    padding: 10,
    borderRadius: 6,
    marginBottom: 12,
  },
  realtimeAlertText: {
    fontSize: 12,
    fontWeight: '600',
    color: colors.primary,
    flex: 1,
  },
  realtimeAlertDismiss: {
    fontSize: 14,
    color: colors.textMuted,
    paddingLeft: 8,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: colors.text,
  },
  cardSubtitle: {
    fontSize: 13,
    color: colors.textMuted,
    marginTop: 2,
    marginBottom: 14,
  },
  mealTypeSelector: {
    flexDirection: 'row',
    gap: 8,
    marginBottom: 16,
  },
  mealTypeBtn: {
    flex: 1,
    paddingVertical: 8,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: colors.border,
    alignItems: 'center',
    backgroundColor: colors.surfaceSubtle,
  },
  mealTypeBtnActive: {
    backgroundColor: colors.primary,
    borderColor: colors.primary,
  },
  mealTypeText: {
    fontSize: 13,
    fontWeight: '600',
    color: colors.text,
  },
  mealTypeTextActive: {
    color: colors.textInverse,
  },
  scanBtn: {
    marginTop: 6,
  },
  feedbackBanner: {
    padding: 14,
    borderRadius: 8,
    marginTop: 14,
    borderWidth: 1,
  },
  approvedBanner: {
    backgroundColor: colors.successLight,
    borderColor: colors.success,
  },
  deniedBanner: {
    backgroundColor: colors.dangerLight,
    borderColor: colors.danger,
  },
  feedbackTitle: {
    fontSize: 14,
    fontWeight: '700',
    marginBottom: 4,
  },
  feedbackMsg: {
    fontSize: 13,
    color: colors.text,
  },
  feedbackDetails: {
    fontSize: 12,
    color: colors.textMuted,
    marginTop: 4,
    fontWeight: '500',
  },
  metricsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
    marginBottom: 16,
  },
  metricCard: {
    flex: 1,
    minWidth: 140,
    backgroundColor: colors.surface,
    padding: 14,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: colors.border,
    alignItems: 'center',
  },
  metricVal: {
    fontSize: 24,
    fontWeight: '800',
    color: colors.text,
  },
  metricLabel: {
    fontSize: 12,
    color: colors.textMuted,
    marginTop: 2,
    textAlign: 'center',
  },
  aiHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
  },
  aiBadge: {
    backgroundColor: colors.primaryLight,
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
  },
  aiBadgeText: {
    color: colors.primary,
    fontSize: 11,
    fontWeight: '700',
    textTransform: 'uppercase',
  },
  aiBody: {
    marginTop: 10,
  },
  aiStatRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 16,
    paddingVertical: 10,
    borderTopWidth: 1,
    borderBottomWidth: 1,
    borderColor: colors.border,
  },
  aiStat: {
    alignItems: 'center',
    flex: 1,
  },
  aiStatNum: {
    fontSize: 20,
    fontWeight: '700',
    color: colors.text,
  },
  aiStatDesc: {
    fontSize: 11,
    color: colors.textMuted,
    marginTop: 2,
    textAlign: 'center',
  },
  insightsBox: {
    backgroundColor: colors.surfaceSubtle,
    padding: 12,
    borderRadius: 8,
  },
  insightsTitle: {
    fontSize: 12,
    fontWeight: '700',
    color: colors.text,
    marginBottom: 6,
  },
  insightItem: {
    fontSize: 12,
    color: colors.text,
    lineHeight: 18,
  },
});
