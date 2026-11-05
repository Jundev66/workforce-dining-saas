/**
 * Domain Port: Biometrics & Hardware Abstraction
 * Follows Hexagonal Architecture: the domain/application layer only depends
 * on this contract, never on specific hardware drivers or vendor SDKs.
 */
export type BiometryType = 'fingerprint' | 'facial' | 'iris' | 'hardware_token' | 'none';

export interface BiometricAuthResult {
  success: boolean;
  biometryType: BiometryType;
  errorMessage?: string;
}

export interface BiometricsPort {
  /**
   * Checks whether the current device hardware supports biometric scanning.
   */
  isHardwareAvailable(): Promise<boolean>;

  /**
   * Prompts the user with native hardware biometrics (Fingerprint / FaceID)
   * or executes platform-appropriate fallback verification.
   */
  authenticate(promptReason: string): Promise<BiometricAuthResult>;
}
