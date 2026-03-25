# 📋 TASK BREAKDOWN — Serramentista

> Derivato dal TDD v1.0 — 25/03/2026
> Ogni task è atomico: una cosa alla volta, spuntabile.
> Aggiornare questo file ad ogni progresso.

---

## M0 — Setup (Giorno 1)

### Repo e struttura progetto
- [ ] Creare repo GitHub `PoontoAgency/serramentista` (privato)
- [ ] Creare struttura cartelle come da TDD §17 (`src/bot/`, `src/web/`, `src/supabase/`)
- [ ] Creare `.gitignore` (Python + Node + env + IDE)
- [ ] Creare `.env.example` (bot + web)
- [ ] Creare `README.md` con setup locale

### Bot Python — Bootstrap
- [ ] Creare `src/bot/requirements.txt` con tutte le dipendenze (§3.1)
- [ ] Creare `src/bot/config.py` (pydantic-settings, variabili env)
- [ ] Creare `src/bot/main.py` (entry point, echo bot funzionante)
- [ ] Creare struttura cartelle bot: `handlers/`, `services/`, `models/`, `utils/`, `templates/`
- [ ] Creare `__init__.py` per ogni package
- [ ] Verificare che il bot risponda a `/start` in locale (polling mode)

### Dashboard React — Bootstrap
- [ ] Inizializzare progetto Vite + React 19 + TypeScript in `src/web/`
- [ ] Installare dipendenze: Tailwind 4, React Router 7, Zustand 5, TanStack Query 5, supabase-js 2
- [ ] Installare dipendenze UI: Radix UI, Lucide React, Sonner, React Hook Form, Zod
- [ ] Creare struttura cartelle web: `features/`, `components/`, `lib/`, `store/`, `types/`
- [ ] Creare `src/web/src/lib/supabase.ts` (client singleton, placeholder URL)
- [ ] Creare `src/web/src/lib/queryClient.ts`
- [ ] Creare `src/web/src/lib/utils.ts` (`cn()`, `formatCurrency()`, `formatDate()`)
- [ ] Creare `vercel.json`
- [ ] Verificare che `npm run dev` funzioni e mostri pagina vuota

### Supabase — Setup
- [ ] Creare progetto Supabase (nota: segnaposto fino a progetto reale)
- [ ] Creare `src/supabase/migrations/001_schema.sql` — tutte le 12 tabelle (§4.2)
- [ ] Creare `src/supabase/migrations/002_rls.sql` — tutte le RLS policies (§4.5)
- [ ] Creare `src/supabase/migrations/003_triggers.sql` — trigger e funzioni (§4.3)
- [ ] Creare `src/supabase/migrations/004_indexes.sql` — indici (§4.4)
- [ ] Creare `src/supabase/migrations/005_seed.sql` — seed trigger per nuova azienda
- [ ] Creare `src/supabase/migrations/006_storage.sql` — bucket storage (§4.6)
- [ ] Eseguire migrazioni su Supabase (o verificare SQL valido)

### Deploy test
- [ ] Creare `Dockerfile` per bot (§11.2)
- [ ] Creare `railway.toml`
- [ ] Push iniziale su GitHub
- [ ] Deploy test bot su Railway (echo bot)
- [ ] Deploy test web su Vercel (pagina vuota)
- [ ] Verificare health check Railway

### CI/CD
- [ ] Creare `.github/workflows/ci.yml` — lint + typecheck + build (bot + web)
- [ ] Verificare che la CI passi su push

**✅ Gate M0:** Bot risponde a /start, dashboard mostra pagina vuota, CI verde

---

## M1 — Auth + Onboarding (Giorni 2-4)

### Supabase Auth
- [ ] Configurare Supabase Auth (email/password, conferma email disabilitata per MVP)
- [ ] Creare `src/web/src/store/authStore.ts` — Zustand (user + company + settings)
- [ ] Creare `src/web/src/types/index.ts` — tipi Company, CompanySettings, Customer, Product, Quote...

### Auth Frontend
- [ ] Creare componenti UI base: `Button`, `Input`, `Card`, `Badge`, `LoadingSpinner`
- [ ] Creare `AppLayout.tsx` (Sidebar + Header + Content)
- [ ] Creare `Sidebar.tsx` con navigazione (Home, Preventivi, Clienti, Catalogo, Impostazioni)
- [ ] Creare `Header.tsx` con nome azienda + avatar
- [ ] Creare `LoginPage.tsx` con form email/password
- [ ] Creare `RegisterPage.tsx` con form (email, password, nome azienda, telefono)
- [ ] Creare `src/web/src/features/auth/authService.ts` — signup, login, logout, getSession
- [ ] Creare `src/web/src/features/auth/useAuth.ts` — hook auth con redirect
- [ ] Creare `ProtectedLayout` wrapper (redirect a /login se non autenticato)
- [ ] Creare `router.tsx` con tutte le route (§7.2)
- [ ] Testare: registrazione → login → dashboard vuota → logout

### Onboarding Wizard
- [ ] Creare `OnboardingWizard.tsx` — 3 step con progress bar
- [ ] Step 1: `CompanyProfileForm.tsx` (P.IVA, indirizzo, logo upload)
- [ ] Step 2: Catalogo quick setup (almeno 1 prodotto per tier — o skip con demo data)
- [ ] Step 3: `TelegramConnect.tsx` (genera token, mostra istruzioni)
- [ ] Al completamento: `onboarding_completed = true`
- [ ] Se onboarding non completato → redirect a wizard

### Collegamento Telegram
- [ ] Creare `src/web/src/features/settings/TelegramConnect.tsx`
- [ ] Generare `telegram_token` (UUID) e salvarlo su `companies`
- [ ] Mostrare istruzioni: "Apri @SerrBot e invia /connect {token}"
- [ ] Polling per verificare `telegram_chat_id` presente
- [ ] Creare `src/bot/handlers/start.py` — gestione `/connect {token}`
- [ ] Bot verifica token su Supabase → salva `telegram_chat_id`
- [ ] Bot risponde "✅ Account collegato! Sei [Nome Azienda]."
- [ ] Testare il flusso completo dashboard → bot → dashboard

**✅ Gate M1:** Serramentista si registra, completa onboarding, collega bot

---

## M2 — Core Bot: Foto → Misure (Giorni 5-9)

### State Machine
- [ ] Creare `src/bot/services/session_service.py` — SessionManager (§6.3)
- [ ] Implementare `get_or_create()`, `transition()`, `reset()`, `cleanup_expired()`
- [ ] Creare `src/bot/models/session.py` — SessionState enum, StateData model
- [ ] Testare transizioni: idle → awaiting_customer → awaiting_photo → ...

### Flusso nuovo preventivo
- [ ] Creare `src/bot/handlers/new_quote.py` — gestione `/nuovo`
- [ ] Creare `src/bot/services/quote_service.py` — `create_draft()`, `update()`, `finalize()`
- [ ] Creare `src/bot/services/customer_service.py` — `find_or_create()` da testo libero
- [ ] Flusso: /nuovo → chiede cliente → parsing nome/indirizzo → crea quote draft
- [ ] Messaggi strutturati con formattazione Markdown (§6.4)

### Analisi foto AI
- [ ] Creare `src/bot/services/vision.py` — VisionService (§5)
- [ ] Implementare prompt GPT-4o Vision completo (§5.2)
- [ ] Creare `src/bot/models/vision.py` — VisionResult + VisionError (Pydantic §5.3)
- [ ] Pre-processing foto: resize, compress, EXIF fix (Pillow)
- [ ] Creare `src/bot/services/storage_service.py` — upload foto su Supabase Storage
- [ ] Creare `src/bot/handlers/photo.py` — ricezione foto → upload → AI → risultato
- [ ] Mostrare risultato: tipo, misure in cm, area, confidenza
- [ ] Inline keyboard: [✅ Confermo] [✏️ Correggi] [🔄 Rifai foto]
- [ ] Fallback manuale: se marker non rilevato → chiedi misure in cm
- [ ] Salvare `windows` su Supabase + `ai_response_raw` per debug

### Multi-finestra
- [ ] Loop: dopo conferma misure → "Scatta foto finestra N+1 o scrivi 'chiudi'"
- [ ] Contatore finestre in `state_data`
- [ ] Riepilogo finestre al momento di "chiudi" (tipo, misure, area per ognuna)

### Note vocali
- [ ] Creare `src/bot/services/transcription.py` — WhisperService (§5.4)
- [ ] Creare `src/bot/handlers/voice.py` — ricezione vocale → trascrizione
- [ ] Salvare trascrizione su `windows.voice_transcript`
- [ ] Upload file vocale su Supabase Storage

### Comandi utility
- [ ] Creare `src/bot/handlers/commands.py` — `/stato`, `/annulla`, `/help`
- [ ] `/annulla` → reset sessione, bozza preventivo resta nel DB
- [ ] `/stato` → mostra stato attuale (idle, preventivo in corso con N finestre)
- [ ] `/help` → lista comandi disponibili
- [ ] Creare `src/bot/handlers/errors.py` — handler errori globale

### Utilities
- [ ] Creare `src/bot/utils/keyboards.py` — builder per InlineKeyboardMarkup
- [ ] Creare `src/bot/utils/messages.py` — tutti i testi messaggi (§6.4)
- [ ] Creare `src/bot/utils/formatters.py` — formattazione moneta, misure, date

**✅ Gate M2:** Sessione completa foto → misure → conferma per 3+ finestre

---

## M3 — Catalogo + Calcolo (Giorni 10-13)

### Catalogo Dashboard
- [ ] Creare `src/web/src/features/catalog/catalogService.ts` — CRUD Supabase
- [ ] Creare `src/web/src/features/catalog/useCatalog.ts` — TanStack Query hooks
- [ ] Creare `CatalogPage.tsx` — vista per categorie, filtro per tier
- [ ] Creare `ProductForm.tsx` — form creazione/modifica prodotto (nome, SKU, fornitore, tier, prezzo, unità)
- [ ] Creare `CategoryManager.tsx` — gestione categorie con drag & sort
- [ ] Creare `TierPriceTable.tsx` — vista tabellare base/medio/top
- [ ] CRUD completo: crea, modifica, disattiva prodotto
- [ ] Validazione: almeno 1 prodotto per tier per poter fare preventivi

### Extra Presets Dashboard
- [ ] Creare `ExtraPresetsManager.tsx` — gestione voci extra (posa, smaltimento, ecc.)
- [ ] CRUD: aggiungi, modifica prezzo default, disattiva, riordina

### Selezione prodotti nel Bot
- [ ] Creare `src/bot/services/catalog_service.py` — carica prodotti per company + tier
- [ ] Creare `src/bot/handlers/products.py` — selezione prodotti
- [ ] Inline keyboard con categorie → prodotti disponibili per tier
- [ ] Per ogni finestra → applicare prodotti in base al tipo finestra e tier
- [ ] Calcolo automatico quantità (area_mq × prezzo_unitario)
- [ ] Mostrare subtotale per tier: base €X / medio €Y / top €Z

### Voci extra nel Bot
- [ ] Creare `src/bot/handlers/extras.py` — selezione voci extra
- [ ] Inline keyboard con voci extra preimpostate + [Personalizza] + [Fine]
- [ ] Per ogni voce selezionata → inserire quantità e prezzo (default da preset)
- [ ] Creare `quote_extras` su Supabase

### Margine
- [ ] Creare `src/bot/handlers/margin.py` — regolazione margine
- [ ] Inline keyboard: [20%] [25%] [30%] [35%] [Personalizza]
- [ ] Ricalcolo totale con margine su tutti e 3 i tier
- [ ] Mostrare riepilogo: subtotale + extra + margine → totale per tier

### Conferma preventivo
- [ ] Creare `src/bot/handlers/confirm.py` — riepilogo finale + conferma
- [ ] Riepilogo strutturato: N finestre, prodotti scelti, extra, margine, totali
- [ ] Inline keyboard: [✅ Genera PDF] [✏️ Modifica margine] [✏️ Modifica extra]
- [ ] Se "modifica" → torna allo stato corrispondente

**✅ Gate M3:** Preventivo completo con importi calcolati su 3 tier

---

## M4 — PDF + CRM (Giorni 14-17)

### Generazione PDF
- [ ] Creare `src/bot/templates/quote.html` — template Jinja2 (layout §8.1)
- [ ] CSS @page: A4, margini 15mm, header con logo, footer
- [ ] Tabella finestre: #, tipo, misure, area, note
- [ ] Tabella 3 colonne: base / medio / top con subtotali
- [ ] Sezione voci extra
- [ ] Sezione totali con IVA
- [ ] Note del serramentista
- [ ] Footer con info azienda + "Generato con Serramentista by Poonto"
- [ ] Creare `src/bot/services/pdf_generator.py` — PDFGenerator (§8.2)
- [ ] Download logo azienda da Supabase Storage (se presente)
- [ ] Render HTML → WeasyPrint → PDF bytes
- [ ] Upload PDF su Supabase Storage (`pdfs/{company_id}/{number}.pdf`)
- [ ] Aggiornare `quotes.pdf_url` e `quotes.status = 'sent'`
- [ ] Inviare PDF come documento Telegram al serramentista
- [ ] Messaggio: "📄 Preventivo {number} generato! Invialo al cliente via WhatsApp."
- [ ] Testare: generare 3 PDF con dati diversi, verificare layout e calcoli

### CRM Dashboard
- [ ] Creare `src/web/src/features/customers/customerService.ts` — CRUD Supabase
- [ ] Creare `src/web/src/features/customers/useCustomers.ts` — hooks
- [ ] Creare `CustomersPage.tsx` — lista clienti con ricerca
- [ ] Creare `CustomerForm.tsx` — form creazione/modifica
- [ ] Creare `CustomerDetailPage.tsx` — dettaglio con storico preventivi
- [ ] Mostrare stats: totale preventivi, accettati, valore totale

### Preventivi Dashboard
- [ ] Creare `src/web/src/features/quotes/quoteService.ts` — lettura Supabase
- [ ] Creare `src/web/src/features/quotes/useQuotes.ts` — hooks
- [ ] Creare `QuotesPage.tsx` — lista con filtri (stato, cliente, data)
- [ ] Creare `QuoteCard.tsx` — card preventivo con numero, cliente, stato, importo
- [ ] Creare `QuoteStatusBadge.tsx` — badge colorato per stato (§7.3)
- [ ] Creare `QuoteDetailPage.tsx` — dettaglio con:
  - Lista finestre (tipo, misure, foto thumbnail)
  - Tabella prodotti per tier
  - Voci extra
  - Totali con margine e IVA
  - Download PDF
  - Cambio stato (accettato/rifiutato)

### Dashboard Home
- [ ] Creare `src/web/src/features/dashboard/useDashboardStats.ts` — query aggregate
- [ ] Creare `StatsCard.tsx` — card KPI singola
- [ ] Creare `DashboardPage.tsx` con 4 KPI: totale, aperti, valore, conversione (§7.4)
- [ ] Creare `RecentQuotes.tsx` — ultimi 5 preventivi
- [ ] Grafico ultimi 30 giorni (Recharts — preventivi creati per giorno)

**✅ Gate M4:** PDF professionale generato e inviato, CRM funzionante, dashboard con KPI

---

## M5 — Polish + Beta (Giorni 18-22)

### Settings Dashboard
- [ ] Creare `SettingsPage.tsx` con 3 tab: Profilo | Preventivo | Telegram
- [ ] Tab Profilo: `CompanyProfileForm.tsx` (dati azienda + logo upload)
- [ ] Tab Preventivo: `QuoteSettingsForm.tsx` (margine default, IVA%, validità, prefisso)
- [ ] Tab Telegram: `TelegramConnect.tsx` (stato, scollega, ricollega)
- [ ] Creare `src/web/src/features/settings/settingsService.ts`
- [ ] Creare `src/web/src/features/settings/useSettings.ts`

### UX Polish
- [ ] Componenti UI mancanti: `Modal`, `Table`, `Select`, `EmptyState`, `ConfirmDialog`
- [ ] Loading states su ogni pagina (skeleton o spinner)
- [ ] Empty states con illustrazione e CTA
- [ ] Toast per feedback azioni (Sonner)
- [ ] Conferma prima di azioni distruttive (cancella prodotto, scollega bot)
- [ ] Responsive: sidebar collapsabile su mobile
- [ ] Favicon e titolo pagina

### Error Handling
- [ ] Bot: catch tutte le eccezioni, messaggio user-friendly + log errore
- [ ] Bot: timeout OpenAI → "Riprova tra qualche secondo"
- [ ] Bot: Supabase down → "Servizio temporaneamente non disponibile"
- [ ] Web: error boundary globale
- [ ] Web: retry automatico query fallite (TanStack Query)

### Test e QA
- [ ] Test T-001: Foto con marker → misure corrette
- [ ] Test T-002: Foto senza marker → errore chiaro
- [ ] Test T-004: Preventivo 5 finestre → PDF completo
- [ ] Test T-005: Cambio margine → ricalcolo corretto
- [ ] Test T-006: Timeout sessione → reset corretto
- [ ] Test T-007: RLS — account A non vede dati B
- [ ] Test T-008: /connect token invalido → errore
- [ ] Test T-009: PDF con logo → logo visibile
- [ ] Smoke test post-deploy (§12.3)

### Beta Test
- [ ] Invitare 3-5 serramentisti beta
- [ ] Preparare catalogo demo (3 prodotti per tier)
- [ ] Raccogliere feedback su: velocità, precisione, UX bot, qualità PDF
- [ ] Bug fixing da feedback

### Deploy Produzione
- [ ] DNS: `serramentista.poonto.it` → Vercel
- [ ] Variabili ambiente produzione su Railway e Vercel
- [ ] Disabilitare Vercel SSO protection
- [ ] Verificare HTTPS funzionante
- [ ] Health check bot
- [ ] Smoke test completo

**✅ Gate M5:** Sistema stabile, 3+ serramentisti lo hanno usato con successo

---

## Post-MVP (V2) — Da pianificare dopo M5

- [ ] Reminder preventivi automatici (quote aperta da X giorni)
- [ ] Tracking apertura PDF (viewed_at)
- [ ] Ordine al fornitore (distinta automatica)
- [ ] Portfolio foto prima/dopo
- [ ] Listino fornitori live
- [ ] Notifiche stato lavoro al cliente
- [ ] Paginazione liste
- [ ] Migrazione GPT-4o → OpenCV+ArUco (TD-001)
- [ ] GDPR: export dati, cancellazione account
- [ ] Monitoring e alerting

---

## Contatori

| Milestone | Task totali | Completati |
|-----------|------------|------------|
| M0 — Setup | 24 | 0 |
| M1 — Auth + Onboarding | 26 | 0 |
| M2 — Core Bot | 28 | 0 |
| M3 — Catalogo + Calcolo | 21 | 0 |
| M4 — PDF + CRM | 25 | 0 |
| M5 — Polish + Beta | 24 | 0 |
| **TOTALE MVP** | **148** | **0** |
