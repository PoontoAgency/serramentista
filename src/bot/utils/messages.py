"""Tutti i testi messaggi bot — centralizzati per manutenzione"""

# /start
MSG_START = """🪟 *Benvenuto in Serramentista!*

Questo bot ti aiuta a creare preventivi per serramenti in pochi minuti.

*Come funziona:*
1️⃣ Scrivi /nuovo per iniziare un preventivo
2️⃣ Inserisci il nome del cliente
3️⃣ Scatta una foto della finestra con il marker A4
4️⃣ Conferma le misure e scegli i prodotti
5️⃣ Ricevi il PDF pronto da inviare!

Scrivi /help per i comandi disponibili."""

# /help
MSG_HELP = """📋 *Comandi disponibili:*

/nuovo — 🆕 Inizia un nuovo preventivo
/stato — 📊 Mostra stato sessione attuale
/annulla — ❌ Annulla il preventivo corrente
/help — ❓ Mostra questa guida

Per collegare l'account: /connect `<token>`"""

# /connect
MSG_CONNECT_OK = "✅ *Account collegato!*\n\nSei _{company_name}_.\nOra puoi usare /nuovo per fare il primo preventivo."
MSG_CONNECT_NO_TOKEN = "⚠️ Per collegare l'account scrivi:\n`/connect <token>`\n\nTrovi il token nella dashboard su serramentista.vercel.app"
MSG_CONNECT_INVALID = "❌ Token non valido. Verifica il token nella dashboard."
MSG_CONNECT_ALREADY = "ℹ️ Questo account è già collegato a _{company_name}_."

# /nuovo
MSG_NEW_QUOTE_ASK_CUSTOMER = "👤 *Nuovo preventivo*\n\nScrivi il nome del cliente (opzionalmente, aggiungi indirizzo e città separati da virgola):\n\n_Es: Mario Rossi, Via Roma 1, Milano_"
MSG_NEW_QUOTE_CUSTOMER_OK = "✅ Cliente: *{customer_name}*\n\n📸 Ora scatta una foto della prima finestra.\n\n_Ricorda: posiziona un foglio A4 bianco accanto alla finestra come riferimento._"

# Foto
MSG_PHOTO_ANALYZING = "🔄 *Analizzo la foto...*\nCalcolo dimensioni in base al marker A4."
MSG_PHOTO_RESULT = """📐 *Finestra #{window_num}*

• Tipo: {window_type}
• Larghezza: {width_cm} cm
• Altezza: {height_cm} cm
• Area: {area_mq} m²
• Confidenza: {confidence}

{notes}"""

MSG_PHOTO_NO_MARKER = """⚠️ *Marker A4 non rilevato*

Non riesco a vedere il foglio A4 nella foto. Puoi:
• Scattare un'altra foto con il marker ben visibile
• Inserire le misure manualmente"""

# Riepilogo
MSG_WINDOWS_SUMMARY = "📋 *Riepilogo finestre:*\n\n{windows_text}\n\n*Totale: {total_count} finestre — {total_area} m²*"

# Sessione
MSG_STATE_IDLE = "ℹ️ Nessun preventivo in corso.\nScrivi /nuovo per iniziarne uno."
MSG_STATE_ACTIVE = "📊 *Preventivo in corso*\n\n• Cliente: {customer_name}\n• Finestre: {window_count}\n• Stato: {state}"

# Errori
MSG_NOT_CONNECTED = "⚠️ Account non collegato.\n\nApri la dashboard su serramentista.vercel.app e genera un token di collegamento."
MSG_CANCELLED = "❌ Preventivo annullato.\nScrivi /nuovo per iniziarne uno nuovo."
MSG_ERROR = "❌ Si è verificato un errore. Riprova tra qualche momento."

# Vocali
MSG_VOICE_TRANSCRIBED = "🎤 *Nota vocale trascritta:*\n_{text}_"
MSG_VOICE_ERROR = "⚠️ Non sono riuscito a trascrivere il messaggio vocale."
