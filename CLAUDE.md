# Serramentista — Regole di Progetto

> ⚠️ Questo file va letto ad ogni nuova sessione di lavoro.
> Contiene tutte le convenzioni, lo stack e i riferimenti per lavorare su questo progetto.

---

## 🚨 OBBLIGO — The Lair & Guida Operativa

> **OBBLIGO ASSOLUTO.** Non esistono alternative. Non esistono scorciatoie.
> Ogni violazione è un errore grave.

Per **TUTTE** le seguenti operazioni è **OBBLIGATORIO**:
1. Leggere la guida `../Memoria AI/the_lair_tools.md` **PRIMA** di eseguire qualsiasi comando
2. Seguire il workflow esattamente come descritto, passo per passo
3. Usare **ESCLUSIVAMENTE** i token e le credenziali salvati su Hetzner VPS (`/home/lair/projects/the-lair/.env`)
4. **MAI** usare token/password hardcoded, `npx vercel` diretto, o qualsiasi workaround

### Operazioni coperte dall'obbligo:
- **Creare repo GitHub** → guida, sezione CASO 1
- **Registrare progetto su The Lair** → guida, sezione CASO 1, Passo 3
- **Deploy dashboard (Vercel)** → guida, sezione CASO 1, Passo 4
- **Deploy bot (Railway)** → guida
- **Creare/modificare tabelle Supabase** → guida, sezione Supabase
- **Collegare dominio custom** → guida, sezione Cloudflare + Vercel
- **Inviare notifiche Telegram** → guida, sezione Telegram
- **Qualsiasi operazione con API esterne** → guida

### Regole segreti:
- **MAI** committare password, token, API key o credenziali in nessun file del repo
- I segreti vivono SOLO su Hetzner e in Memoria AI, MAI nel codice

## 🚨 OBBLIGO — Task Breakdown

> **OBBLIGO ASSOLUTO.** Non esistono scorciatoie. Non si salta nessun task.

1. **PRIMA** di iniziare qualsiasi lavoro: aprire e leggere `TASK_BREAKDOWN.md`
2. Individuare il **prossimo task non spuntato** nell'ordine scritto
3. Eseguire **quel task e solo quel task**
4. **Spuntarlo** nel file (`[ ]` → `[x]`) dopo averlo completato
5. Passare al task successivo — **MAI saltare avanti**
6. Se un task è un test/verifica → **eseguirlo davvero**, non saltarlo
7. Non passare alla milestone successiva finché TUTTI i task della milestone corrente non sono `[x]`

## 🚨 OBBLIGO — Qualità sopra velocità

> **OBBLIGO ASSOLUTO.** Non si va di fretta. Si fanno le cose per bene.

- Scegliere **SEMPRE** la strada più professionale, mai quella più veloce e superficiale
- Ogni file scritto deve essere **testato e verificato** prima di considerarlo completato
- Mai scrivere codice "tanto poi lo sistemo" — farlo giusto la prima volta
- Se c'è un modo corretto e uno veloce, scegliere **SEMPRE** quello corretto
- Non accumulare debito tecnico: fix, test e verifica subito, non "dopo"
- La fretta produce errori (secret leak, deploy falliti, task saltati) — la calma produce qualità

---

## Progetto

**Serramentista** — App Telegram + Dashboard per serramentisti.
Il serramentista scatta una foto della finestra con un marker fisico A4, l'AI calcola le misure, e in pochi minuti ha un preventivo PDF pronto da inviare al cliente.

- **Stato:** In sviluppo — MVP
- **Owner:** Stefano Colicino / Poonto S.r.l.
- **TDD:** `TDD_Serramentista.md` (in questa cartella — fonte di verità tecnica)
- **Task:** `TASK_BREAKDOWN.md` (in questa cartella — checklist operativa)

---

## Stack

### Bot (Python 3.12)
- python-telegram-bot 21.x (async)
- httpx 0.27+ (HTTP client)
- supabase-py 2.x (database)
- WeasyPrint 62+ (PDF)
- Jinja2 3.x (template PDF)
- Pillow 10+ (image processing)
- Pydantic 2.x (validazione)
- structlog 24+ (logging)

### Dashboard (React + TypeScript)
- React 19 + Vite 6 + TypeScript 5
- Tailwind CSS 4
- React Router 7
- Zustand 5 (state)
- TanStack Query 5 (server state)
- supabase-js 2 (auth + DB)
- React Hook Form 7 + Zod 3 (forms)
- Radix UI (UI primitivi)
- Lucide React (icons)
- Sonner (toast)
- Recharts 2 (grafici dashboard)

### Infrastruttura
- **Database:** Supabase (PostgreSQL + RLS + Auth + Storage)
- **Bot hosting:** Railway (Docker container)
- **Dashboard hosting:** Vercel
- **AI:** OpenAI GPT-4o Vision + Whisper
- **Deploy:** The Lair (Hetzner VPS `178.104.79.139`)

---

## Struttura cartelle

```
serramentista/
├── src/
│   ├── bot/                    # Python — Telegram Bot
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── handlers/           # Un file per feature
│   │   ├── services/           # Business logic
│   │   ├── models/             # Pydantic models
│   │   ├── utils/              # Keyboards, formatters, messages
│   │   └── templates/          # Template HTML per PDF
│   ├── web/                    # React — Dashboard
│   │   └── src/
│   │       ├── app/            # Router, App, main
│   │       ├── features/       # Feature-based (auth, quotes, customers, catalog, settings, dashboard)
│   │       ├── components/     # Layout + UI riusabili
│   │       ├── lib/            # Supabase client, utils
│   │       ├── store/          # Zustand stores
│   │       └── types/          # TypeScript types
│   └── supabase/
│       └── migrations/         # SQL versionate (001_, 002_, ...)
├── docs/                       # TDD, marker specs
├── .github/workflows/          # CI/CD
├── Dockerfile                  # Bot container
├── railway.toml
├── vercel.json
└── CLAUDE.md                   # QUESTO FILE
```

---

## Convenzioni

### Naming
| Cosa | Regola | Esempio |
|------|--------|---------|
| File Python | snake_case | `quote_service.py` |
| Classi Python | PascalCase | `QuoteService` |
| File React (componenti) | PascalCase | `QuoteCard.tsx` |
| File React (hook) | camelCase con `use` | `useQuotes.ts` |
| File React (servizi) | camelCase | `quoteService.ts` |
| Tabelle DB | snake_case plurale | `line_items` |
| Colonne DB | snake_case | `company_id` |

### Git
- **Branch:** `feature/xxx`, `fix/xxx`, `chore/xxx`
- **Commit:** Conventional Commits → `feat(bot): add photo analysis`
- **Main branch:** `main`
- **Non lavorare mai direttamente su `main`** — branch separati per ogni feature

### Preventivi
- Formato numero: `{PREFIX}-{ANNO}-{PROGRESSIVO}` → `SER-2026-0001`
- PREFIX configurabile per azienda (default: `SER`)

---

## Deploy

### Via The Lair (metodo standard)

> ⚠️ Tutti i comandi deploy, credenziali e token sono documentati in:
> - `../Memoria AI/the_lair_tools.md` — workflow completo passo per passo
> - `../Memoria AI/the_lair_briefing.md` — infrastruttura e stato live
>
> **Non duplicare segreti in questo repo.**

Workflow rapido (dettagli in Memoria AI):
1. `git push` — pusha su GitHub
2. Sync Hetzner — `git pull` sul VPS
3. Deploy via The Lair API — login + `/api/deploy/serramentista`
4. Verifica sito live

### Credenziali
> ⚠️ Tutte le credenziali sono centralizzate su The Lair (Hetzner VPS) e in `Memoria AI/`.
> Non committare mai segreti in questo repo.
- **Riferimento:** `../Memoria AI/the_lair_tools.md`

---

## Comandi utili

### Sviluppo locale
```bash
# Bot (Python)
cd src/bot && python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python main.py  # polling mode

# Dashboard (React)
cd src/web && npm install && npm run dev
# → http://localhost:5173
```

### Test
```bash
# Bot
cd src/bot && pytest

# Dashboard
cd src/web && npm run typecheck && npm run lint && npm test
```

---

## Riferimenti
- **TDD completo:** `TDD_Serramentista.md`
- **Task breakdown:** `TASK_BREAKDOWN.md`
- **Marker specs:** `docs/MARKER_SPECS.md`
- **Memoria AI:** `../Memoria AI/` (contesto globale, credenziali, progetti)
- **The Lair tools:** `../Memoria AI/the_lair_tools.md` (workflow deploy dettagliato)
