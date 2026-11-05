import { useState, useEffect, useCallback } from 'react';
import { biometricsAdapter } from '../infrastructure/biometricsAdapter';
import { BiometricAuthResult } from '../model/biometricsPort';

export function useBiometrics() {
  const [isAvailable, setIsAvailable] = useState<boolean>(false);
  const [isAuthenticating, setIsAuthenticating] = useState<boolean>(false);

  useEffect(() => {
    let isMounted = true;
    biometricsAdapter.isHardwareAvailable().then((available) => {
      if (isMounted) {
        setIsAvailable(available);
      }
    });
    return () => {
      isMounted = false;
    };
  }, []);

  const authenticateWithBiometrics = useCallback(
    async (reason = 'Verificación biométrica para ración de comedor'): Promise<BiometricAuthResult> => {
      setIsAuthenticating(true);
      try {
        const result = await biometricsAdapter.authenticate(reason);
        return result;
      } finally {
        setIsAuthenticating(false);
      }
    },
    []
  );

  return {
    isAvailable,
    isAuthenticating,
    authenticateWithBiometrics,
  };
}
