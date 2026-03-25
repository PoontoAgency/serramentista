/**
 * useCatalog.ts — TanStack Query hooks per catalogo
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  getCategories,
  createCategory,
  updateCategory,
  deleteCategory,
  getProducts,
  createProduct,
  updateProduct,
  deleteProduct,
  getExtraPresets,
  createExtraPreset,
  updateExtraPreset,
  deleteExtraPreset,
  type ProductCategory,
  type Product,
  type ExtraPreset,
} from './catalogService';

// ── Categorie ──────────────────────────────────────────

export function useCategories() {
  return useQuery({
    queryKey: ['categories'],
    queryFn: getCategories,
  });
}

export function useCreateCategory() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: createCategory,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['categories'] }),
  });
}

export function useUpdateCategory() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, ...updates }: { id: string } & Partial<ProductCategory>) =>
      updateCategory(id, updates),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['categories'] }),
  });
}

export function useDeleteCategory() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: deleteCategory,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['categories'] }),
  });
}

// ── Prodotti ───────────────────────────────────────────

export function useProducts(filters?: { tier?: string; category_id?: string }) {
  return useQuery({
    queryKey: ['products', filters],
    queryFn: () => getProducts(filters),
  });
}

export function useCreateProduct() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: createProduct,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['products'] }),
  });
}

export function useUpdateProduct() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, ...updates }: { id: string } & Partial<Product>) =>
      updateProduct(id, updates),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['products'] }),
  });
}

export function useDeleteProduct() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: deleteProduct,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['products'] }),
  });
}

// ── Extra Presets ──────────────────────────────────────

export function useExtraPresets() {
  return useQuery({
    queryKey: ['extraPresets'],
    queryFn: getExtraPresets,
  });
}

export function useCreateExtraPreset() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: createExtraPreset,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['extraPresets'] }),
  });
}

export function useUpdateExtraPreset() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, ...updates }: { id: string } & Partial<ExtraPreset>) =>
      updateExtraPreset(id, updates),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['extraPresets'] }),
  });
}

export function useDeleteExtraPreset() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: deleteExtraPreset,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['extraPresets'] }),
  });
}
