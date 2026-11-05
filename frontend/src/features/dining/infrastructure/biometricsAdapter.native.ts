import { BiometricsPort, BiometricAuthResult } from '../model/biometricsPort';

/**
 * Mobile Native Infrastructure Adapter:
 * Compiled exclusively by Metro when targeting iOS or Android.
 * Communicates with the native OS hardware layers (FaceID/TouchID on iOS, BiometricPrompt on Android).
 */
export class NativeBiometricsAdapter implements BiometricsPort {
  async isHardwareAvailable(): Promise<boolean> {
    try {
      // Dynamic import to decouple build without hard dependency if not installed
      const LocalAuth = require('expo-local-authentication');
      const hasHardware = await LocalAuth.hasHardwareAsync();
      const isEnrolled = await LocalAuth.isEnrolledAsync();
      return hasHardware && isEnrolled;
    } catch {
      return false;
    }
  }

  async authenticate(promptReason: string): Promise<BiometricAuthResult> {
    try {
      const LocalAuth = require('expo-local-authentication');
      const result = await LocalAuth.authenticateAsync({
        promptMessage: promptReason,
        cancelLabel: 'Cancelar',
        disableDeviceFallback: false,
      });

      return {
        success: result.success,
        biometryType: 'fingerprint',
        errorMessage: result.error,
      };
    } catch (err: any) {
      return {
        success: false,
        biometryType: 'none',
        errorMessage: err.message || 'Error de hardware biométrico',
      };
    }
  }
}

export const biometricsAdapter: BiometricsPort = new NativeBiometricsAdapter();
