-- ============================================================
-- MIGRAZIONE 001 — Schema Serramentista v1.0
-- Tutte le 12 tabelle principali
-- ============================================================

-- 1. Profilo azienda (estende auth.users)
CREATE TABLE companies (
  id              UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  company_name    TEXT NOT NULL,
  owner_name      TEXT NOT NULL,
  vat_number      TEXT,
  fiscal_code     TEXT,
  address         TEXT,
  city            TEXT,
  province        TEXT,
  zip_code        TEXT,
  phone           TEXT NOT NULL,
  email           TEXT NOT NULL,
  logo_url        TEXT,
  website         TEXT,
  telegram_chat_id  BIGINT UNIQUE,
  telegram_token    TEXT UNIQUE,
  telegram_linked_at TIMESTAMPTZ,
  onboarding_completed BOOLEAN NOT NULL DEFAULT false,
  subscription_tier    TEXT NOT NULL DEFAULT 'trial'
                       CHECK (subscription_tier IN ('trial','base','pro','partner')),
  trial_ends_at        TIMESTAMPTZ DEFAULT NOW() + INTERVAL '30 days',
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 2. Configurazione azienda
CREATE TABLE company_settings (
  company_id      UUID PRIMARY KEY REFERENCES companies(id) ON DELETE CASCADE,
  default_margin  DECIMAL(5,2) NOT NULL DEFAULT 25.00,
  iva_rate        DECIMAL(4,2) NOT NULL DEFAULT 22.00,
  iva_included    BOOLEAN NOT NULL DEFAULT false,
  quote_validity_days INTEGER NOT NULL DEFAULT 30,
  quote_prefix    TEXT NOT NULL DEFAULT 'SER',
  notify_on_quote_view    BOOLEAN NOT NULL DEFAULT true,
  reminder_days           INTEGER NOT NULL DEFAULT 7,
  pdf_show_company_logo   BOOLEAN NOT NULL DEFAULT true,
  pdf_footer_text         TEXT DEFAULT '',
  pdf_accent_color        TEXT DEFAULT '#1A56DB',
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 3. Clienti
CREATE TABLE customers (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  company_id      UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  name            TEXT NOT NULL,
  phone           TEXT,
  email           TEXT,
  address         TEXT,
  city            TEXT,
  province        TEXT,
  zip_code        TEXT,
  notes           TEXT,
  total_quotes    INTEGER NOT NULL DEFAULT 0,
  total_accepted  INTEGER NOT NULL DEFAULT 0,
  total_value     DECIMAL(12,2) NOT NULL DEFAULT 0,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  deleted_at      TIMESTAMPTZ
);

-- 4. Categorie prodotto
CREATE TABLE product_categories (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  company_id      UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  name            TEXT NOT NULL,
  description     TEXT,
  sort_order      INTEGER NOT NULL DEFAULT 0,
  is_active       BOOLEAN NOT NULL DEFAULT true,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 5. Catalogo prodotti
CREATE TABLE products (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  company_id      UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  category_id     UUID REFERENCES product_categories(id) ON DELETE SET NULL,
  name            TEXT NOT NULL,
  sku             TEXT,
  description     TEXT,
  supplier        TEXT,
  unit            TEXT NOT NULL DEFAULT 'mq' CHECK (unit IN ('mq', 'ml', 'pz')),
  tier            TEXT NOT NULL CHECK (tier IN ('base', 'medio', 'top')),
  price           DECIMAL(10,2) NOT NULL,
  applies_to      TEXT[] DEFAULT ARRAY['battente','scorrevole','vasistas','portafinestra'],
  is_active       BOOLEAN NOT NULL DEFAULT true,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 6. Voci extra preimpostate
CREATE TABLE extra_presets (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  company_id      UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  name            TEXT NOT NULL,
  description     TEXT,
  default_price   DECIMAL(10,2) NOT NULL DEFAULT 0,
  unit            TEXT NOT NULL DEFAULT 'pz' CHECK (unit IN ('pz', 'mq', 'ml', 'ora', 'forfait')),
  is_active       BOOLEAN NOT NULL DEFAULT true,
  sort_order      INTEGER NOT NULL DEFAULT 0,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 7. Preventivi
CREATE TABLE quotes (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  company_id      UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  customer_id     UUID REFERENCES customers(id) ON DELETE SET NULL,
  number          TEXT NOT NULL,
  year            INTEGER NOT NULL DEFAULT EXTRACT(YEAR FROM NOW()),
  status          TEXT NOT NULL DEFAULT 'draft'
                  CHECK (status IN ('draft','ready','sent','viewed','accepted','rejected','expired')),
  subtotal_base   DECIMAL(12,2),
  subtotal_medio  DECIMAL(12,2),
  subtotal_top    DECIMAL(12,2),
  extras_total    DECIMAL(12,2) DEFAULT 0,
  margin_pct      DECIMAL(5,2) NOT NULL DEFAULT 25.00,
  total_base      DECIMAL(12,2),
  total_medio     DECIMAL(12,2),
  total_top       DECIMAL(12,2),
  notes           TEXT,
  customer_notes  TEXT,
  pdf_url         TEXT,
  pdf_generated_at TIMESTAMPTZ,
  sent_at         TIMESTAMPTZ,
  viewed_at       TIMESTAMPTZ,
  responded_at    TIMESTAMPTZ,
  expires_at      TIMESTAMPTZ,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 8. Finestre rilevate
CREATE TABLE windows (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  quote_id        UUID NOT NULL REFERENCES quotes(id) ON DELETE CASCADE,
  position        INTEGER NOT NULL,
  label           TEXT,
  width_mm        DECIMAL(7,1) NOT NULL,
  height_mm       DECIMAL(7,1) NOT NULL,
  area_mq         DECIMAL(8,4) GENERATED ALWAYS AS ((width_mm * height_mm) / 1000000.0) STORED,
  window_type     TEXT NOT NULL DEFAULT 'battente'
                  CHECK (window_type IN ('battente','scorrevole','vasistas','portafinestra','fisso','altro')),
  ai_confidence   TEXT DEFAULT 'media' CHECK (ai_confidence IN ('alta','media','bassa')),
  manually_adjusted BOOLEAN NOT NULL DEFAULT false,
  photo_url       TEXT,
  voice_note_url  TEXT,
  voice_transcript TEXT,
  ai_response_raw JSONB,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 9. Righe prodotto nel preventivo
CREATE TABLE line_items (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  quote_id        UUID NOT NULL REFERENCES quotes(id) ON DELETE CASCADE,
  window_id       UUID REFERENCES windows(id) ON DELETE CASCADE,
  product_id      UUID REFERENCES products(id) ON DELETE SET NULL,
  product_name    TEXT NOT NULL,
  product_tier    TEXT NOT NULL CHECK (product_tier IN ('base','medio','top')),
  product_unit    TEXT NOT NULL,
  quantity        DECIMAL(10,3) NOT NULL,
  unit_price      DECIMAL(10,2) NOT NULL,
  total_price     DECIMAL(10,2) NOT NULL,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 10. Voci extra nel preventivo
CREATE TABLE quote_extras (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  quote_id        UUID NOT NULL REFERENCES quotes(id) ON DELETE CASCADE,
  preset_id       UUID REFERENCES extra_presets(id) ON DELETE SET NULL,
  name            TEXT NOT NULL,
  quantity        DECIMAL(10,3) NOT NULL DEFAULT 1,
  unit            TEXT NOT NULL DEFAULT 'pz',
  unit_price      DECIMAL(10,2) NOT NULL,
  total_price     DECIMAL(10,2) NOT NULL,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 11. Sessioni bot
CREATE TABLE bot_sessions (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  company_id      UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  telegram_chat_id BIGINT NOT NULL UNIQUE,
  state           TEXT NOT NULL DEFAULT 'idle'
                  CHECK (state IN (
                    'idle','awaiting_customer','awaiting_photo',
                    'confirming_measures','selecting_products',
                    'selecting_extras','adjusting_margin','confirming_quote'
                  )),
  current_quote_id UUID REFERENCES quotes(id) ON DELETE SET NULL,
  state_data       JSONB NOT NULL DEFAULT '{}',
  last_activity_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  session_timeout  INTERVAL NOT NULL DEFAULT '2 hours',
  updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 12. Activity log
CREATE TABLE activity_log (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  company_id      UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  entity_type     TEXT NOT NULL,
  entity_id       UUID NOT NULL,
  action          TEXT NOT NULL,
  details         JSONB DEFAULT '{}',
  source          TEXT NOT NULL DEFAULT 'bot' CHECK (source IN ('bot', 'dashboard', 'system')),
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
