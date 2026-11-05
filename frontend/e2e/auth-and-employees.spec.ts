import { test, expect } from '@playwright/test';

test.describe('SaaS Workforce & Dining - Mobile Web E2E Flows', () => {
  test('should render login screen with form inputs and buttons', async ({ page }) => {
    await page.goto('/');

    const card = page.getByTestId('login-card');
    await expect(card).toBeVisible();

    await expect(page.getByTestId('input-email')).toBeVisible();
    await expect(page.getByTestId('input-password')).toBeVisible();
    await expect(page.getByTestId('btn-submit-login')).toBeVisible();
    await expect(page.getByTestId('btn-switch-register')).toBeVisible();
  });

  test('should toggle between Login and Register Tenant forms', async ({ page }) => {
    await page.goto('/');

    // Switch to Register
    await page.getByTestId('btn-switch-register').click();
    await expect(page.getByTestId('register-tenant-card')).toBeVisible();
    await expect(page.getByTestId('input-register-name')).toBeVisible();
    await expect(page.getByTestId('input-register-slug')).toBeVisible();
    await expect(page.getByTestId('btn-submit-register')).toBeVisible();

    // Switch back to Login
    await page.getByTestId('btn-switch-login').click();
    await expect(page.getByTestId('login-card')).toBeVisible();
  });

  test('should show validation errors when submitting empty form', async ({ page }) => {
    await page.goto('/');

    await page.getByTestId('btn-submit-login').click();

    await expect(page.getByText('Ingresá un correo electrónico válido')).toBeVisible();
    await expect(page.getByText('La contraseña debe tener al menos 6 caracteres')).toBeVisible();
  });

  test('should complete full tenant onboarding, employee registration, and dining scan flow', async ({ page }) => {
    const uniqueId = Date.now().toString().slice(-6);
    const tenantSlug = `org-${uniqueId}`;
    const adminEmail = `admin-${uniqueId}@testcompany.com`;
    const employeeBadge = `BADGE-${uniqueId}`;

    await page.goto('/');

    // 1. Switch to Register Tenant
    await page.getByTestId('btn-switch-register').click();
    await expect(page.getByTestId('register-tenant-card')).toBeVisible();

    // 2. Fill Register Tenant Form
    await page.getByTestId('input-register-name').fill(`Enterprise ${uniqueId}`);
    await page.getByTestId('input-register-slug').fill(tenantSlug);
    await page.getByTestId('input-register-admin-name').fill('Arquitecto Principal');
    await page.getByTestId('input-register-admin-email').fill(adminEmail);
    await page.getByTestId('input-register-admin-password').fill('Password123!');

    await page.getByTestId('btn-submit-register').click();

    // 3. Confirm transition to Dashboard Screen
    await expect(page.getByTestId('dashboard-screen')).toBeVisible({ timeout: 10000 });
    await expect(page.getByText('Arquitecto Principal (admin)')).toBeVisible();

    // 4. Open Create Employee Modal
    await page.getByTestId('btn-open-create-employee').click();
    await expect(page.getByTestId('modal-create-employee')).toBeVisible();

    // Fill Employee Details
    await page.getByTestId('input-employee-firstname').fill('Juan');
    await page.getByTestId('input-employee-lastname').fill('Perez');
    await page.getByTestId('input-employee-document').fill(`DOC-${uniqueId}`);
    await page.getByTestId('input-employee-department').fill('Operaciones');
    await page.getByTestId('input-employee-position').fill('Operario Especializado');
    await page.getByTestId('input-employee-badge').fill(employeeBadge);

    await page.getByTestId('btn-submit-employee').click();

    // Employee should be displayed in the workforce virtualized list
    await expect(page.getByText('Juan Perez')).toBeVisible({ timeout: 5000 });
    await expect(page.getByText('Operario Especializado')).toBeVisible();

    // 5. Navigate to Dining & AI Dashboard
    await page.getByTestId('tab-dining').click();
    await expect(page.getByTestId('terminal-scan-card')).toBeVisible();

    // Check WebSocket status indicator presence
    await expect(page.getByTestId('ws-status-indicator')).toBeVisible();

    // 6. Scan badge for lunch
    await page.getByTestId('input-scan-badge').fill(employeeBadge);
    await page.getByTestId('btn-scan-meal').click();

    // Verify successful authorization banner
    await expect(page.getByTestId('scan-result-banner')).toBeVisible({ timeout: 5000 });
    await expect(page.getByText('✓ RACIÓN AUTORIZADA')).toBeVisible();
    await expect(page.getByText(/Personal: Juan Perez/)).toBeVisible();

    // 7. Verify duplicate protection: scan same badge again
    await page.getByTestId('input-scan-badge').fill(employeeBadge);
    await page.getByTestId('btn-scan-meal').click();

    await expect(page.getByText('✕ ACCESO DENEGADO')).toBeVisible({ timeout: 5000 });
    await expect(page.getByText(/Ración duplicada/i)).toBeVisible();
  });
});
