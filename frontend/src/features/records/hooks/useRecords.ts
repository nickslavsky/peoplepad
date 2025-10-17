// src/features/records/hooks/useRecords.ts
import { useQuery } from '@tanstack/react-query';
import { components } from '../../../api';
import { fetchWithAuth } from '../../../lib/api';

interface RecordsParams {
  query?: string;
  startDate?: Date | undefined;
  endDate?: Date | undefined;
  tags?: string[];
}

const fetchRecords = async (params: RecordsParams) => {
  try {
    const body: components['schemas']['SearchRequest'] = {
      query: params.query || '',
      start_date: params.startDate ? params.startDate.toISOString().split('T')[0] : null,
      end_date: params.endDate ? params.endDate.toISOString().split('T')[0] : null,
      tags: params.tags || [],
    };

    const response = await fetchWithAuth('/api/search/', {
      method: 'POST',
      body: JSON.stringify(body),
    });

    return response.json() as Promise<components['schemas']['SearchResponse'][]>;
  } catch (error) {
    console.error('Error fetching records:', error);
    throw error; // Rethrow to let react-query handle the error state
  }
};

export const useRecords = (params: RecordsParams) => {
  return useQuery({
    queryKey: ['records', params], // Simplified query key to include all params
    queryFn: () => fetchRecords(params),
    retry: 1, // Retry once on failure
    staleTime: 1000 * 60, // 1 minute stale time
    onError: (error) => {
      console.error('useRecords error:', error);
    },
  });
};