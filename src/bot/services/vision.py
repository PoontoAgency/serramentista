"""Servizio analisi foto con GPT-4o Vision"""
import base64
import logging
import httpx
from typing import Optional

from config import settings
from models.vision import VisionResult, VisionError

logger = logging.getLogger(__name__)

VISION_PROMPT = """Sei un assistente per serramentisti. Analizza questa foto di una finestra.

ISTRUZIONI:
1. Cerca un foglio A4 bianco nella foto (marker di riferimento). Il foglio A4 è 21.0 cm × 29.7 cm.
2. Usa il rapporto tra il foglio A4 e la finestra per calcolare le dimensioni reali della finestra.
3. Identifica il tipo di finestra.

RISPONDI IN FORMATO JSON (nessun altro testo):
{
  "marker_detected": true/false,
  "window_type": "battente|scorrevole|vasistas|portafinestra|fisso|altro",
  "width_cm": numero (larghezza in cm),
  "height_cm": numero (altezza in cm),
  "confidence": "alta|media|bassa",
  "notes": "eventuali osservazioni"
}

Se il marker A4 non è visibile, rispondi con marker_detected: false e stima approssimativa se possibile.
Se non riesci a identificare una finestra, metti width_cm e height_cm a 0."""


class VisionService:
    """Analisi foto finestre con GPT-4o Vision"""

    @staticmethod
    async def analyze_photo(image_bytes: bytes, mime_type: str = "image/jpeg") -> VisionResult | VisionError:
        """Invia foto a GPT-4o Vision e ritorna risultato strutturato"""
        if not settings.openai_api_key:
            return VisionError(code="NO_API_KEY", message="Chiave API OpenAI non configurata")

        try:
            b64_image = base64.b64encode(image_bytes).decode("utf-8")

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.openai_api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": "gpt-4o",
                        "messages": [
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": VISION_PROMPT},
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:{mime_type};base64,{b64_image}",
                                            "detail": "high",
                                        },
                                    },
                                ],
                            }
                        ],
                        "max_tokens": 500,
                        "temperature": 0.1,
                    },
                )

            if response.status_code != 200:
                logger.error(f"OpenAI API error: {response.status_code} — {response.text[:200]}")
                return VisionError(
                    code="API_ERROR",
                    message="Errore nella comunicazione con il servizio AI.",
                    suggestion="Riprova tra qualche secondo.",
                )

            data = response.json()
            content = data["choices"][0]["message"]["content"]

            # Parse JSON dalla risposta
            import json
            # Rimuovi eventuale markdown code block
            clean = content.strip()
            if clean.startswith("```"):
                clean = clean.split("\n", 1)[1] if "\n" in clean else clean[3:]
                clean = clean.rsplit("```", 1)[0]

            parsed = json.loads(clean)

            result = VisionResult(
                marker_detected=parsed.get("marker_detected", False),
                window_type=parsed.get("window_type", "battente"),
                width_cm=float(parsed.get("width_cm", 0)),
                height_cm=float(parsed.get("height_cm", 0)),
                area_mq=round(float(parsed.get("width_cm", 0)) * float(parsed.get("height_cm", 0)) / 10000, 4),
                confidence=parsed.get("confidence", "media"),
                notes=parsed.get("notes", ""),
                raw_response=parsed,
            )

            logger.info(f"Vision result: {result.window_type} {result.width_cm}x{result.height_cm}cm (conf: {result.confidence})")
            return result

        except json.JSONDecodeError:
            logger.error(f"Failed to parse Vision response: {content[:200]}")
            return VisionError(
                code="PARSE_ERROR",
                message="Non riesco a interpretare la risposta dell'AI.",
                suggestion="Scatta un'altra foto assicurandoti che la finestra e il marker siano ben visibili.",
            )
        except httpx.TimeoutException:
            return VisionError(
                code="TIMEOUT",
                message="L'analisi sta impiegando troppo tempo.",
                suggestion="Riprova tra qualche secondo.",
            )
        except Exception as e:
            logger.exception(f"Vision service error: {e}")
            return VisionError(code="UNKNOWN", message=f"Errore imprevisto: {str(e)}")
