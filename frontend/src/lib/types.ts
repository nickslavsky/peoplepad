// src/lib/types.ts
import { z } from 'zod';
import { recordCreateSchema, recordResponseSchema, searchRequestSchema, searchResponseSchema, tagResponseSchema } from './schemas';

export type RecordCreate = z.infer<typeof recordCreateSchema>;
export type RecordResponse = z.infer<typeof recordResponseSchema>;
export type SearchRequest = z.infer<typeof searchRequestSchema>;
export type SearchResponse = z.infer<typeof searchResponseSchema>;
export type TagResponse = z.infer<typeof tagResponseSchema>;