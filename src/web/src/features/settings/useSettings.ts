/**
 * useSettings.ts — TanStack Query hooks per impostazioni
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  getCompanyProfile, updateCompanyProfile, uploadLogo,
  getCompanySettings, updateCompanySettings,
  type CompanyProfile, type CompanySettings,
} from './settingsService';

export function useCompanyProfile() {
  return useQuery({
    queryKey: ['companyProfile'],
    queryFn: getCompanyProfile,
  });
}

export function useUpdateCompanyProfile() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, ...updates }: { id: string } & Partial<CompanyProfile>) =>
      updateCompanyProfile(id, updates),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['companyProfile'] }),
  });
}

export function useUploadLogo() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ companyId, file }: { companyId: string; file: File }) =>
      uploadLogo(companyId, file),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['companyProfile'] }),
  });
}

export function useCompanySettings() {
  return useQuery({
    queryKey: ['companySettings'],
    queryFn: getCompanySettings,
  });
}

export function useUpdateCompanySettings() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, ...updates }: { id: string } & Partial<CompanySettings>) =>
      updateCompanySettings(id, updates),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['companySettings'] }),
  });
}
