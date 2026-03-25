"""Formattazione moneta, misure, date"""


def format_currency(amount: float) -> str:
    """Formatta importo in EUR: 1234.56 → € 1.234,56"""
    return f"€ {amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def format_measure_cm(cm: float) -> str:
    """Formatta misura in cm: 120.5 → 120,5 cm"""
    return f"{cm:.1f} cm".replace(".", ",")


def format_area_mq(mq: float) -> str:
    """Formatta area in m²: 1.2345 → 1,23 m²"""
    return f"{mq:.2f} m²".replace(".", ",")


def format_date(dt_str: str) -> str:
    """Formatta data ISO → gg/mm/aaaa"""
    from datetime import datetime
    try:
        dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        return dt.strftime("%d/%m/%Y")
    except Exception:
        return dt_str


def format_window_type(wtype: str) -> str:
    """Formatta tipo finestra per display"""
    types = {
        "battente": "🪟 Battente",
        "scorrevole": "↔️ Scorrevole",
        "vasistas": "↕️ Vasistas",
        "portafinestra": "🚪 Portafinestra",
        "fisso": "⬜ Fisso",
        "altro": "❓ Altro",
    }
    return types.get(wtype, wtype)
