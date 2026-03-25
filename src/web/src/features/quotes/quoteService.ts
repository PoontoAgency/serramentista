/**
 * quoteService.ts — Servizio preventivi per dashboard
 */
import { supabase } from '../../lib/supabase';

export interface Quote {
  id: string;
  company_id: string;
  customer_id: string | null;
  number: string;
  year: number;
  status: 'draft' | 'ready' | 'sent' | 'accepted' | 'rejected';
  subtotal_base: number;
  subtotal_medio: number;
  subtotal_top: number;
  extras_total: number;
  margin_pct: number;
  total_base: number;
  total_medio: number;
  total_top: number;
  pdf_url: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
  customers?: { name: string; address: string; city: string } | null;
}

export interface QuoteWithDetails extends Quote {
  windows: any[];
  extras: any[];
  line_items: any[];
}

export async function getQuotes(filters?: {
  status?: string;
  search?: string;
}): Promise<Quote[]> {
  let query = supabase
    .from('quotes')
    .select('*, customers(name, address, city)')
    .order('created_at', { ascending: false });

  if (filters?.status) query = query.eq('status', filters.status);
  if (filters?.search) query = query.ilike('number', `%${filters.search}%`);

  const { data, error } = await query;
  if (error) throw error;
  return data || [];
}

export async function getQuoteDetail(id: string): Promise<QuoteWithDetails | null> {
  const { data: quote, error } = await supabase
    .from('quotes')
    .select('*, customers(name, address, city)')
    .eq('id', id)
    .single();

  if (error || !quote) return null;

  const [windows, extras, lineItems] = await Promise.all([
    supabase.from('windows').select('*').eq('quote_id', id).order('position'),
    supabase.from('quote_extras').select('*').eq('quote_id', id),
    supabase.from('line_items').select('*').eq('quote_id', id),
  ]);

  return {
    ...quote,
    windows: windows.data || [],
    extras: extras.data || [],
    line_items: lineItems.data || [],
  };
}

export async function updateQuoteStatus(id: string, status: string): Promise<void> {
  const { error } = await supabase
    .from('quotes')
    .update({ status, updated_at: new Date().toISOString() })
    .eq('id', id);
  if (error) throw error;
}

export async function getQuoteStats(): Promise<{
  total: number;
  draft: number;
  sent: number;
  accepted: number;
  totalValue: number;
}> {
  const { data, error } = await supabase
    .from('quotes')
    .select('status, total_medio');

  if (error) throw error;
  const quotes = data || [];
  return {
    total: quotes.length,
    draft: quotes.filter(q => q.status === 'draft').length,
    sent: quotes.filter(q => q.status === 'sent' || q.status === 'ready').length,
    accepted: quotes.filter(q => q.status === 'accepted').length,
    totalValue: quotes
      .filter(q => q.status === 'accepted')
      .reduce((sum, q) => sum + (q.total_medio || 0), 0),
  };
}
