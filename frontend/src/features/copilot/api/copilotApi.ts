import { apiClient } from '../../../shared/api/client';
import { CopilotResponse, CopilotResponseSchema } from '../model/copilotSchemas';

export interface SendCopilotMessageParams {
  message: string;
  employee_id: string;
}

export async function sendCopilotMessage(params: SendCopilotMessageParams): Promise<CopilotResponse> {
  const rawData = await apiClient<unknown>('/copilot/chat', {
    method: 'POST',
    body: JSON.stringify(params),
  });

  // Client-side anti-hallucination validation with Zod
  const parsed = CopilotResponseSchema.safeParse(rawData);
  if (!parsed.success) {
    throw new Error('Validación Zod fallida: La respuesta del agente no cumple el esquema estricto.');
  }

  return parsed.data;
}
