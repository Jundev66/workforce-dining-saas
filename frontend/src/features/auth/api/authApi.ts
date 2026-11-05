import { apiClient } from '../../../shared/api/client';
import { LoginFormData, RegisterTenantFormData } from '../model/authSchemas';
import { UserSession } from '../model/authStore';

export interface AuthApiResponse {
  access_token: string;
  token_type: string;
  user_id: string;
  tenant_id: string;
  role: string;
  full_name: string;
  email: string;
}

export const authApi = {
  login: async (data: LoginFormData): Promise<{ token: string; user: UserSession }> => {
    const res = await apiClient<AuthApiResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({
        email: data.email,
        password: data.password,
        tenant_slug: data.tenantSlug || undefined,
      }),
    });

    return {
      token: res.access_token,
      user: {
        userId: res.user_id,
        tenantId: res.tenant_id,
        fullName: res.full_name,
        email: res.email,
        role: res.role,
      },
    };
  },

  registerTenant: async (data: RegisterTenantFormData): Promise<{ token: string; user: UserSession }> => {
    const res = await apiClient<AuthApiResponse>('/auth/register-tenant', {
      method: 'POST',
      body: JSON.stringify({
        tenant_name: data.tenantName,
        tenant_slug: data.tenantSlug,
        admin_full_name: data.adminFullName,
        admin_email: data.adminEmail,
        admin_password: data.adminPassword,
      }),
    });

    return {
      token: res.access_token,
      user: {
        userId: res.user_id,
        tenantId: res.tenant_id,
        fullName: res.full_name,
        email: res.email,
        role: res.role,
      },
    };
  },
};
