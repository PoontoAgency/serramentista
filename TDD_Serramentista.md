# 🪟 TDD — Serramentista

**Versione:** 1.0
**Data:** 25/03/2026
**Autore:** Claude (Antigravity) per Stefano Colicino / Poonto
**Status:** Draft — Da approvare

---

## Indice

1. [Visione e Obiettivo](#1-visione-e-obiettivo)
2. [Architettura di Sistema](#2-architettura-di-sistema)
3. [Stack Tecnologico](#3-stack-tecnologico)
4. [Schema Dati](#4-schema-dati)
5. [Pipeline AI Vision](#5-pipeline-ai-vision)
6. [Architettura Bot Telegram](#6-architettura-bot-telegram)
7. [Dashboard Web](#7-dashboard-web)
8. [Generazione PDF](#8-generazione-pdf)
9. [Sicurezza e Multi-tenancy](#9-sicurezza-e-multi-tenancy)
10. [Flussi Operativi](#10-flussi-operativi)
11. [Deploy e Infrastruttura](#11-deploy-e-infrastruttura)
12. [Piano di Test](#12-piano-di-test)
13. [Decisioni Architetturali (ADR)](#13-decisioni-architetturali-adr)
14. [Rischi e Mitigazione](#14-rischi-e-mitigazione)
15. [Milestone di Sviluppo](#15-milestone-di-sviluppo)
16. [Technical Debt Register](#16-technical-debt-register)
17. [Convenzioni e Standard](#17-convenzioni-e-standard)

---

## 1. Visione e Obiettivo

**Problema:** Un serramentista oggi impiega 30-60 minuti per un preventivo di massima. Deve misurare manualmente ogni finestra, trascrivere le misure, aprire un foglio Excel, cercare i prezzi, calcolare, formattare un PDF. Spesso lo fa giorni dopo il sopralluogo, quando il cliente si è già raffreddato.

**Soluzione:** Serramentista azzera questo tempo. Il serramentista incolla un marker adesivo sulla finestra, scatta una foto con Telegram, e l'AI calcola le misure. Finestra dopo finestra, il preventivo si costruisce da solo. Quando ha finito, sceglie i prodotti, regola il margine e invia il PDF — tutto dal telefono, mentre è ancora in casa del cliente.

**Metriche di successo MVP:**
- Tempo medio preventivo: < 10 minuti (da 30-60)
- Precisione misure AI: ±5mm (sufficiente per stima)
- Tasso di conversione preventivi: misurabile dal CRM

---

## 2. Architettura di Sistema

### 2.1 Vista ad alto livello

```
                         ┌──────────────────────────┐
                         │     SERRAMENTISTA         │
                         │      (telefono)           │
                         └─────┬──────────┬──────────┘
                               │          │
                    Telegram   │          │  Browser
                               ▼          ▼
                    ┌──────────────┐  ┌──────────────────┐
                    │  Bot Python  │  │  Dashboard React  │
                    │  (Railway)   │  │  (Vercel)         │
                    └──────┬───┬──┘  └────────┬──────────┘
                           │   │              │
              ┌────────────┘   └──────┐       │
              ▼                       ▼       ▼
     ┌──────────────┐         ┌──────────────────────┐
     │  OpenAI API  │         │      Supabase        │
     │  ─ GPT-4o    │         │  ┌─────────────────┐ │
     │  ─ Whisper   │         │  │ PostgreSQL + RLS│ │
     │              │         │  │ Auth (JWT)      │ │
     └──────────────┘         │  │ Storage (S3)    │ │
                              │  │ Edge Functions  │ │
                              │  └─────────────────┘ │
                              └──────────────────────┘
```

### 2.2 Principi architetturali

| Principio | Implementazione |
|-----------|----------------|
| **Separazione netta** | Il bot è un processo Python standalone. La dashboard è una SPA React. Non condividono codice, solo il database. |
| **Database come fonte di verità** | Tutta la logica di stato vive su Supabase. Se il bot crasha, la sessione si riprende dal DB. |
| **Multi-tenancy by design** | Row Level Security su ogni tabella. Un serramentista non vede MAI i dati di un altro. |
| **AI come servizio** | L'AI è una chiamata API sostituibile. Oggi GPT-4o, domani OpenCV o un modello custom. L'interfaccia resta la stessa. |
| **Offline-first per i dati** | Le foto vengono salvate su Supabase Storage immediatamente. Se il calcolo AI fallisce, la foto è già al sicuro. |

---

## 3. Stack Tecnologico

### 3.1 Bot Backend (Python)

| Componente | Tecnologia | Versione | Motivazione |
|-----------|-----------|---------|-------------|
| Framework bot | python-telegram-bot | 21.x | Async nativo, ConversationHandler built-in, mantenuto attivamente |
| HTTP client | httpx | 0.27+ | Async, timeout granulare, retry built-in |
| Supabase SDK | supabase-py | 2.x | Client ufficiale, supporta RLS |
| PDF engine | WeasyPrint | 62+ | HTML/CSS → PDF, supporta layout multi-colonna per le 3 opzioni |
| Template engine | Jinja2 | 3.x | Template HTML per PDF + messaggi bot |
| Image processing | Pillow | 10+ | Resize/compress foto prima di inviarle all'AI |
| Validazione | Pydantic | 2.x | Parsing e validazione risposte AI (JSON) |
| Config | python-dotenv | 1.x | Gestione variabili ambiente |
| Logging | structlog | 24+ | Log strutturati JSON per debugging produzione |
| Runtime | Python | 3.12 | Pattern matching, performance migliorate |

### 3.2 Dashboard Frontend (React)

| Componente | Tecnologia | Versione | Motivazione |
|-----------|-----------|---------|-------------|
| Framework | React | 19.x | |
| Build tool | Vite | 6.x | HMR veloce, build ottimizzata |
| Linguaggio | TypeScript | 5.x | Type safety, autocompletamento |
| Styling | Tailwind CSS | 4.x | Utility-first, veloce da iterare |
| Router | React Router | 7.x | Nested routes, loader pattern |
| State management | Zustand | 5.x | Store leggero, zero boilerplate |
| Server state | TanStack Query | 5.x | Cache, retry, optimistic updates |
| DB client | supabase-js | 2.x | Auth + RLS + Realtime |
| Forms | React Hook Form + Zod | 7.x + 3.x | Validazione type-safe |
| UI primitivi | Radix UI | latest | Accessibilità built-in |
| Icons | Lucide React | latest | Coerenti, leggere |
| Toast | Sonner | latest | Notifiche non-intrusive |
| Charts | Recharts | 2.x | Dashboard stats |

### 3.3 Infrastruttura

| Servizio | Provider | Piano | Costo stimato |
|---------|---------|-------|---------------|
| Bot hosting | Railway | Starter ($5/mese) | ~$5-8/mese |
| Dashboard hosting | Vercel | Free / Pro | $0-20/mese |
| Database + Auth + Storage | Supabase | Free → Pro | $0-25/mese |
| AI Vision | OpenAI GPT-4o | Pay per use | ~$0.02/preventivo |
| AI Voice | OpenAI Whisper | Pay per use | ~$0.006/minuto |
| **Totale stimato** | | | **$5-55/mese** |

---

## 4. Schema Dati

### 4.1 Entity-Relationship Diagram

```
┌─────────────────────┐
│  auth.users          │ (gestito da Supabase Auth)
└──────────┬──────────┘
           │ 1:1
           ▼
┌─────────────────────┐     ┌──────────────────┐
│  companies          │────▶│  company_settings │
│  (profilo azienda)  │ 1:1 │  (config avanzata)│
└──────┬──┬──┬──┬─────┘     └──────────────────┘
       │  │  │  │
       │  │  │  └─── 1:N ──▶ ┌─────────────────┐
       │  │  │               │  extra_presets   │
       │  │  │               │  (voci standard) │
       │  │  │               └─────────────────┘
       │  │  │
       │  │  └── 1:N ──▶ ┌──────────────────────┐
       │  │              │  product_categories  │
       │  │              └──────────┬───────────┘
       │  │                         │ 1:N
       │  │                         ▼
       │  │              ┌──────────────────────┐
       │  │              │  products            │
       │  │              │  (catalogo per tier)  │
       │  │              └──────────────────────┘
       │  │
       │  └──── 1:N ──▶ ┌──────────────────────┐
       │                │  customers           │
       │                │  (anagrafica clienti) │
       │                └──────────────────────┘
       │
       └────── 1:N ──▶ ┌──────────────────────┐
                       │  quotes              │
                       │  (preventivi)         │
                       └──┬──┬──┬─────────────┘
                          │  │  │
            ┌─────────────┘  │  └──────────────┐
            ▼                ▼                  ▼
   ┌─────────────┐  ┌──────────────┐  ┌──────────────┐
   │  windows    │  │  line_items  │  │  extras      │
   │  (finestre) │  │  (righe prod)│  │  (voci extra)│
   └─────────────┘  └──────────────┘  └──────────────┘

   ┌──────────────────────┐
   │  bot_sessions        │  (state machine conversazione)
   │  1:1 con company     │
   └──────────────────────┘
```

### 4.2 Schema SQL completo

```sql
-- ============================================================
-- SCHEMA SERRAMENTISTA v1.0
-- Convenzioni:
--   - UUID per tutte le PK
--   - created_at / updated_at su ogni tabella
--   - soft delete con deleted_at dove serve
--   - RLS su ogni tabella pubblica
-- ============================================================

-- 1. Profilo azienda (estende auth.users)
CREATE TABLE companies (
  id              UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  company_name    TEXT NOT NULL,
  owner_name      TEXT NOT NULL,
  vat_number      TEXT,                     -- P.IVA (opzionale per piccoli artigiani)
  fiscal_code     TEXT,                     -- Codice fiscale
  address         TEXT,
  city            TEXT,
  province        TEXT,                     -- sigla 2 char (AV, MI, RM...)
  zip_code        TEXT,
  phone           TEXT NOT NULL,
  email           TEXT NOT NULL,
  logo_url        TEXT,                     -- URL su Supabase Storage
  website         TEXT,
  
  -- Collegamento Telegram
  telegram_chat_id  BIGINT UNIQUE,          -- Chat ID del serramentista
  telegram_token    TEXT UNIQUE,            -- Token monouso per /connect
  telegram_linked_at TIMESTAMPTZ,
  
  -- Stato account
  onboarding_completed BOOLEAN NOT NULL DEFAULT false,
  subscription_tier    TEXT NOT NULL DEFAULT 'trial'
                       CHECK (subscription_tier IN ('trial','base','pro','partner')),
  trial_ends_at        TIMESTAMPTZ DEFAULT NOW() + INTERVAL '30 days',
  
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 2. Configurazione azienda (separata per non appesantire la tabella principale)
CREATE TABLE company_settings (
  company_id      UUID PRIMARY KEY REFERENCES companies(id) ON DELETE CASCADE,
  
  -- Preventivo
  default_margin  DECIMAL(5,2) NOT NULL DEFAULT 25.00,  -- margine % default
  iva_rate        DECIMAL(4,2) NOT NULL DEFAULT 22.00,   -- IVA %
  iva_included    BOOLEAN NOT NULL DEFAULT false,         -- prezzi IVA inclusa?
  quote_validity_days INTEGER NOT NULL DEFAULT 30,        -- validità preventivo
  quote_prefix    TEXT NOT NULL DEFAULT 'SER',            -- prefisso numerazione
  
  -- Notifiche
  notify_on_quote_view    BOOLEAN NOT NULL DEFAULT true,  -- V2: notifica quando il cliente apre il PDF
  reminder_days           INTEGER NOT NULL DEFAULT 7,     -- V2: giorni prima del reminder
  
  -- PDF
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
  
  -- Statistiche calcolate (aggiornate via trigger)
  total_quotes    INTEGER NOT NULL DEFAULT 0,
  total_accepted  INTEGER NOT NULL DEFAULT 0,
  total_value     DECIMAL(12,2) NOT NULL DEFAULT 0,
  
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  deleted_at      TIMESTAMPTZ                          -- soft delete
);

-- 4. Categorie prodotto
CREATE TABLE product_categories (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  company_id      UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  name            TEXT NOT NULL,                         -- "Profili PVC", "Vetri", "Accessori"
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
  
  name            TEXT NOT NULL,                         -- "Rehau Brillant Design 70"
  sku             TEXT,                                  -- codice interno serramentista
  description     TEXT,
  supplier        TEXT,                                  -- fornitore (Rehau, Schüco, Aluplast...)
  
  unit            TEXT NOT NULL DEFAULT 'mq'             -- mq, ml, pz
                  CHECK (unit IN ('mq', 'ml', 'pz')),
  tier            TEXT NOT NULL                          -- fascia prezzo
                  CHECK (tier IN ('base', 'medio', 'top')),
  price           DECIMAL(10,2) NOT NULL,               -- prezzo per unità
  
  -- Regole applicazione automatica (quale prodotto si applica a quale tipo finestra)
  applies_to      TEXT[] DEFAULT ARRAY['battente','scorrevole','vasistas','portafinestra'],
  
  is_active       BOOLEAN NOT NULL DEFAULT true,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 6. Voci extra preimpostate
CREATE TABLE extra_presets (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  company_id      UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  
  name            TEXT NOT NULL,                         -- "Posa in opera", "Smaltimento", "Ponteggio"
  description     TEXT,
  default_price   DECIMAL(10,2) NOT NULL DEFAULT 0,
  unit            TEXT NOT NULL DEFAULT 'pz'
                  CHECK (unit IN ('pz', 'mq', 'ml', 'ora', 'forfait')),
  is_active       BOOLEAN NOT NULL DEFAULT true,
  sort_order      INTEGER NOT NULL DEFAULT 0,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 7. Preventivi
CREATE TABLE quotes (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  company_id      UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  customer_id     UUID REFERENCES customers(id) ON DELETE SET NULL,
  
  -- Numerazione
  number          TEXT NOT NULL,                         -- "SER-2026-0001"
  year            INTEGER NOT NULL DEFAULT EXTRACT(YEAR FROM NOW()),
  
  -- Stato
  status          TEXT NOT NULL DEFAULT 'draft'
                  CHECK (status IN ('draft','ready','sent','viewed','accepted','rejected','expired')),
  
  -- Importi (calcolati, snapshot al momento della generazione)
  subtotal_base   DECIMAL(12,2),
  subtotal_medio  DECIMAL(12,2),
  subtotal_top    DECIMAL(12,2),
  extras_total    DECIMAL(12,2) DEFAULT 0,
  margin_pct      DECIMAL(5,2) NOT NULL DEFAULT 25.00,
  total_base      DECIMAL(12,2),
  total_medio     DECIMAL(12,2),
  total_top       DECIMAL(12,2),
  
  -- Metadati
  notes           TEXT,                                  -- note interne serramentista
  customer_notes  TEXT,                                  -- note per il cliente sul PDF
  pdf_url         TEXT,                                  -- URL Supabase Storage
  pdf_generated_at TIMESTAMPTZ,
  
  -- Date
  sent_at         TIMESTAMPTZ,
  viewed_at       TIMESTAMPTZ,                          -- V2: tracking apertura
  responded_at    TIMESTAMPTZ,                          -- data accettazione/rifiuto
  expires_at      TIMESTAMPTZ,
  
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 8. Finestre rilevate
CREATE TABLE windows (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  quote_id        UUID NOT NULL REFERENCES quotes(id) ON DELETE CASCADE,
  
  position        INTEGER NOT NULL,                      -- ordine nella sessione (1, 2, 3...)
  label           TEXT,                                  -- "Cucina", "Camera matrimoniale"
  
  -- Misure (in millimetri)
  width_mm        DECIMAL(7,1) NOT NULL,
  height_mm       DECIMAL(7,1) NOT NULL,
  area_mq         DECIMAL(8,4) GENERATED ALWAYS AS (
                    (width_mm * height_mm) / 1000000.0
                  ) STORED,
  
  -- Classificazione AI
  window_type     TEXT NOT NULL DEFAULT 'battente'
                  CHECK (window_type IN ('battente','scorrevole','vasistas','portafinestra','fisso','altro')),
  ai_confidence   TEXT DEFAULT 'media'
                  CHECK (ai_confidence IN ('alta','media','bassa')),
  manually_adjusted BOOLEAN NOT NULL DEFAULT false,     -- se il serramentista ha corretto le misure
  
  -- Media
  photo_url       TEXT,                                  -- foto originale
  voice_note_url  TEXT,                                  -- nota vocale
  voice_transcript TEXT,                                 -- trascrizione Whisper
  
  -- Risposta AI raw (per debug e miglioramento)
  ai_response_raw JSONB,
  
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 9. Righe prodotto nel preventivo
CREATE TABLE line_items (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  quote_id        UUID NOT NULL REFERENCES quotes(id) ON DELETE CASCADE,
  window_id       UUID REFERENCES windows(id) ON DELETE CASCADE,
  product_id      UUID REFERENCES products(id) ON DELETE SET NULL,
  
  -- Snapshot del prodotto al momento del preventivo (i prezzi possono cambiare)
  product_name    TEXT NOT NULL,
  product_tier    TEXT NOT NULL CHECK (product_tier IN ('base','medio','top')),
  product_unit    TEXT NOT NULL,
  
  quantity        DECIMAL(10,3) NOT NULL,               -- mq, ml o pezzi
  unit_price      DECIMAL(10,2) NOT NULL,               -- prezzo unitario (snapshot)
  total_price     DECIMAL(10,2) NOT NULL,               -- quantità × prezzo
  
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

-- 11. Sessioni bot (state machine)
CREATE TABLE bot_sessions (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  company_id      UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  telegram_chat_id BIGINT NOT NULL UNIQUE,
  
  -- State machine
  state           TEXT NOT NULL DEFAULT 'idle'
                  CHECK (state IN (
                    'idle',
                    'awaiting_customer',        -- attende nome/indirizzo cliente
                    'awaiting_photo',           -- attende foto finestra
                    'confirming_measures',      -- mostra misure, attende conferma
                    'selecting_products',       -- selezione catalogo
                    'selecting_extras',         -- selezione voci extra
                    'adjusting_margin',         -- regolazione margine
                    'confirming_quote'          -- conferma finale
                  )),
  
  -- Contesto sessione corrente
  current_quote_id UUID REFERENCES quotes(id) ON DELETE SET NULL,
  state_data       JSONB NOT NULL DEFAULT '{}',         -- dati temporanei (es. finestra in lavorazione)
  
  -- Tracking
  last_activity_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  session_timeout  INTERVAL NOT NULL DEFAULT '2 hours',
  
  updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 12. Activity log (audit trail)
CREATE TABLE activity_log (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  company_id      UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  
  entity_type     TEXT NOT NULL,                         -- 'quote', 'customer', 'product'
  entity_id       UUID NOT NULL,
  action          TEXT NOT NULL,                         -- 'created', 'updated', 'sent', 'accepted'
  details         JSONB DEFAULT '{}',                    -- dettagli azione
  source          TEXT NOT NULL DEFAULT 'bot'            -- 'bot' o 'dashboard'
                  CHECK (source IN ('bot', 'dashboard', 'system')),
  
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### 4.3 Trigger e funzioni

```sql
-- Auto-update updated_at
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Applicare a tutte le tabelle con updated_at
CREATE TRIGGER trg_companies_updated BEFORE UPDATE ON companies
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_customers_updated BEFORE UPDATE ON customers
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_products_updated BEFORE UPDATE ON products
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_quotes_updated BEFORE UPDATE ON quotes
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_bot_sessions_updated BEFORE UPDATE ON bot_sessions
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- Aggiorna statistiche cliente quando un preventivo cambia stato
CREATE OR REPLACE FUNCTION update_customer_stats()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.customer_id IS NOT NULL THEN
    UPDATE customers SET
      total_quotes = (SELECT COUNT(*) FROM quotes WHERE customer_id = NEW.customer_id AND status != 'draft'),
      total_accepted = (SELECT COUNT(*) FROM quotes WHERE customer_id = NEW.customer_id AND status = 'accepted'),
      total_value = COALESCE((SELECT SUM(total_top) FROM quotes WHERE customer_id = NEW.customer_id AND status = 'accepted'), 0)
    WHERE id = NEW.customer_id;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_quote_stats AFTER INSERT OR UPDATE OF status ON quotes
  FOR EACH ROW EXECUTE FUNCTION update_customer_stats();

-- Genera numero preventivo progressivo
CREATE OR REPLACE FUNCTION generate_quote_number(p_company_id UUID)
RETURNS TEXT AS $$
DECLARE
  v_prefix TEXT;
  v_year INTEGER;
  v_count INTEGER;
BEGIN
  SELECT quote_prefix INTO v_prefix FROM company_settings WHERE company_id = p_company_id;
  v_year := EXTRACT(YEAR FROM NOW());
  SELECT COUNT(*) + 1 INTO v_count FROM quotes
    WHERE company_id = p_company_id AND year = v_year;
  RETURN v_prefix || '-' || v_year || '-' || LPAD(v_count::TEXT, 4, '0');
END;
$$ LANGUAGE plpgsql;

-- Seed voci extra default per nuova azienda
CREATE OR REPLACE FUNCTION seed_new_company()
RETURNS TRIGGER AS $$
BEGIN
  -- Settings
  INSERT INTO company_settings (company_id) VALUES (NEW.id);
  
  -- Voci extra standard
  INSERT INTO extra_presets (company_id, name, default_price, unit, sort_order) VALUES
    (NEW.id, 'Posa in opera',     0, 'pz', 1),
    (NEW.id, 'Smaltimento vecchi', 0, 'pz', 2),
    (NEW.id, 'Ponteggio',         0, 'forfait', 3),
    (NEW.id, 'Trasferta',         0, 'forfait', 4),
    (NEW.id, 'Controtelaio',      0, 'pz', 5);
  
  -- Categorie default
  INSERT INTO product_categories (company_id, name, sort_order) VALUES
    (NEW.id, 'Profili',    1),
    (NEW.id, 'Vetri',      2),
    (NEW.id, 'Accessori',  3);
    
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_seed_company AFTER INSERT ON companies
  FOR EACH ROW EXECUTE FUNCTION seed_new_company();
```

### 4.4 Indici

```sql
CREATE INDEX idx_customers_company     ON customers(company_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_customers_search      ON customers(company_id, name);
CREATE INDEX idx_products_company_tier ON products(company_id, tier) WHERE is_active = true;
CREATE INDEX idx_products_category     ON products(category_id) WHERE is_active = true;
CREATE INDEX idx_quotes_company        ON quotes(company_id);
CREATE INDEX idx_quotes_status         ON quotes(company_id, status);
CREATE INDEX idx_quotes_customer       ON quotes(customer_id);
CREATE INDEX idx_quotes_number         ON quotes(company_id, year, number);
CREATE INDEX idx_windows_quote         ON windows(quote_id);
CREATE INDEX idx_line_items_quote      ON line_items(quote_id);
CREATE INDEX idx_line_items_window     ON line_items(window_id);
CREATE INDEX idx_bot_sessions_chat     ON bot_sessions(telegram_chat_id);
CREATE INDEX idx_activity_entity       ON activity_log(company_id, entity_type, entity_id);
CREATE INDEX idx_activity_date         ON activity_log(company_id, created_at DESC);
```

### 4.5 RLS Policies

```sql
-- Pattern: ogni tabella ha la stessa regola base
-- "un'azienda vede solo i propri dati"

ALTER TABLE companies ENABLE ROW LEVEL SECURITY;
CREATE POLICY "companies_own" ON companies
  FOR ALL USING (id = auth.uid());

ALTER TABLE company_settings ENABLE ROW LEVEL SECURITY;
CREATE POLICY "settings_own" ON company_settings
  FOR ALL USING (company_id = auth.uid());

-- Pattern ripetuto per tutte le tabelle con company_id:
-- customers, product_categories, products, extra_presets,
-- quotes, bot_sessions, activity_log

-- Per le tabelle figlie (windows, line_items, quote_extras):
-- join con quotes per verificare il company_id
ALTER TABLE windows ENABLE ROW LEVEL SECURITY;
CREATE POLICY "windows_own" ON windows
  FOR ALL USING (
    quote_id IN (SELECT id FROM quotes WHERE company_id = auth.uid())
  );

-- Stessa logica per line_items e quote_extras
```

### 4.6 Storage buckets

```sql
-- Supabase Storage
INSERT INTO storage.buckets (id, name, public) VALUES
  ('logos',  'logos',  true),   -- logo azienda, pubblico per PDF
  ('photos', 'photos', false),  -- foto finestre, privato
  ('pdfs',   'pdfs',   false),  -- PDF preventivi, privato
  ('voices', 'voices', false);  -- note vocali, privato

-- Policy: ogni azienda accede solo alla propria cartella
-- Path convention: {bucket}/{company_id}/{filename}
```

---

## 5. Pipeline AI Vision

### 5.1 Flusso di elaborazione foto

```
Foto da Telegram (JPG, fino a 20MB)
        │
        ▼
┌──────────────────────┐
│  1. PRE-PROCESSING   │
│  ─ Resize max 2048px │  (Pillow)
│  ─ Compress quality  │
│  ─ EXIF orientation  │
│  ─ Salva su Storage  │
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│  2. AI ANALYSIS      │
│  ─ GPT-4o Vision     │
│  ─ Prompt strutturato│
│  ─ Output JSON       │
│  ─ Validazione Pydan │
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│  3. POST-PROCESSING  │
│  ─ Confidence check  │
│  ─ Range validation  │
│  ─ Salva risultato   │
│  ─ Feedback utente   │
└──────────────────────┘
```

### 5.2 Prompt GPT-4o Vision

```python
VISION_SYSTEM_PROMPT = """
Sei un sistema di visione artificiale specializzato nella misurazione di finestre.
Rispondi SOLO con JSON valido, mai con testo.
"""

VISION_USER_PROMPT = """
Questa foto mostra una finestra con un marker di calibrazione incollato sul vetro.

## Il Marker
- Quadrato bianco con 4 cerchi neri agli angoli
- QR code al centro
- Dimensione reale: {marker_size_mm}mm × {marker_size_mm}mm
- Usalo come riferimento di scala per calcolare le dimensioni della finestra

## Istruzioni
1. LOCALIZZA il marker nella foto (identifica i 4 cerchi angolari)
2. CALCOLA la matrice di trasformazione prospettica dai 4 angoli del marker
3. MISURA larghezza e altezza della finestra IN MILLIMETRI usando il marker come scala
4. IDENTIFICA il tipo di apertura della finestra
5. VALUTA la tua confidenza nella misurazione

## Output richiesto (JSON)
{
  "marker_detected": boolean,
  "marker_corners_visible": integer (0-4),
  "width_mm": number,
  "height_mm": number,
  "window_type": "battente" | "scorrevole" | "vasistas" | "portafinestra" | "fisso" | "altro",
  "confidence": "alta" | "media" | "bassa",
  "confidence_reason": "string",
  "suggestions": "string (suggerimenti per foto migliore, se confidence bassa)"
}

Se il marker NON è rilevato:
{
  "marker_detected": false,
  "error": "string (motivo: non visibile, troppo piccolo, foto sfocata...)",
  "suggestions": "string (come rifare la foto)"
}
"""
```

### 5.3 Validazione e fallback

```python
# Pydantic model per validare la risposta AI
class VisionResult(BaseModel):
    marker_detected: bool
    marker_corners_visible: int = Field(ge=0, le=4)
    width_mm: float = Field(ge=200, le=6000)    # finestre: 20cm-6m
    height_mm: float = Field(ge=200, le=4000)   # finestre: 20cm-4m
    window_type: Literal['battente','scorrevole','vasistas','portafinestra','fisso','altro']
    confidence: Literal['alta','media','bassa']
    confidence_reason: str = ""
    suggestions: str = ""

class VisionError(BaseModel):
    marker_detected: Literal[False]
    error: str
    suggestions: str = ""

# Strategia di fallback
FALLBACK_CHAIN = [
    # 1. Riprova con prompt semplificato
    # 2. Chiedi al serramentista di rifare la foto
    # 3. Inserimento manuale: "Inserisci larghezza in cm:" → "Inserisci altezza in cm:"
]

# Parametri API
VISION_CONFIG = {
    "model": "gpt-4o",
    "max_tokens": 400,        # risposta JSON breve
    "temperature": 0.1,        # output deterministico
    "timeout_seconds": 30,
    "max_retries": 2,
    "retry_delay_seconds": 3,
}
```

### 5.4 Trascrizione vocale

```python
WHISPER_CONFIG = {
    "model": "whisper-1",
    "language": "it",          # forza italiano
    "response_format": "text",
    "max_audio_duration": 120, # 2 minuti max
    "timeout_seconds": 20,
}

# Telegram invia audio come .ogg (Opus codec)
# Whisper accetta .ogg nativamente → nessuna conversione necessaria
```

---

## 6. Architettura Bot Telegram

### 6.1 Struttura cartelle

```
src/bot/
├── main.py                     # Entry point: registra handlers, avvia polling/webhook
├── config.py                   # Settings con pydantic-settings
├── handlers/
│   ├── __init__.py
│   ├── start.py                # /start — collegamento account
│   ├── new_quote.py            # /nuovo — avvia sessione preventivo
│   ├── photo.py                # Ricezione foto → analisi AI
│   ├── voice.py                # Ricezione vocale → Whisper
│   ├── products.py             # Selezione prodotti (inline keyboards)
│   ├── extras.py               # Selezione voci extra
│   ├── margin.py               # Regolazione margine
│   ├── confirm.py              # Conferma e generazione PDF
│   ├── commands.py             # /stato, /annulla, /help
│   └── errors.py               # Handler errori globale
├── services/
│   ├── __init__.py
│   ├── vision.py               # GPT-4o Vision → VisionResult
│   ├── transcription.py        # Whisper → testo
│   ├── pdf_generator.py        # Jinja2 + WeasyPrint → PDF
│   ├── quote_service.py        # CRUD preventivi su Supabase
│   ├── customer_service.py     # CRUD clienti
│   ├── session_service.py      # State machine bot_sessions
│   ├── catalog_service.py      # Lettura catalogo prodotti
│   └── storage_service.py      # Upload/download da Supabase Storage
├── models/
│   ├── __init__.py
│   ├── vision.py               # VisionResult, VisionError
│   ├── session.py              # SessionState, StateData
│   └── quote.py                # QuoteData, WindowData
├── utils/
│   ├── __init__.py
│   ├── keyboards.py            # Builder per InlineKeyboardMarkup
│   ├── messages.py             # Testi messaggi bot (i18n ready)
│   └── formatters.py           # Formattazione moneta, misure, date
├── templates/
│   └── quote.html              # Template Jinja2 per PDF preventivo
├── .env.example
└── requirements.txt
```

### 6.2 State Machine dettagliata

```
                    ┌──────────┐
         ┌─────────│   IDLE   │◄──────────────────────────┐
         │         └────┬─────┘                           │
         │              │ /nuovo                          │
         │              ▼                                  │
         │    ┌──────────────────┐                        │
         │    │ AWAITING_CUSTOMER│ ← nome/indirizzo       │
         │    └────────┬─────────┘                        │
         │             │ cliente inserito                  │
         │             ▼                                   │
    /annulla  ┌──────────────────┐◄──────────────┐       │
         │    │  AWAITING_PHOTO  │               │       │
         │    │  "Scatta foto    │               │       │
         │    │   finestra N"    │               │       │
         │    └────────┬─────────┘               │       │
         │             │ foto ricevuta            │       │
         │             ▼                          │       │
         │    ┌──────────────────┐               │       │
         │    │ CONFIRMING_      │    ✏️ correggi │       │
         │    │ MEASURES         │───────────────┘       │
         │    │ "120×140cm ok?"  │                        │
         │    └──┬───────────┬───┘                        │
         │       │ ✅ sì     │ "chiudi"                   │
         │       │           ▼                            │
         │       │  ┌──────────────────┐                  │
         │       │  │ SELECTING_       │                  │
         │       │  │ PRODUCTS         │                  │
         │       │  │ [Base][Medio]    │                  │
         │       │  │ [Top]            │                  │
         │       │  └────────┬─────────┘                  │
         │       │           │ prodotti scelti             │
         │       │           ▼                            │
         │       │  ┌──────────────────┐                  │
         │       ▼  │ SELECTING_EXTRAS │                  │
         │  (loop)  │ [Posa][Smalt.]   │                  │
         │          │ [Pont.][Fine]    │                  │
         │          └────────┬─────────┘                  │
         │                   │ "fine"                      │
         │                   ▼                            │
         │          ┌──────────────────┐                  │
         │          │ ADJUSTING_MARGIN │                  │
         │          │ "Margine: 25%"   │                  │
         │          │ [20%][25%][30%]  │                  │
         │          │ [Personalizza]   │                  │
         │          └────────┬─────────┘                  │
         │                   │ margine confermato          │
         │                   ▼                            │
         │          ┌──────────────────┐                  │
         │          │ CONFIRMING_QUOTE │                  │
         │          │ Riepilogo totale │                  │
         │          │ [✅ Genera PDF]  │                  │
         │          │ [✏️ Modifica]    │                  │
         │          └────────┬─────────┘                  │
         │                   │ ✅ conferma                │
         │                   ▼                            │
         │          ┌──────────────────┐                  │
         └─────────▶│   IDLE           │──────────────────┘
                    │ PDF generato ✅   │
                    └──────────────────┘
```

### 6.3 Gestione sessione (session_service.py)

```python
class SessionManager:
    """
    La sessione vive TUTTA su Supabase, mai in memoria.
    Se il bot crasha/riavvia, la sessione si riprende automaticamente.
    
    Timeout: sessione scade dopo 2 ore di inattività.
    Il serramentista può riprendere con /nuovo (la bozza resta nel DB).
    """
    
    async def get_or_create(self, chat_id: int) -> BotSession:
        """Recupera sessione attiva o ne crea una nuova."""
        
    async def transition(self, chat_id: int, new_state: str, state_data: dict = None):
        """Transizione atomica di stato con validazione."""
        
    async def reset(self, chat_id: int):
        """Reset a idle (su /annulla o timeout)."""
        
    async def cleanup_expired(self):
        """Pulizia sessioni scadute (cron ogni 30 min)."""
```

### 6.4 Messaggi bot (estratti chiave)

```python
MESSAGES = {
    "welcome": (
        "🪟 **Benvenuto in Serramentista!**\n\n"
        "Sono il tuo assistente per i preventivi.\n"
        "Per iniziare, collega il tuo account con il comando:\n"
        "/connect {token}\n\n"
        "Il token lo trovi nella dashboard web, sezione Impostazioni."
    ),
    "new_quote": (
        "📋 **Nuovo preventivo**\n\n"
        "Per chi è il preventivo?\n"
        "Scrivi _nome e indirizzo_ del cliente.\n\n"
        "Esempio: `Mario Rossi, Via Roma 12, Milano`"
    ),
    "awaiting_photo": (
        "📸 **Finestra {n}**\n\n"
        "Incolla il marker sul vetro e scatta la foto.\n\n"
        "💡 _Consigli per foto migliori:_\n"
        "• Inquadra tutta la finestra\n"
        "• Il marker deve essere ben visibile\n"
        "• Evita controluce forte\n\n"
        "Puoi anche inviare una 🎤 nota vocale per aggiungere dettagli."
    ),
    "measures_result": (
        "📐 **Finestra {n} rilevata**\n\n"
        "Tipo: {window_type}\n"
        "Larghezza: **{width_cm} cm**\n"
        "Altezza: **{height_cm} cm**\n"
        "Area: {area_mq} m²\n"
        "Confidenza: {confidence}\n\n"
        "{notes}"
    ),
}
```

---

## 7. Dashboard Web

### 7.1 Struttura cartelle (feature-based)

```
src/web/
├── src/
│   ├── app/
│   │   ├── router.tsx              # Route configuration
│   │   ├── App.tsx                 # Root component
│   │   └── main.tsx                # Entry point
│   ├── features/
│   │   ├── auth/
│   │   │   ├── LoginPage.tsx
│   │   │   ├── RegisterPage.tsx
│   │   │   ├── useAuth.ts
│   │   │   └── authService.ts
│   │   ├── dashboard/
│   │   │   ├── DashboardPage.tsx   # KPI cards + grafici
│   │   │   ├── StatsCard.tsx
│   │   │   ├── RecentQuotes.tsx
│   │   │   └── useDashboardStats.ts
│   │   ├── quotes/
│   │   │   ├── QuotesPage.tsx      # Lista con filtri e ricerca
│   │   │   ├── QuoteDetailPage.tsx # Dettaglio con finestre + PDF
│   │   │   ├── QuoteCard.tsx
│   │   │   ├── QuoteStatusBadge.tsx
│   │   │   ├── WindowCard.tsx
│   │   │   ├── useQuotes.ts
│   │   │   └── quoteService.ts
│   │   ├── customers/
│   │   │   ├── CustomersPage.tsx   # Lista + ricerca
│   │   │   ├── CustomerDetailPage.tsx
│   │   │   ├── CustomerForm.tsx
│   │   │   ├── useCustomers.ts
│   │   │   └── customerService.ts
│   │   ├── catalog/
│   │   │   ├── CatalogPage.tsx     # Prodotti per categoria e tier
│   │   │   ├── ProductForm.tsx
│   │   │   ├── CategoryManager.tsx
│   │   │   ├── TierPriceTable.tsx
│   │   │   ├── useCatalog.ts
│   │   │   └── catalogService.ts
│   │   └── settings/
│   │       ├── SettingsPage.tsx     # Tab: Profilo | Preventivo | Telegram
│   │       ├── CompanyProfileForm.tsx
│   │       ├── QuoteSettingsForm.tsx
│   │       ├── TelegramConnect.tsx
│   │       ├── ExtraPresetsManager.tsx
│   │       ├── useSettings.ts
│   │       └── settingsService.ts
│   ├── components/
│   │   ├── layout/
│   │   │   ├── AppLayout.tsx       # Sidebar + Header + Content
│   │   │   ├── Sidebar.tsx
│   │   │   └── Header.tsx
│   │   └── ui/                     # Componenti generici riusabili
│   │       ├── Button.tsx
│   │       ├── Input.tsx
│   │       ├── Select.tsx
│   │       ├── Badge.tsx
│   │       ├── Card.tsx
│   │       ├── Modal.tsx
│   │       ├── Table.tsx
│   │       ├── EmptyState.tsx
│   │       ├── LoadingSpinner.tsx
│   │       └── ConfirmDialog.tsx
│   ├── lib/
│   │   ├── supabase.ts             # Client singleton
│   │   ├── queryClient.ts          # TanStack Query config
│   │   └── utils.ts                # cn(), formatCurrency(), formatDate()
│   ├── store/
│   │   └── authStore.ts            # Zustand: user + company + settings
│   └── types/
│       └── index.ts                # Tipi TypeScript condivisi
├── public/
│   └── favicon.svg
├── index.html
├── package.json
├── vite.config.ts
├── tsconfig.json
├── tailwind.config.ts
└── vercel.json
```

### 7.2 Routing

```typescript
const routes = [
  { path: "/login",    element: <LoginPage /> },
  { path: "/register", element: <RegisterPage /> },
  {
    path: "/",
    element: <ProtectedLayout />,  // redirect a /login se non autenticato
    children: [
      { index: true,          element: <DashboardPage /> },
      { path: "quotes",       element: <QuotesPage /> },
      { path: "quotes/:id",   element: <QuoteDetailPage /> },
      { path: "customers",    element: <CustomersPage /> },
      { path: "customers/:id",element: <CustomerDetailPage /> },
      { path: "catalog",      element: <CatalogPage /> },
      { path: "settings",     element: <SettingsPage /> },
    ]
  }
];
```

### 7.3 Design System

```css
/* Palette — professionale, moderna, pensata per artigiani */
--primary:       #2563EB;    /* Blu lavoro — affidabile */
--primary-light: #DBEAFE;
--primary-dark:  #1D4ED8;
--success:       #059669;    /* Verde — accettato */
--warning:       #D97706;    /* Ambra — in attesa */
--danger:        #DC2626;    /* Rosso — rifiutato */
--neutral-900:   #0F172A;    /* Testo principale */
--neutral-600:   #475569;    /* Testo secondario */
--neutral-200:   #E2E8F0;    /* Bordi */
--neutral-50:    #F8FAFC;    /* Background */
--surface:       #FFFFFF;    /* Card, modali */

/* Tipografia */
font-family: 'Inter', system-ui, -apple-system, sans-serif;
/* H1: 28px/700 — titoli pagina */
/* H2: 20px/600 — sezioni */
/* H3: 16px/600 — card title */
/* Body: 14px/400 — testo */
/* Small: 12px/400 — metadata, label */

/* Spacing scale */
--space-1: 4px;   --space-2: 8px;   --space-3: 12px;
--space-4: 16px;  --space-5: 20px;  --space-6: 24px;
--space-8: 32px;  --space-10: 40px; --space-12: 48px;

/* Border radius */
--radius-sm: 6px;  --radius-md: 8px;  --radius-lg: 12px;

/* Shadows */
--shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
--shadow-md: 0 4px 6px rgba(0,0,0,0.07);
```

### 7.4 Dashboard KPI

```
┌─────────────────────────────────────────────────────────┐
│  🪟 Serramentista          [Rossi Serramenti]  [👤 SC] │
├──────────┬──────────────────────────────────────────────┤
│          │                                              │
│ 📊 Home  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌──────┐ │
│ 📄 Prev. │  │ 23     │ │ 8      │ │ €45.2K │ │ 35%  │ │
│ 👥 Clien.│  │ Totali │ │ Aperti │ │ Valore │ │ Conv.│ │
│ 📦 Catal.│  └────────┘ └────────┘ └────────┘ └──────┘ │
│ ⚙️ Impost│                                              │
│          │  [═══════════ Grafico ultimi 30gg ═════════] │
│          │                                              │
│          │  Ultimi preventivi                           │
│          │  ┌─────────────────────────────────────────┐ │
│          │  │ SER-2026-0023 ● Inviato                │ │
│          │  │ Mario Rossi · 5 finestre · €3.240      │ │
│          │  ├─────────────────────────────────────────┤ │
│          │  │ SER-2026-0022 ● Accettato              │ │
│          │  │ Anna Bianchi · 3 finestre · €1.890     │ │
│          │  └─────────────────────────────────────────┘ │
└──────────┴──────────────────────────────────────────────┘
```

---

## 8. Generazione PDF

### 8.1 Layout del preventivo

```
┌──────────────────────────────────────────────────────────┐
│  [LOGO AZIENDA]                                          │
│  Rossi Serramenti S.r.l.                                 │
│  Via dell'Artigianato 15, Montella (AV)                 │
│  P.IVA: 01234567890 · Tel: +39 0827 123456             │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  PREVENTIVO N° SER-2026-0023            25/03/2026      │
│  Validità: 30 giorni                                     │
│                                                          │
│  Cliente: Mario Rossi                                    │
│  Indirizzo: Via Roma 12, 20121 Milano (MI)              │
│                                                          │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  RIEPILOGO FINESTRE                                      │
│  ┌────┬──────────────┬──────────┬───────┬──────────┐    │
│  │ #  │ Tipo         │ Misure   │ Area  │ Note     │    │
│  ├────┼──────────────┼──────────┼───────┼──────────┤    │
│  │ 1  │ Battente     │ 120×140  │ 1.68  │ Cucina   │    │
│  │ 2  │ Portafinestra│ 180×220  │ 3.96  │ Salone   │    │
│  │ 3  │ Vasistas     │  60× 40  │ 0.24  │ Bagno    │    │
│  └────┴──────────────┴──────────┴───────┴──────────┘    │
│                                                          │
│  OPZIONI PRODOTTO                                        │
│  ┌──────────────┬──────────┬──────────┬──────────┐      │
│  │              │  BASE    │  MEDIO   │   TOP    │      │
│  ├──────────────┼──────────┼──────────┼──────────┤      │
│  │ Profili      │  €1.200  │  €1.680  │  €2.100  │      │
│  │ Vetri        │    €480  │    €720  │    €960  │      │
│  │ Accessori    │    €180  │    €240  │    €320  │      │
│  ├──────────────┼──────────┼──────────┼──────────┤      │
│  │ Subtotale    │  €1.860  │  €2.640  │  €3.380  │      │
│  └──────────────┴──────────┴──────────┴──────────┘      │
│                                                          │
│  VOCI AGGIUNTIVE                                         │
│  Posa in opera ..................... €450                │
│  Smaltimento vecchi infissi ....... €200                │
│                                                          │
│  ┌──────────────┬──────────┬──────────┬──────────┐      │
│  │ TOTALE       │ €2.510   │ €3.290   │ €4.030   │      │
│  │ (IVA 22%)    │ €3.062   │ €4.014   │ €4.917   │      │
│  └──────────────┴──────────┴──────────┴──────────┘      │
│                                                          │
│  Note: [eventuali note del serramentista]                │
│                                                          │
├──────────────────────────────────────────────────────────┤
│  Rossi Serramenti · rossi@email.it · +39 0827 123456   │
│  Preventivo generato con Serramentista by Poonto        │
└──────────────────────────────────────────────────────────┘
```

### 8.2 Implementazione

```python
# pdf_generator.py
class PDFGenerator:
    """
    Genera PDF preventivo usando Jinja2 + WeasyPrint.
    
    Il template HTML usa CSS @page per:
    - Formato A4
    - Margini 15mm
    - Header con logo
    - Footer con info azienda e numero pagina
    - Tabella multi-colonna per le 3 opzioni
    """
    
    def __init__(self, template_path: str = "templates/quote.html"):
        self.env = Environment(loader=FileSystemLoader(Path(template_path).parent))
        self.template = self.env.get_template(Path(template_path).name)
    
    async def generate(self, quote_data: QuoteRenderData) -> bytes:
        """
        1. Render HTML dal template Jinja2
        2. Scarica logo azienda da Supabase Storage (se presente)
        3. Converte HTML → PDF con WeasyPrint
        4. Ritorna bytes del PDF
        
        Tempo medio: 2-4 secondi
        """
        html = self.template.render(quote=quote_data)
        pdf_bytes = HTML(string=html).write_pdf()
        return pdf_bytes
    
    async def generate_and_upload(self, quote_data: QuoteRenderData) -> str:
        """Genera PDF e lo carica su Supabase Storage. Ritorna l'URL."""
        pdf_bytes = await self.generate(quote_data)
        path = f"{quote_data.company_id}/{quote_data.number}.pdf"
        url = await storage.upload("pdfs", path, pdf_bytes, "application/pdf")
        return url
```

---

## 9. Sicurezza e Multi-tenancy

### 9.1 Modello di isolamento

```
┌────────────────────────────────────┐
│       Supabase Row Level Security  │
│                                    │
│  Serramentista A    Serramentista B│
│  ┌──────────┐      ┌──────────┐   │
│  │ clienti  │      │ clienti  │   │
│  │ prodotti │      │ prodotti │   │
│  │ preventivi│      │ preventivi│  │
│  │ ...      │      │ ...      │   │
│  └──────────┘      └──────────┘   │
│                                    │
│  ⛔ A non può MAI vedere dati di B │
│  Garantito a livello database      │
└────────────────────────────────────┘
```

### 9.2 Checklist sicurezza

| Area | Misura | Stato |
|------|--------|-------|
| Autenticazione | Supabase Auth (bcrypt, JWT) | ✅ Built-in |
| Autorizzazione | RLS su ogni tabella | ✅ Schema |
| Bot ↔ DB | Service role key (bypassa RLS), validazione lato codice | ⚠️ Attenzione |
| API keys | Mai nel codice, solo env vars | ✅ Policy |
| Storage | Bucket privati con policy per company_id | ✅ Schema |
| HTTPS | Vercel (dashboard) + Railway (bot webhook) | ✅ Default |
| Rate limiting | python-telegram-bot built-in (30 msg/s) | ✅ Default |
| Input sanitization | Pydantic per AI, escape HTML per messaggi | Da implementare |
| Logging | Mai loggare token, password, dati personali | Policy |
| GDPR | Soft delete clienti, export dati, cancellazione account | V2 |

### 9.3 Bot security: il rischio service_role

Il bot usa `SUPABASE_SERVICE_ROLE_KEY` perché non ha un JWT utente (il serramentista interagisce via Telegram, non via web). Questo bypassa RLS.

**Mitigazione:**
```python
# OGNI query del bot DEVE filtrare per company_id
# MAI fare SELECT * senza filtro company_id

class SecureSupabaseClient:
    """Wrapper che forza il filtro company_id su ogni query."""
    
    def __init__(self, supabase_client, company_id: UUID):
        self.client = supabase_client
        self.company_id = company_id
    
    def from_table(self, table: str):
        return self.client.table(table).eq("company_id", str(self.company_id))
```

---

## 10. Flussi Operativi

### 10.1 Onboarding nuovo serramentista

```
1. Serramentista va su serramentista.poonto.it
2. Clicca "Registrati"
3. Inserisce: email, password, nome azienda, telefono
4. Supabase Auth crea l'utente
5. Trigger seed_new_company() crea: company_settings + extra_presets + product_categories
6. Redirect alla dashboard
7. Wizard onboarding (3 step):
   a. Completa profilo: P.IVA, indirizzo, logo
   b. Configura catalogo: almeno 1 prodotto per tier
   c. Collega Telegram: genera token → /connect sul bot
8. onboarding_completed = true
```

### 10.2 Flusso preventivo end-to-end (sequence diagram)

```
Serramentista          Bot               Supabase         OpenAI
     │                  │                    │               │
     │── /nuovo ───────▶│                    │               │
     │                  │── crea quote ─────▶│               │
     │                  │◀── quote_id ───────│               │
     │◀── "Per chi?" ──│                    │               │
     │                  │                    │               │
     │── "Mario Rossi  │                    │               │
     │    Via Roma 12" ▶│                    │               │
     │                  │── upsert customer ▶│               │
     │◀── "Scatta foto │                    │               │
     │     finestra 1" ─│                    │               │
     │                  │                    │               │
     │── [📸 foto] ────▶│                    │               │
     │                  │── upload foto ────▶│               │
     │                  │── analizza ───────────────────────▶│
     │                  │◀── {width, height, type} ─────────│
     │                  │── salva window ───▶│               │
     │◀── "120×140cm   │                    │               │
     │     battente ✅?" │                    │               │
     │                  │                    │               │
     │── ✅ ────────────▶│                    │               │
     │◀── "Foto finestra│                    │               │
     │     2 o chiudi" ─│                    │               │
     │                  │                    │               │
     │── "chiudi" ──────▶│                    │               │
     │                  │── leggi catalogo ─▶│               │
     │◀── [prodotti     │◀── products ──────│               │
     │     inline kbd] ─│                    │               │
     │── [selezione] ──▶│── crea line_items ▶│               │
     │                  │                    │               │
     │◀── "Voci extra?" │                    │               │
     │── [Posa][Smalt.] ▶│── crea extras ───▶│               │
     │── [Fine] ────────▶│                    │               │
     │                  │                    │               │
     │◀── "Margine 25%" │                    │               │
     │── "30%" ─────────▶│                    │               │
     │                  │                    │               │
     │◀── Riepilogo     │                    │               │
     │── ✅ Genera PDF ─▶│                    │               │
     │                  │── genera PDF ─────▶│ (WeasyPrint)  │
     │                  │── upload PDF ─────▶│               │
     │                  │── update quote ───▶│               │
     │◀── [📄 PDF] ─────│                    │               │
     │                  │                    │               │
```

### 10.3 Collegamento Telegram ↔ Dashboard

```
Dashboard                    Supabase              Bot Telegram
    │                            │                      │
    │── genera token UUID ──────▶│                      │
    │◀── token "abc-123-def" ───│                      │
    │                            │                      │
    │   Mostra: "Apri @SerrBot                         │
    │   e scrivi /connect abc-123-def"                 │
    │                            │                      │
    │                            │◀── /connect abc... ─│
    │                            │── verifica token    │
    │                            │── salva chat_id ───▶│
    │                            │                      │── "✅ Collegato!"
    │                            │                      │
    │── polling telegram_chat_id ▶│                      │
    │◀── chat_id presente ──────│                      │
    │   "✅ Bot connesso"        │                      │
```

---

## 11. Deploy e Infrastruttura

### 11.1 Ambienti

| Ambiente | Scopo | URL |
|---------|-------|-----|
| **Local** | Sviluppo | `localhost:5173` (web) + polling bot |
| **Preview** | Review PR | `pr-123.serramentista.vercel.app` |
| **Production** | Utenti reali | `serramentista.poonto.it` |

### 11.2 Deploy Bot (Railway)

```dockerfile
# Dockerfile
FROM python:3.12-slim

# WeasyPrint dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 \
    libffi-dev shared-mime-info && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY src/bot/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/bot/ .

CMD ["python", "main.py"]
```

```yaml
# railway.toml
[build]
  builder = "dockerfile"
  dockerfilePath = "Dockerfile"

[deploy]
  startCommand = "python main.py"
  healthcheckPath = "/health"
  healthcheckTimeout = 30
  restartPolicyType = "always"
```

### 11.3 Deploy Dashboard (Vercel)

```json
// vercel.json
{
  "buildCommand": "cd src/web && npm run build",
  "outputDirectory": "src/web/dist",
  "framework": "vite",
  "rewrites": [
    { "source": "/(.*)", "destination": "/index.html" }
  ]
}
```

### 11.4 Variabili ambiente

```bash
# === BOT (.env) ===
TELEGRAM_BOT_TOKEN=           # da @BotFather
OPENAI_API_KEY=               # per GPT-4o e Whisper
SUPABASE_URL=                 # https://xxx.supabase.co
SUPABASE_SERVICE_KEY=         # service_role (bypassa RLS)
BOT_MODE=webhook              # "webhook" in prod, "polling" in dev
WEBHOOK_URL=                  # https://xxx.up.railway.app/webhook
LOG_LEVEL=INFO

# === WEB (.env) ===
VITE_SUPABASE_URL=            # https://xxx.supabase.co
VITE_SUPABASE_ANON_KEY=       # anon key (RLS attiva)
VITE_APP_URL=                 # https://serramentista.poonto.it
```

---

## 12. Piano di Test

### 12.1 Livelli di test

| Livello | Cosa testa | Tool | Copertura target |
|---------|-----------|------|-----------------|
| Unit | Singole funzioni (formattatori, calcoli, validazione) | pytest + vitest | 80%+ |
| Integration | Servizi ↔ Supabase, AI ↔ validazione | pytest (fixtures Supabase) | Flussi critici |
| E2E Bot | Conversazione completa via Telegram Test API | pytest + python-telegram-bot mock | Happy path + errori |
| E2E Web | Navigazione dashboard completa | Playwright | Happy path |
| Manual | Qualità PDF, UX bot sul campo | Tester umano | Pre-release |

### 12.2 Test cases critici

```
T-001: Foto con marker visibile → misure corrette (±10mm)
T-002: Foto senza marker → errore chiaro + suggerimento
T-003: Foto sfocata → bassa confidenza + richiesta nuova foto
T-004: Preventivo 5 finestre → PDF con tutte le righe
T-005: Cambio margine → ricalcolo corretto su tutti i tier
T-006: Timeout sessione → sessione resettata, bozza salvata
T-007: Account A non vede dati account B (RLS)
T-008: /connect con token invalido → errore chiaro
T-009: PDF con logo aziendale → logo visibile nell'header
T-010: Nota vocale 90 secondi → trascrizione completa
```

### 12.3 Smoke test post-deploy

```bash
# 1. Health check bot
curl -s https://serramentista-bot.up.railway.app/health

# 2. Dashboard raggiungibile
curl -sL -w "%{http_code}" https://serramentista.poonto.it | tail -1

# 3. Supabase connesso
curl -s -H "apikey: $ANON_KEY" "$SUPABASE_URL/rest/v1/"

# 4. Bot risponde
# Invio /start al bot → deve rispondere entro 5 secondi
```

---

## 13. Decisioni Architetturali (ADR)

### ADR-001: Telegram Bot come interfaccia primaria

**Contesto:** Il serramentista è dal cliente, ha le mani occupate, non vuole installare nuove app.

| Opzione | Pro | Contro |
|---------|-----|--------|
| App nativa iOS/Android | UX completa, offline | Sviluppo 3×, App Store review, installazione |
| Telegram Bot | Zero installazione, foto native, condivisione facile | UX limitata a messaggi e inline keyboard |
| PWA | Installabile, offline | Permesso fotocamera limitato iOS, service worker complesso |

**Decisione:** Telegram Bot per il MVP. Dashboard web per le operazioni non urgenti (catalogo, CRM, settings).

**Conseguenze:** L'UX del bot deve essere impeccabile. Ogni messaggio deve essere chiaro, ogni inline keyboard intuitiva. Il bot è il prodotto — la dashboard è un complemento.

---

### ADR-002: GPT-4o Vision per analisi marker

**Contesto:** Serve analizzare foto con marker per calcolare dimensioni finestre.

| Opzione | Pro | Contro |
|---------|-----|--------|
| OpenCV + ArUco markers | Gratuito, veloce, offline | Richiede ArUco specifici, integrazione complessa |
| GPT-4o Vision | Flessibile, identifica anche tipo finestra, prompt-driven | €0.02/chiamata, latenza 2-5s, dipendenza API |
| YOLO custom | Veloce, offline | Training dataset costoso, manutenzione modello |

**Decisione:** GPT-4o Vision per MVP. Costo trascurabile a volume previsto (<100 preventivi/mese al lancio).

**Debito tecnico:** Valutare migrazione a OpenCV+ArUco in V2 se il volume cresce significativamente (TD-001).

---

### ADR-003: Railway per il bot (non Supabase Edge Functions)

**Contesto:** Dove hostare il processo bot Python?

| Opzione | Pro | Contro |
|---------|-----|--------|
| Railway | Container Docker, persistente, WeasyPrint funziona | $5-8/mese |
| Supabase Edge Functions | Gratis, integrato, scaling automatico | Deno (non Python), no WeasyPrint, cold start |
| Fly.io | Container Docker, generoso free tier | Networking più complesso |
| VPS Hetzner | Già ce l'abbiamo | Manutenzione, no auto-scaling, single point of failure |

**Decisione:** Railway. Container Docker sempre attivo, WeasyPrint funziona nativamente, deploy da GitHub push, logging integrato. $5/mese è accettabile.

---

### ADR-004: Separazione netta Bot ↔ Dashboard

**Contesto:** Bot e dashboard condividono logica? Monorepo? API intermedia?

**Decisione:** Due codebase separate che parlano allo stesso database Supabase. Nessuna API custom intermedia.

**Motivazione:**
- Il bot è Python, la dashboard è TypeScript/React — linguaggi diversi
- Supabase è già l'API — aggiungere un backend custom è overengineering
- Deploy indipendente: posso aggiornare il bot senza toccare la dashboard e viceversa
- Shared nothing: se il bot è down, la dashboard funziona e viceversa

---

### ADR-005: State machine su database (non in memoria)

**Contesto:** La sessione conversazionale del bot ha uno stato (idle → foto → prodotti → PDF). Dove lo conserviamo?

**Decisione:** Tabella `bot_sessions` su Supabase con colonna `state` e `state_data` (JSONB).

**Motivazione:**
- Se Railway riavvia il container → la sessione non si perde
- Se il serramentista chiude Telegram e riapre dopo un'ora → riprende da dove era
- Debug facile: posso ispezionare lo stato sul DB
- Sessioni miste bot/dashboard: la dashboard può mostrare "preventivo in corso" in tempo reale

---

## 14. Rischi e Mitigazione

| ID | Rischio | P | I | Mitigazione |
|----|---------|---|---|-------------|
| R-001 | GPT-4o non rileva marker in scarsa luce | Media | Alto | Fallback inserimento manuale + consigli foto nel messaggio + pre-processing (brightness/contrast) |
| R-002 | Precisione misure insufficiente (>5mm errore) | Media | Alto | Confidenza AI mostrata all'utente + possibilità correzione manuale + A/B test con misure reali |
| R-003 | WeasyPrint lento su Railway starter | Media | Medio | Messaggio "⏳ Sto generando il PDF..." + async generation + upgrade Railway se necessario |
| R-004 | Cold start Railway (bot non risponde) | Bassa | Alto | Keep-alive ping ogni 5 min via cron + Railway always-on ($5) |
| R-005 | Serramentista non completa l'onboarding | Alta | Alto | Wizard semplificato (3 step) + catalogo demo precaricato + video tutorial |
| R-006 | Costi OpenAI crescono con il volume | Bassa | Medio | Monitoraggio spesa mensile + alert >$50 + TD-001 (OpenCV) come piano B |
| R-007 | Telegram cambia API/limiti bot | Bassa | Alto | python-telegram-bot è mantenuto attivamente + webhook standard, nessuna API non documentata |
| R-008 | Supabase free tier esaurito | Media | Alto | Monitoring storage e row count + upgrade a Pro ($25/mese) quando necessario |

---

## 15. Milestone di Sviluppo

### M0 — Setup (Giorno 1)
- [  ] Repo GitHub `PoontoAgency/serramentista`
- [  ] Inizializzazione: bot Python + web React/Vite
- [  ] Supabase project + schema SQL + migrazioni
- [  ] Deploy test: Railway (bot echo) + Vercel (pagina vuota)
- [  ] CI: GitHub Actions (lint + typecheck + build)

**✅ Gate:** Bot risponde a /start, dashboard mostra login

### M1 — Auth + Onboarding (Giorni 2-4)
- [  ] Supabase Auth (email/password)
- [  ] Registrazione + login dashboard
- [  ] Wizard onboarding (profilo, catalogo, Telegram)
- [  ] Collegamento bot ↔ dashboard (/connect)
- [  ] Seed dati default (extra presets, categorie)

**✅ Gate:** Serramentista si registra, configura profilo, collega bot

### M2 — Core Bot: Foto → Misure (Giorni 5-9)
- [  ] State machine sessione su Supabase
- [  ] Flusso /nuovo → cliente → foto
- [  ] Integrazione GPT-4o Vision con prompt
- [  ] Validazione risposta AI (Pydantic)
- [  ] Fallback inserimento manuale
- [  ] Multi-finestra (loop foto)
- [  ] Note vocali Whisper
- [  ] /annulla e timeout sessione

**✅ Gate:** Sessione completa foto → misure → conferma per 3+ finestre

### M3 — Catalogo + Calcolo (Giorni 10-13)
- [  ] CRUD catalogo prodotti (dashboard)
- [  ] Categorie e tier (base/medio/top)
- [  ] Selezione prodotti inline nel bot
- [  ] Voci extra (presets + custom)
- [  ] Calcolo margine con riepilogo
- [  ] Conferma preventivo

**✅ Gate:** Preventivo completo con importi calcolati su 3 tier

### M4 — PDF + CRM (Giorni 14-17)
- [  ] Template PDF Jinja2 responsivo
- [  ] Generazione WeasyPrint + upload Storage
- [  ] Invio PDF via Telegram
- [  ] CRM clienti (lista, dettaglio, storico)
- [  ] Lista preventivi con filtri e ricerca
- [  ] Dettaglio preventivo con finestre
- [  ] Dashboard KPI (stats rapide)

**✅ Gate:** PDF professionale generato e inviato, CRM funzionante

### M5 — Polish + Beta (Giorni 18-22)
- [  ] Settings completo (profilo, logo, config preventivo)
- [  ] Extra presets personalizzabili
- [  ] Error handling robusto (bot + web)
- [  ] Loading states, empty states, toasts
- [  ] Responsività mobile dashboard
- [  ] Test con 3-5 serramentisti beta
- [  ] Bug fixing da feedback beta
- [  ] Deploy produzione

**✅ Gate:** Sistema stabile, 3+ serramentisti lo hanno usato con successo

---

## 16. Technical Debt Register

| ID | Descrizione | Severità | Target |
|----|-------------|----------|--------|
| TD-001 | Valutare migrazione da GPT-4o a OpenCV+ArUco per ridurre costi | Media | V2 |
| TD-002 | Paginazione liste (preventivi, clienti, prodotti) — ora carica tutto | Media | M5 |
| TD-003 | Caching immagini marker per preventivi multipli stessa finestra | Bassa | V2 |
| TD-004 | i18n messaggi bot (ora hardcoded in italiano) | Bassa | V3 |
| TD-005 | Rate limiting per account (max preventivi/giorno per piano) | Bassa | Lancio commerciale |
| TD-006 | Backup automatico dati Supabase | Media | Pre-lancio |
| TD-007 | Monitoring e alerting (uptime bot, errori AI, spesa OpenAI) | Media | M5 |

---

## 17. Convenzioni e Standard

### Naming

| Cosa | Convenzione | Esempio |
|------|------------|---------|
| File Python | snake_case | `quote_service.py` |
| Classi Python | PascalCase | `QuoteService` |
| File React | PascalCase per componenti | `QuoteCard.tsx` |
| Hook React | camelCase con `use` | `useQuotes.ts` |
| Tabelle DB | snake_case plurale | `line_items` |
| Colonne DB | snake_case | `company_id` |
| Branch Git | `feature/xxx`, `fix/xxx` | `feature/pdf-generation` |
| Commit | Conventional Commits | `feat(bot): add photo analysis` |

### Commit Messages

```
feat(bot): add GPT-4o vision photo analysis
fix(pdf): correct margin calculation in multi-tier layout
feat(web): implement catalog product CRUD
chore(deps): update supabase-py to 2.8.0
docs: update TDD with ADR-005
```

### Numerazione preventivi

`{PREFIX}-{ANNO}-{PROGRESSIVO}` → `SER-2026-0001`

- PREFIX configurabile per azienda (default: `SER`)
- Progressivo annuale, 4 cifre, per azienda
- Unicità garantita da `generate_quote_number()` su DB

### Struttura cartelle progetto

```
serramentista/
├── src/
│   ├── bot/                    # Python — Telegram Bot
│   ├── web/                    # React — Dashboard
│   └── supabase/
│       └── migrations/         # SQL versionate
│           ├── 001_schema.sql
│           ├── 002_rls.sql
│           ├── 003_triggers.sql
│           ├── 004_indexes.sql
│           ├── 005_seed.sql
│           └── 006_storage.sql
├── docs/
│   ├── TDD.md                  # Questo file
│   └── MARKER_SPECS.md         # Specifiche marker fisico
├── .github/
│   └── workflows/
│       ├── ci.yml              # Lint + test + build
│       └── deploy.yml          # Deploy su push a main
├── Dockerfile                  # Bot container
├── railway.toml
├── vercel.json
├── .gitignore
├── .env.example
└── README.md
```

---

*Fine TDD — Serramentista v1.0*
*25/03/2026 — Poonto Agency*
