# Serramentista

🪟 App Telegram + Dashboard per serramentisti.
Il preventivo in tasca, per ogni finestra, in ogni casa.

## Stack

- **Bot:** Python 3.12, python-telegram-bot, OpenAI GPT-4o Vision
- **Dashboard:** React 19, Vite, TypeScript, Tailwind CSS 4
- **Backend:** Supabase (PostgreSQL, Auth, Storage)
- **Deploy:** Vercel (dashboard) + Railway (bot)

## Setup locale

```bash
# Bot
cd src/bot && python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python main.py

# Dashboard
cd src/web && npm install && npm run dev
```

## Documentazione

- [TDD Tecnico](TDD_Serramentista.md)
- [Task Breakdown](TASK_BREAKDOWN.md)
- [Marker Specs](docs/MARKER_SPECS.md)

---

*Sviluppato da [Poonto](https://poonto.it)*
