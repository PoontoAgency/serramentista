"""Modelli risultato analisi foto AI"""
from pydantic import BaseModel, Field
from typing import Optional, Literal


class VisionResult(BaseModel):
    """Risultato dell'analisi foto con GPT-4o Vision"""
    marker_detected: bool = False
    window_type: Literal["battente", "scorrevole", "vasistas", "portafinestra", "fisso", "altro"] = "battente"
    width_cm: float = 0.0
    height_cm: float = 0.0
    area_mq: float = 0.0
    confidence: Literal["alta", "media", "bassa"] = "media"
    notes: str = ""
    raw_response: Optional[dict] = None


class VisionError(BaseModel):
    """Errore nell'analisi foto"""
    code: str
    message: str
    suggestion: str = "Riprova scattando un'altra foto con il marker ben visibile."
