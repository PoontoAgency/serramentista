/**
 * settingsService.ts — Servizio impostazioni azienda
 */
import { supabase } from '../../lib/supabase';

export interface CompanyProfile {
  id: string;
  name: string;
  address: string | null;
  city: string | null;
  province: string | null;
  phone: string | null;
  email: string | null;
  vat_number: string | null;
  logo_url: string | null;
}

export interface CompanySettings {
  id: string;
  company_id: string;
  default_margin_pct: number;
  iva_pct: number;
  quote_validity_days: number;
  quote_prefix: string;
}

export async function getCompanyProfile(): Promise<CompanyProfile | null> {
  const { data: user } = await supabase.auth.getUser();
  if (!user?.user) return null;

  const { data, error } = await supabase
    .from('companies')
    .select('id, name, address, city, province, phone, email, vat_number, logo_url')
    .eq('owner_id', user.user.id)
    .single();

  if (error) return null;
  return data;
}

export async function updateCompanyProfile(
  id: string,
  updates: Partial<CompanyProfile>
): Promise<CompanyProfile> {
  const { data, error } = await supabase
    .from('companies')
    .update(updates)
    .eq('id', id)
    .select()
    .single();

  if (error) throw error;
  return data;
}

export async function uploadLogo(companyId: string, file: File): Promise<string> {
  const ext = file.name.split('.').pop();
  const path = `${companyId}/logo.${ext}`;

  const { error: uploadError } = await supabase.storage
    .from('logos')
    .upload(path, file, { upsert: true });

  if (uploadError) throw uploadError;

  const { data } = supabase.storage.from('logos').getPublicUrl(path);
  const logoUrl = data.publicUrl;

  // Aggiorna company
  await supabase.from('companies').update({ logo_url: logoUrl }).eq('id', companyId);

  return logoUrl;
}

export async function getCompanySettings(): Promise<CompanySettings | null> {
  const { data: user } = await supabase.auth.getUser();
  if (!user?.user) return null;

  // Prima trova la company
  const { data: company } = await supabase
    .from('companies')
    .select('id')
    .eq('owner_id', user.user.id)
    .single();

  if (!company) return null;

  const { data, error } = await supabase
    .from('company_settings')
    .select('*')
    .eq('company_id', company.id)
    .single();

  if (error) return null;
  return data;
}

export async function updateCompanySettings(
  id: string,
  updates: Partial<CompanySettings>
): Promise<CompanySettings> {
  const { data, error } = await supabase
    .from('company_settings')
    .update(updates)
    .eq('id', id)
    .select()
    .single();

  if (error) throw error;
  return data;
}
