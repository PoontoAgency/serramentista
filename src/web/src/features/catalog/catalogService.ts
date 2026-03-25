/**
 * catalogService.ts — CRUD Supabase per catalogo prodotti e voci extra
 */
import { supabase } from '../../lib/supabase';

// ── Types ──────────────────────────────────────────────

export interface ProductCategory {
  id: string;
  company_id: string;
  name: string;
  description?: string;
  sort_order: number;
  is_active: boolean;
  created_at: string;
}

export interface Product {
  id: string;
  company_id: string;
  category_id: string | null;
  name: string;
  sku?: string;
  description?: string;
  supplier?: string;
  unit: 'mq' | 'ml' | 'pz';
  tier: 'base' | 'medio' | 'top';
  price: number;
  applies_to: string[];
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ExtraPreset {
  id: string;
  company_id: string;
  name: string;
  description?: string;
  default_price: number;
  unit: 'pz' | 'mq' | 'ml' | 'ora' | 'forfait';
  is_active: boolean;
  sort_order: number;
  created_at: string;
}

// ── Categorie ──────────────────────────────────────────

export async function getCategories(): Promise<ProductCategory[]> {
  const { data, error } = await supabase
    .from('product_categories')
    .select('*')
    .eq('is_active', true)
    .order('sort_order');

  if (error) throw error;
  return data || [];
}

export async function createCategory(
  category: Pick<ProductCategory, 'name' | 'description'>
): Promise<ProductCategory> {
  const { data: user } = await supabase.auth.getUser();
  if (!user?.user) throw new Error('Non autenticato');

  const { data, error } = await supabase
    .from('product_categories')
    .insert({ ...category, company_id: user.user.id })
    .select()
    .single();

  if (error) throw error;
  return data;
}

export async function updateCategory(
  id: string,
  updates: Partial<Pick<ProductCategory, 'name' | 'description' | 'sort_order' | 'is_active'>>
): Promise<ProductCategory> {
  const { data, error } = await supabase
    .from('product_categories')
    .update(updates)
    .eq('id', id)
    .select()
    .single();

  if (error) throw error;
  return data;
}

export async function deleteCategory(id: string): Promise<void> {
  const { error } = await supabase
    .from('product_categories')
    .update({ is_active: false })
    .eq('id', id);

  if (error) throw error;
}

// ── Prodotti ───────────────────────────────────────────

export async function getProducts(
  filters?: { tier?: string; category_id?: string }
): Promise<Product[]> {
  let query = supabase
    .from('products')
    .select('*')
    .eq('is_active', true)
    .order('name');

  if (filters?.tier) query = query.eq('tier', filters.tier);
  if (filters?.category_id) query = query.eq('category_id', filters.category_id);

  const { data, error } = await query;
  if (error) throw error;
  return data || [];
}

export async function createProduct(
  product: Omit<Product, 'id' | 'company_id' | 'is_active' | 'created_at' | 'updated_at'>
): Promise<Product> {
  const { data: user } = await supabase.auth.getUser();
  if (!user?.user) throw new Error('Non autenticato');

  const { data, error } = await supabase
    .from('products')
    .insert({ ...product, company_id: user.user.id })
    .select()
    .single();

  if (error) throw error;
  return data;
}

export async function updateProduct(
  id: string,
  updates: Partial<Product>
): Promise<Product> {
  const { data, error } = await supabase
    .from('products')
    .update(updates)
    .eq('id', id)
    .select()
    .single();

  if (error) throw error;
  return data;
}

export async function deleteProduct(id: string): Promise<void> {
  const { error } = await supabase
    .from('products')
    .update({ is_active: false })
    .eq('id', id);

  if (error) throw error;
}

// ── Extra Presets ──────────────────────────────────────

export async function getExtraPresets(): Promise<ExtraPreset[]> {
  const { data, error } = await supabase
    .from('extra_presets')
    .select('*')
    .eq('is_active', true)
    .order('sort_order');

  if (error) throw error;
  return data || [];
}

export async function createExtraPreset(
  preset: Pick<ExtraPreset, 'name' | 'description' | 'default_price' | 'unit'>
): Promise<ExtraPreset> {
  const { data: user } = await supabase.auth.getUser();
  if (!user?.user) throw new Error('Non autenticato');

  const { data, error } = await supabase
    .from('extra_presets')
    .insert({ ...preset, company_id: user.user.id })
    .select()
    .single();

  if (error) throw error;
  return data;
}

export async function updateExtraPreset(
  id: string,
  updates: Partial<ExtraPreset>
): Promise<ExtraPreset> {
  const { data, error } = await supabase
    .from('extra_presets')
    .update(updates)
    .eq('id', id)
    .select()
    .single();

  if (error) throw error;
  return data;
}

export async function deleteExtraPreset(id: string): Promise<void> {
  const { error } = await supabase
    .from('extra_presets')
    .update({ is_active: false })
    .eq('id', id);

  if (error) throw error;
}
