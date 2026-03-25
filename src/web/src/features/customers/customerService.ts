/**
 * customerService.ts — CRUD clienti
 */
import { supabase } from '../../lib/supabase';

export interface Customer {
  id: string;
  company_id: string;
  name: string;
  address: string | null;
  city: string | null;
  province: string | null;
  phone: string | null;
  email: string | null;
  vat_number: string | null;
  fiscal_code: string | null;
  notes: string | null;
  created_at: string;
}

export async function getCustomers(search?: string): Promise<Customer[]> {
  let query = supabase
    .from('customers')
    .select('*')
    .order('name');

  if (search) query = query.ilike('name', `%${search}%`);

  const { data, error } = await query;
  if (error) throw error;
  return data || [];
}

export async function getCustomerWithQuotes(id: string) {
  const [customer, quotes] = await Promise.all([
    supabase.from('customers').select('*').eq('id', id).single(),
    supabase.from('quotes')
      .select('id, number, status, total_medio, created_at')
      .eq('customer_id', id)
      .order('created_at', { ascending: false }),
  ]);

  return {
    customer: customer.data,
    quotes: quotes.data || [],
  };
}

export async function createCustomer(
  customer: Pick<Customer, 'name' | 'address' | 'city' | 'phone' | 'email'>
): Promise<Customer> {
  const { data: user } = await supabase.auth.getUser();
  if (!user?.user) throw new Error('Non autenticato');

  const { data, error } = await supabase
    .from('customers')
    .insert({ ...customer, company_id: user.user.id })
    .select()
    .single();

  if (error) throw error;
  return data;
}

export async function updateCustomer(
  id: string,
  updates: Partial<Customer>
): Promise<Customer> {
  const { data, error } = await supabase
    .from('customers')
    .update(updates)
    .eq('id', id)
    .select()
    .single();

  if (error) throw error;
  return data;
}
