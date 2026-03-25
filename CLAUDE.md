# Serramentista — Regole di Progetto

> ⚠️ Questo file va letto ad ogni nuova sessione di lavoro.
> Contiene tutte le convenzioni, lo stack e i riferimenti per lavorare su questo progetto.

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
