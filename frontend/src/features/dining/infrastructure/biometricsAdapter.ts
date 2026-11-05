import { Platform } from 'react-native';
import { BiometricsPort } from '../model/biometricsPort';
import { WebBiometricsAdapter } from './biometricsAdapter.web';
import { NativeBiometricsAdapter } from './biometricsAdapter.native';

/**
 * Universal Biometrics Service (Port Resolver):
 * Resolves the appropriate Hexagonal Adapter based on the runtime platform.
 */
export const biometricsAdapter: BiometricsPort =
  Platform.OS === 'web' ? new WebBiometricsAdapter() : new NativeBiometricsAdapter();
