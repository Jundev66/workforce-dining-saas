import { test, expect } from '@playwright/test';

test.describe('Offline-First Architecture & Network Sync', () => {
  test('should detect network disconnection and display real-time offline warning banner', async ({ page }) => {
    await page.goto('/');

    // Initially online, banner should not be present
    await expect(page.getByTestId('offline-banner')).not.toBeVisible();

    // Emulate offline network conditions
    await page.context().setOffline(true);

    // Verify offline banner appears reactively
    await expect(page.getByTestId('offline-banner')).toBeVisible({ timeout: 5000 });
    await expect(page.getByText(/Modo sin conexión/i)).toBeVisible();

    // Restore online network conditions
    await page.context().setOffline(false);

    // Verify offline banner disappears automatically
    await expect(page.getByTestId('offline-banner')).not.toBeVisible({ timeout: 5000 });
  });
});
