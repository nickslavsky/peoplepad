// src/lib/schemas.ts
import { z } from 'zod';

export const recordCreateSchema = z.object({
  name: z.string().min(1),
  notes: z.string().nullable(),
  tags: z.array(z.string()).default([]),
});

export const recordUpdateSchema = recordCreateSchema;

export const recordResponseSchema = z.object({
  id: z.string().uuid(),
  user_id: z.string().uuid(),
  name: z.string(),
  notes: z.string().nullable(),
  tags: z.array(z.string()),
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
});

export const searchRequestSchema = z.object({
  query: z.string().min(1),
  start_date: z.string().datetime().nullable(),
  end_date: z.string().datetime().nullable(),
  tags: z.array(z.string()).default([]),
});

export const searchResponseSchema = recordResponseSchema.extend({
  distance: z.number(),
});

export const tagResponseSchema = z.object({
  id: z.string().uuid(),
  name: z.string(),
});