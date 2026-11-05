import { test, expect } from '@playwright/test';

test.describe('SaaS Workforce & Dining - Mobile Web E2E Flows', () => {
  test('should render login screen with form inputs and buttons', async ({ page }) => {
    await page.goto('/');

    // Verify auth card rendered
    const card = page.getByTestId('login-card');
    await expect(card).toBeVisible();

    // Verify inputs present
    await expect(page.getByTestId('input-email')).toBeVisible();
    await expect(page.getByTestId('input-password')).toBeVisible();
    await expect(page.getByTestId('btn-submit-login')).toBeVisible();
    await expect(page.getByTestId('btn-switch-register')).toBeVisible();
  });

  test('should toggle between Login and Register Tenant forms', async ({ page }) => {
    await page.goto('/');

    // Click to switch to Register Tenant
    await page.getByTestId('btn-switch-register').click();

    // Verify Register Tenant card is visible
    await expect(page.getByTestId('register-tenant-card')).toBeVisible();
    await expect(page.getByTestId('input-register-name')).toBeVisible();
    await expect(page.getByTestId('input-register-slug')).toBeVisible();
    await expect(page.getByTestId('input-register-admin-name')).toBeVisible();
    await expect(page.getByTestId('btn-submit-register')).toBeVisible();

    // Switch back to Login
    await page.getByTestId('btn-switch-login').click();
    await expect(page.getByTestId('login-card')).toBeVisible();
  });

  test('should show validation errors when submitting empty form', async ({ page }) => {
    await page.goto('/');

    await page.getByTestId('btn-submit-login').click();

    // Zod validation messages
    await expect(page.getByText('Ingresá un correo electrónico válido')).toBeVisible();
    await expect(page.getByText('La contraseña debe tener al menos 6 caracteres')).toBeVisible();
  });
});
