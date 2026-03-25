# 🔧 Piano Fix Deploy — Da fare a fine progetto

> Errori emersi durante M0 di Serramentista. Da sistemare alla fine dello sviluppo.
> **NON IMPLEMENTARE ORA.**

---

## 1. Workflow deploy per progetti monorepo

**Problema:** The Lair pipeline assume `package.json` nella root. Serramentista ha `src/web/` come cartella React.

**Fix:**
- [ ] Aggiornare `projects.json` su Hetzner: aggiungere campo `build_root` o `build_command` custom per progetto
- [ ] Nella pipeline `deploy_pipeline.py`, se il progetto ha un `build_root`, fare `cd` in quella cartella prima di `npm run build`
- [ ] In alternativa: creare un `package.json` wrapper nella root con script `"build": "cd src/web && npm run build"`

---

## 2. Mai segreti nei CLAUDE.md di progetto

**Problema:** Ho copiato i comandi deploy da `the_lair_tools.md` nel `CLAUDE.md` del progetto, inclusi email/password. Il file è finito nel repo pubblico.

**Fix:**
- [ ] Aggiungere regola in `Memoria AI/memoriaAI.md` sezione "Regole operative → Codice":
  ```
  - CLAUDE.md nei progetti NON deve MAI contenere credenziali, password, token o chiavi API
  - I comandi deploy devono referenziare Memoria AI, non duplicare segreti
  - Verificare con `grep -rn "password\|token\|Poonto" .` prima di ogni primo push
  ```
- [ ] Aggiungere un check in `the_lair_tools.md` nel CASO 1, Passo 1:
  ```
  ⚠️ PRIMA DEL PUSH: verifica che nessun file nel repo contenga segreti.
  ```

---

## 3. Usare sempre Hetzner per operazioni con token

**Problema:** Ho provato ad accedere al Keychain macOS e SSH dal terminale di Antigravity — si blocca perché serve un prompt di autorizzazione.

**Fix:**
- [ ] Aggiungere nota in `Memoria AI/memoriaAI.md`:
  ```
  - Per operazioni che richiedono GitHub token o SSH key: usare SEMPRE il VPS Hetzner
  - Il Keychain macOS richiede autorizzazione GUI, non funziona da terminale remoto
  - Comandi SSH verso Hetzner: sempre semplici e lineari, mai heredoc con quote nidificate
  ```

---

## 4. Comandi SSH — best practice

**Problema:** I comandi SSH con heredoc `<< 'EOF'` e python inline si bloccano quando ci sono quote nidificate.

**Fix:**
- [ ] Aggiungere in `the_lair_tools.md` una sezione "Best practice SSH":
  ```
  - Usare comandi semplici, un'azione alla volta
  - Evitare heredoc con quote nidificate (usare pipe o file temporanei)  
  - Sempre aggiungere: -o ConnectTimeout=10 -o ServerAliveInterval=5
  - Per script complessi: scrivere un .sh, copiarlo via scp, eseguirlo via ssh
  ```

---

## 5. Pre-deploy checklist per nuovi progetti

- [ ] Creare file `Memoria AI/checklist_nuovo_progetto.md` con:
  1. Verificare struttura cartelle (dove è il `package.json`?)
  2. Grep segreti prima del push: `grep -rn "password\|token\|Poonto\|vcp_" . --exclude-dir=node_modules --exclude-dir=.git`
  3. Configurare `vercel.json` coerente con il root directory
  4. Usare Hetzner per creare repo GitHub (non Keychain locale)
  5. Testare build locale prima di deployare
  6. Dopo il push: verificare che GitGuardian non segnali nulla

---

**Quando implementare:** Dopo M5, prima di chiudere il progetto.
