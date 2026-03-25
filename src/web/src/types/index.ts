// === Serramentista — TypeScript Types ===
// Corrispondono allo schema Supabase (TDD §4)

export interface Company {
  id: string
  company_name: string
  owner_name: string
  vat_number: string | null
  fiscal_code: string | null
  address: string | null
  city: string | null
  province: string | null
  zip_code: string | null
  phone: string
  email: string
  logo_url: string | null
  website: string | null
  telegram_chat_id: number | null
  telegram_token: string | null
  telegram_linked_at: string | null
  onboarding_completed: boolean
  subscription_tier: 'trial' | 'base' | 'pro' | 'partner'
  trial_ends_at: string | null
  created_at: string
  updated_at: string
}

export interface CompanySettings {
  company_id: string
  default_margin: number
  iva_rate: number
  iva_included: boolean
  quote_validity_days: number
  quote_prefix: string
  notify_on_quote_view: boolean
  reminder_days: number
  pdf_show_company_logo: boolean
  pdf_footer_text: string
  pdf_accent_color: string
  updated_at: string
}

export interface Customer {
  id: string
  company_id: string
  name: string
  phone: string | null
  email: string | null
  address: string | null
  city: string | null
  province: string | null
  zip_code: string | null
  notes: string | null
  total_quotes: number
  total_accepted: number
  total_value: number
  created_at: string
  updated_at: string
  deleted_at: string | null
}

export interface ProductCategory {
  id: string
  company_id: string
  name: string
  description: string | null
  sort_order: number
  is_active: boolean
  created_at: string
}

export type ProductTier = 'base' | 'medio' | 'top'
export type ProductUnit = 'mq' | 'ml' | 'pz'

export interface Product {
  id: string
  company_id: string
  category_id: string | null
  name: string
  sku: string | null
  description: string | null
  supplier: string | null
  unit: ProductUnit
  tier: ProductTier
  price: number
  applies_to: string[]
  is_active: boolean
  created_at: string
  updated_at: string
}

export type QuoteStatus = 'draft' | 'ready' | 'sent' | 'viewed' | 'accepted' | 'rejected' | 'expired'

export interface Quote {
  id: string
  company_id: string
  customer_id: string | null
  number: string
  year: number
  status: QuoteStatus
  subtotal_base: number | null
  subtotal_medio: number | null
  subtotal_top: number | null
  extras_total: number | null
  margin_pct: number
  total_base: number | null
  total_medio: number | null
  total_top: number | null
  notes: string | null
  customer_notes: string | null
  pdf_url: string | null
  pdf_generated_at: string | null
  sent_at: string | null
  viewed_at: string | null
  responded_at: string | null
  expires_at: string | null
  created_at: string
  updated_at: string
  // Relazioni (opzionali, populate via join)
  customer?: Customer
  windows?: QuoteWindow[]
}

export type WindowType = 'battente' | 'scorrevole' | 'vasistas' | 'portafinestra' | 'fisso' | 'altro'

export interface QuoteWindow {
  id: string
  quote_id: string
  position: number
  label: string | null
  width_mm: number
  height_mm: number
  area_mq: number
  window_type: WindowType
  ai_confidence: 'alta' | 'media' | 'bassa'
  manually_adjusted: boolean
  photo_url: string | null
  voice_note_url: string | null
  voice_transcript: string | null
  ai_response_raw: Record<string, unknown> | null
  created_at: string
}

export interface LineItem {
  id: string
  quote_id: string
  window_id: string | null
  product_id: string | null
  product_name: string
  product_tier: ProductTier
  product_unit: string
  quantity: number
  unit_price: number
  total_price: number
  created_at: string
}

export interface QuoteExtra {
  id: string
  quote_id: string
  preset_id: string | null
  name: string
  quantity: number
  unit: string
  unit_price: number
  total_price: number
  created_at: string
}

export interface ExtraPreset {
  id: string
  company_id: string
  name: string
  description: string | null
  default_price: number
  unit: string
  is_active: boolean
  sort_order: number
  created_at: string
}
