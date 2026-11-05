import { z } from 'zod';

export const loginSchema = z.object({
  email: z.string().email('Ingresá un correo electrónico válido'),
  password: z.string().min(6, 'La contraseña debe tener al menos 6 caracteres'),
  tenantSlug: z.string().optional(),
});

export type LoginFormData = z.infer<typeof loginSchema>;

export const registerTenantSchema = z.object({
  tenantName: z.string().min(2, 'El nombre de la empresa debe tener al menos 2 caracteres'),
  tenantSlug: z.string().min(2, 'El identificador debe tener al menos 2 caracteres')
    .regex(/^[a-z0-9-]+$/, 'Solo minúsculas, números y guiones'),
  adminFullName: z.string().min(2, 'El nombre debe tener al menos 2 caracteres'),
  adminEmail: z.string().email('Ingresá un correo válido'),
  adminPassword: z.string().min(8, 'La contraseña debe tener al menos 8 caracteres'),
});

export type RegisterTenantFormData = z.infer<typeof registerTenantSchema>;
