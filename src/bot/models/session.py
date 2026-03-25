"""Modelli sessione bot — State machine per il flusso preventivo"""
from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID


class SessionState(str, Enum):
    """Stati della sessione bot"""
    IDLE = "idle"
    AWAITING_CUSTOMER = "awaiting_customer"
    AWAITING_PHOTO = "awaiting_photo"
    CONFIRMING_MEASURES = "confirming_measures"
    SELECTING_PRODUCTS = "selecting_products"
    SELECTING_EXTRAS = "selecting_extras"
    ADJUSTING_MARGIN = "adjusting_margin"
    CONFIRMING_QUOTE = "confirming_quote"


class StateData(BaseModel):
    """Dati temporanei della sessione"""
    current_quote_id: Optional[str] = None
    customer_name: Optional[str] = None
    customer_address: Optional[str] = None
    window_count: int = 0
    current_window_id: Optional[str] = None
    last_vision_result: Optional[dict] = None
    selected_tier: Optional[str] = None
    margin_pct: float = 25.0
