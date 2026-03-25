/**
 * useCustomers.ts — TanStack Query hooks per clienti
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getCustomers, getCustomerWithQuotes, createCustomer, updateCustomer } from './customerService';
import type { Customer } from './customerService';

export function useCustomers(search?: string) {
  return useQuery({
    queryKey: ['customers', search],
    queryFn: () => getCustomers(search),
  });
}

export function useCustomerDetail(id: string | null) {
  return useQuery({
    queryKey: ['customer', id],
    queryFn: () => getCustomerWithQuotes(id!),
    enabled: !!id,
  });
}

export function useCreateCustomer() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: createCustomer,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['customers'] }),
  });
}

export function useUpdateCustomer() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, ...updates }: { id: string } & Partial<Customer>) =>
      updateCustomer(id, updates),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['customers'] });
      qc.invalidateQueries({ queryKey: ['customer'] });
    },
  });
}
