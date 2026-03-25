# 📐 MARKER_SPECS — Marker di Calibrazione Serramentista

**Versione:** 1.0
**Data:** 25/03/2026

---

## Specifiche fisiche

| Parametro | Valore |
|-----------|--------|
| **Formato** | A4 (210mm × 297mm) |
| **Materiale MVP** | Carta standard 80g/m² (stampata da stampante laser) |
| **Materiale produzione** | Vinile adesivo rimovibile (non lascia residui sul vetro) |
| **Colore** | Alto contrasto bianco/nero |

---

## Design del marker

```
┌──────────────────────────────────────────────┐
│  ●                                        ●  │
│                                              │
│                                              │
│                                              │
│                                              │
│               ┌──────────────┐               │
│               │              │               │
│               │   QR CODE    │               │
│               │   (size +    │               │
│               │    version)  │               │
│               │              │               │
│               └──────────────┘               │
│                                              │
│                                              │
│                                              │
│                                              │
│                                              │
│  ●                                        ●  │
└──────────────────────────────────────────────┘
      210mm × 297mm (A4)
```

### Elementi

1. **4 cerchi angolari** (marker di calibrazione)
   - Diametro: 15mm
   - Colore: nero pieno su sfondo bianco
   - Posizione: 20mm dal bordo (centro del cerchio)
   - Scopo: GPT-4o Vision li usa per calcolare la matrice di trasformazione prospettica

2. **QR Code centrale**
   - Dimensione: 60mm × 60mm
   - Contenuto: JSON → `{"size":"A4","w":210,"h":297,"v":1}`
   - Scopo: conferma al bot la dimensione esatta del marker (per calibrazione)

3. **Sfondo**
   - Bianco puro (#FFFFFF) per massimo contrasto
   - Bordo nero 2mm intorno al perimetro (aiuta il rilevamento)

---

## Come si usa

1. Il serramentista **stampa il marker** su un foglio A4 (o lo riceve nel kit di benvenuto)
2. Lo **posiziona sulla finestra** — appoggiato al vetro, visibile nella foto
3. **Scatta la foto** con Telegram, inquadrando tutta la finestra + marker
4. L'AI rileva i 4 cerchi → calcola la prospettiva → misura la finestra rispetto al marker

---

## Perché A4

- **Universale:** ogni serramentista ha una stampante, e le misure A4 sono standard (210×297mm)
- **Sufficientemente grande:** copre finestre da 40cm a 3m+ con buona precisione
- **Costo zero per il MVP:** si stampa su carta normale, nessun costo di produzione
- **Upgrade futuro:** vinile adesivo personalizzato con logo dell'azienda (V2)

---

## Calibrazione nel prompt AI

Il prompt GPT-4o Vision riceve come parametro:
```
marker_size_mm = 210  (larghezza A4)
```

Il sistema sa che il marker è 210×297mm e usa questa informazione come scala di riferimento per calcolare le dimensioni reali della finestra.

---

## Condizioni di utilizzo

| Condizione | Supportata | Note |
|-----------|:----------:|------|
| Luce naturale | ✅ | Condizione ideale |
| Luce artificiale | ✅ | Funziona bene |
| Controluce forte | ⚠️ | Può ridurre il contrasto — il bot suggerisce di cambiare angolazione |
| Notte/buio | ❌ | Flash del telefono potrebbe creare riflessi sul vetro |
| Pioggia (marker bagnato) | ⚠️ | Solo con vinile impermeabile (V2) |
| Finestra molto grande (>3m) | ⚠️ | Richiedere foto più distante, confidenza potrebbe calare |
| Finestra molto piccola (<40cm) | ✅ | Il marker A4 è quasi della stessa dimensione — alta precisione |

---

## Taglie future (V2)

Per la V2, se la validazione conferma il bisogno:
- **S (A5):** 148×210mm — per finestre molto piccole (vasistas bagno)
- **M (A4):** 210×297mm — standard (quello attuale)
- **L (A3):** 297×420mm — per portefinestre e vetrate grandi

Il QR code codifica la taglia, quindi il bot sa automaticamente quale marker sta guardando.
