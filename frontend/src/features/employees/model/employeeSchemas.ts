import { z } from 'zod';

export const employeeFormSchema = z.object({
  firstName: z.string().min(1, 'El nombre es obligatorio'),
  lastName: z.string().min(1, 'El apellido es obligatorio'),
  documentId: z.string().min(3, 'El documento debe tener al menos 3 caracteres'),
  department: z.string().min(1, 'El departamento es obligatorio'),
  position: z.string().min(1, 'El cargo es obligatorio'),
  email: z.string().email('Email inválido').optional().or(z.literal('')),
  phone: z.string().optional().or(z.literal('')),
  badgeCode: z.string().optional().or(z.literal('')),
});

export type EmployeeFormData = z.infer<typeof employeeFormSchema>;
