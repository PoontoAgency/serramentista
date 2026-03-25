/**
 * useQuotes.ts — TanStack Query hooks per preventivi
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getQuotes, getQuoteDetail, updateQuoteStatus, getQuoteStats } from './quoteService';

export function useQuotes(filters?: { status?: string; search?: string }) {
  return useQuery({
    queryKey: ['quotes', filters],
    queryFn: () => getQuotes(filters),
  });
}

export function useQuoteDetail(id: string | null) {
  return useQuery({
    queryKey: ['quote', id],
    queryFn: () => getQuoteDetail(id!),
    enabled: !!id,
  });
}

export function useUpdateQuoteStatus() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, status }: { id: string; status: string }) =>
      updateQuoteStatus(id, status),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['quotes'] });
      qc.invalidateQueries({ queryKey: ['quote'] });
      qc.invalidateQueries({ queryKey: ['quoteStats'] });
    },
  });
}

export function useQuoteStats() {
  return useQuery({
    queryKey: ['quoteStats'],
    queryFn: getQuoteStats,
  });
}
