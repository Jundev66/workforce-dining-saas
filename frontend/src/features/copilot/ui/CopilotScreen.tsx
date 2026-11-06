import React, { useState, useRef, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TextInput,
  TouchableOpacity,
  ScrollView,
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { colors } from '../../../shared/theme/colors';
import { sendCopilotMessage } from '../api/copilotApi';
import { CopilotResponse } from '../model/copilotSchemas';

interface ChatMessage {
  id: string;
  sender: 'user' | 'assistant';
  text: string;
  time: string;
  responseMeta?: CopilotResponse;
  showAudit?: boolean;
}

export function CopilotScreen() {
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([
    {
      id: 'welcome-1',
      sender: 'assistant',
      text: '¡Hola! Soy tu Copilot de RRHH y Comedor Industrial. Puedo registrar tus avisos de ausencia, verificar convenios laborales y coordinar la cancelación de viandas para evitar desperdicio de alimentos. ¿En qué te puedo ayudar?',
      time: 'Ahora',
    },
  ]);

  const scrollViewRef = useRef<any>(null);

  useEffect(() => {
    scrollViewRef.current?.scrollToEnd({ animated: true });
  }, [chatHistory, loading]);

  const handleSend = async (textOverride?: string) => {
    const textToSend = textOverride || message;
    if (!textToSend.trim() || loading) return;

    const userMsgId = `user-${Date.now()}`;
    const userMsg: ChatMessage = {
      id: userMsgId,
      sender: 'user',
      text: textToSend.trim(),
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setChatHistory((prev) => [...prev, userMsg]);
    if (!textOverride) setMessage('');
    setLoading(true);

    try {
      const res = await sendCopilotMessage({
        message: textToSend.trim(),
        employee_id: 'emp-active-session',
      });

      const assistantMsg: ChatMessage = {
        id: `bot-${Date.now()}`,
        sender: 'assistant',
        text: res.message,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        responseMeta: res,
        showAudit: false,
      };

      setChatHistory((prev) => [...prev, assistantMsg]);
    } catch (err: any) {
      const errorMsg: ChatMessage = {
        id: `err-${Date.now()}`,
        sender: 'assistant',
        text: `⚠️ ${err?.message || 'Error al conectar con los agentes'}`,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setChatHistory((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  const toggleAudit = (msgId: string) => {
    setChatHistory((prev) =>
      prev.map((msg) =>
        msg.id === msgId ? { ...msg, showAudit: !msg.showAudit } : msg
      )
    );
  };

  const quickChips = [
    { label: '🩺 Médico + Cancelar Menú', prompt: 'El viernes falto por consulta médica y por favor cancelar mi vianda de almuerzo' },
    { label: '📅 Permiso Personal', prompt: 'El lunes falto a mi turno por trámites personales' },
    { label: '❓ Consulta Políticas', prompt: '¿Cómo funciona la política de licencias y comedor de la empresa?' },
  ];

  return (
    <KeyboardAvoidingView
      style={styles.keyboardContainer}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      keyboardVerticalOffset={Platform.OS === 'ios' ? 90 : 0}
    >
      <View style={styles.container}>
        {/* Chat Messages */}
        <ScrollView
          ref={scrollViewRef}
          style={styles.messagesScroll}
          contentContainerStyle={styles.messagesContent}
          showsVerticalScrollIndicator={false}
          keyboardShouldPersistTaps="handled"
        >
          {chatHistory.map((item) => (
            <View
              key={item.id}
              style={[
                styles.messageRow,
                item.sender === 'user' ? styles.messageRowUser : styles.messageRowAssistant,
              ]}
            >
              {item.sender === 'assistant' && (
                <View style={styles.avatar}>
                  <Text style={styles.avatarIcon}>🤖</Text>
                </View>
              )}

              <View
                style={[
                  styles.bubble,
                  item.sender === 'user' ? styles.bubbleUser : styles.bubbleAssistant,
                ]}
              >
                <Text
                  style={[
                    styles.messageText,
                    item.sender === 'user' ? styles.messageTextUser : styles.messageTextAssistant,
                  ]}
                >
                  {item.text}
                </Text>

                {/* Status Badges for Agent Responses */}
                {item.responseMeta && (
                  <View style={styles.badgeContainer}>
                    <View style={[styles.pill, styles.pillSuccess]}>
                      <Text style={styles.pillTextSuccess}>🛡️ Guardrail OK</Text>
                    </View>
                    <View
                      style={[
                        styles.pill,
                        item.responseMeta.policy_approved ? styles.pillSuccess : styles.pillWarning,
                      ]}
                    >
                      <Text
                        style={
                          item.responseMeta.policy_approved
                            ? styles.pillTextSuccess
                            : styles.pillTextWarning
                        }
                      >
                        {item.responseMeta.policy_approved ? '📋 RRHH Aprobado' : '📋 RRHH Pendiente'}
                      </Text>
                    </View>
                    {item.responseMeta.meal_cancelled && (
                      <View style={[styles.pill, styles.pillPrimary]}>
                        <Text style={styles.pillTextPrimary}>🍽️ Vianda Cancelada</Text>
                      </View>
                    )}
                  </View>
                )}

                {/* Collapsible Multi-Agent Audit Trail */}
                {item.responseMeta && (
                  <View style={styles.auditWrapper}>
                    <TouchableOpacity
                      style={styles.auditToggleBtn}
                      onPress={() => toggleAudit(item.id)}
                      activeOpacity={0.7}
                    >
                      <Text style={styles.auditToggleText}>
                        {item.showAudit ? '▲ Ocultar' : '▼ Auditoría Multi-Agente'} (
                        {item.responseMeta.audit_trail.length} pasos)
                      </Text>
                    </TouchableOpacity>

                    {item.showAudit && (
                      <View style={styles.auditBox}>
                        {item.responseMeta.audit_trail.map((step, idx) => (
                          <View key={idx} style={styles.auditItem}>
                            <Text style={styles.auditDot}>•</Text>
                            <Text style={styles.auditLogText}>{step}</Text>
                          </View>
                        ))}
                      </View>
                    )}
                  </View>
                )}

                <Text
                  style={[
                    styles.timeText,
                    item.sender === 'user' ? styles.timeTextUser : styles.timeTextAssistant,
                  ]}
                >
                  {item.time}
                </Text>
              </View>
            </View>
          ))}

          {loading && (
            <View style={styles.loadingRow}>
              <View style={styles.avatar}>
                <Text style={styles.avatarIcon}>🤖</Text>
              </View>
              <View style={styles.loadingBubble}>
                <ActivityIndicator size="small" color={colors.primary} />
                <Text style={styles.loadingText}>Coordinando agentes en LangGraph...</Text>
              </View>
            </View>
          )}
        </ScrollView>

        {/* Quick Suggestion Chips */}
        <View style={styles.chipsSection}>
          <ScrollView
            horizontal
            showsHorizontalScrollIndicator={false}
            contentContainerStyle={styles.chipsContent}
          >
            {quickChips.map((chip, idx) => (
              <TouchableOpacity
                key={idx}
                style={styles.chipBtn}
                onPress={() => handleSend(chip.prompt)}
                disabled={loading}
              >
                <Text style={styles.chipText}>{chip.label}</Text>
              </TouchableOpacity>
            ))}
          </ScrollView>
        </View>

        {/* Input Bar */}
        <View style={styles.inputSection}>
          <View style={styles.inputCapsule}>
            <TextInput
              style={styles.textInput}
              placeholder="Escribí tu consulta o aviso de ausencia..."
              placeholderTextColor={colors.textMuted}
              value={message}
              onChangeText={setMessage}
              multiline
              maxLength={500}
              editable={!loading}
            />
            <TouchableOpacity
              style={[
                styles.sendBtn,
                (!message.trim() || loading) && styles.sendBtnDisabled,
              ]}
              onPress={() => handleSend()}
              disabled={!message.trim() || loading}
            >
              <Text style={styles.sendBtnIcon}>➔</Text>
            </TouchableOpacity>
          </View>
        </View>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  keyboardContainer: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  container: {
    flex: 1,
    width: '100%',
    maxWidth: 720,
    alignSelf: 'center',
    backgroundColor: '#f8fafc',
  },
  messagesScroll: {
    flex: 1,
  },
  messagesContent: {
    paddingHorizontal: 16,
    paddingTop: 16,
    paddingBottom: 16,
  },
  messageRow: {
    flexDirection: 'row',
    marginBottom: 16,
    alignItems: 'flex-end',
  },
  messageRowUser: {
    justifyContent: 'flex-end',
  },
  messageRowAssistant: {
    justifyContent: 'flex-start',
  },
  avatar: {
    width: 34,
    height: 34,
    borderRadius: 17,
    backgroundColor: '#e0e7ff',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 8,
    marginBottom: 2,
    borderWidth: 1,
    borderColor: '#c7d2fe',
  },
  avatarIcon: {
    fontSize: 18,
  },
  bubble: {
    maxWidth: '82%',
    borderRadius: 18,
    paddingHorizontal: 14,
    paddingVertical: 10,
    shadowColor: '#000',
    shadowOpacity: 0.04,
    shadowRadius: 5,
    shadowOffset: { width: 0, height: 2 },
    elevation: 1,
  },
  bubbleUser: {
    backgroundColor: colors.primary,
    borderBottomRightRadius: 4,
  },
  bubbleAssistant: {
    backgroundColor: '#ffffff',
    borderBottomLeftRadius: 4,
    borderWidth: 1,
    borderColor: '#e2e8f0',
  },
  messageText: {
    fontSize: 14,
    lineHeight: 20,
  },
  messageTextUser: {
    color: '#ffffff',
    fontWeight: '500',
  },
  messageTextAssistant: {
    color: '#1e293b',
  },
  timeText: {
    fontSize: 10,
    marginTop: 4,
    alignSelf: 'flex-end',
  },
  timeTextUser: {
    color: 'rgba(255, 255, 255, 0.7)',
  },
  timeTextAssistant: {
    color: '#94a3b8',
  },
  badgeContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 6,
    marginTop: 10,
    marginBottom: 4,
  },
  pill: {
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 12,
  },
  pillSuccess: {
    backgroundColor: '#ecfdf5',
    borderWidth: 1,
    borderColor: '#a7f3d0',
  },
  pillTextSuccess: {
    color: '#059669',
    fontSize: 11,
    fontWeight: '600',
  },
  pillWarning: {
    backgroundColor: '#fffbeb',
    borderWidth: 1,
    borderColor: '#fde68a',
  },
  pillTextWarning: {
    color: '#d97706',
    fontSize: 11,
    fontWeight: '600',
  },
  pillPrimary: {
    backgroundColor: '#eff6ff',
    borderWidth: 1,
    borderColor: '#bfdbfe',
  },
  pillTextPrimary: {
    color: '#2563eb',
    fontSize: 11,
    fontWeight: '600',
  },
  auditWrapper: {
    marginTop: 8,
    borderTopWidth: 1,
    borderTopColor: '#f1f5f9',
    paddingTop: 6,
  },
  auditToggleBtn: {
    paddingVertical: 4,
  },
  auditToggleText: {
    fontSize: 11,
    color: colors.primary,
    fontWeight: '600',
  },
  auditBox: {
    backgroundColor: '#f8fafc',
    borderRadius: 8,
    padding: 8,
    marginTop: 6,
    borderWidth: 1,
    borderColor: '#e2e8f0',
  },
  auditItem: {
    flexDirection: 'row',
    marginBottom: 4,
  },
  auditDot: {
    fontSize: 11,
    color: colors.primary,
    marginRight: 4,
  },
  auditLogText: {
    fontSize: 10,
    color: '#475569',
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    flex: 1,
  },
  loadingRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  loadingBubble: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#ffffff',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    gap: 8,
  },
  loadingText: {
    fontSize: 12,
    color: colors.textMuted,
  },
  chipsSection: {
    paddingVertical: 6,
    backgroundColor: '#ffffff',
    borderTopWidth: 1,
    borderTopColor: '#f1f5f9',
  },
  chipsContent: {
    paddingHorizontal: 12,
    paddingRight: 24,
    gap: 8,
  },
  chipBtn: {
    backgroundColor: '#f1f5f9',
    paddingHorizontal: 12,
    paddingVertical: 7,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: '#e2e8f0',
  },
  chipText: {
    fontSize: 12,
    color: '#334155',
    fontWeight: '500',
  },
  inputSection: {
    backgroundColor: '#ffffff',
    paddingHorizontal: 12,
    paddingTop: 6,
    paddingBottom: Platform.OS === 'ios' ? 24 : 10,
    borderTopWidth: 1,
    borderTopColor: '#e2e8f0',
  },
  inputCapsule: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#f8fafc',
    borderRadius: 24,
    borderWidth: 1,
    borderColor: '#cbd5e1',
    paddingLeft: 14,
    paddingRight: 6,
    paddingVertical: 4,
    minHeight: 44,
  },
  textInput: {
    flex: 1,
    fontSize: 14,
    color: '#0f172a',
    maxHeight: 100,
    paddingVertical: 6,
  },
  sendBtn: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: colors.primary,
    alignItems: 'center',
    justifyContent: 'center',
    marginLeft: 6,
  },
  sendBtnDisabled: {
    backgroundColor: '#cbd5e1',
  },
  sendBtnIcon: {
    color: '#ffffff',
    fontSize: 14,
    fontWeight: '700',
    marginLeft: 1,
  },
});
