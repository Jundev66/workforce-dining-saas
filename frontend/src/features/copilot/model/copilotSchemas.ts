import { z } from 'zod';

export const CopilotResponseSchema = z.object({
  intent: z.string(),
  policy_approved: z.boolean(),
  meal_cancelled: z.boolean(),
  message: z.string(),
  guardrail_passed: z.boolean(),
  audit_trail: z.array(z.string()),
});

export type CopilotResponse = z.infer<typeof CopilotResponseSchema>;
