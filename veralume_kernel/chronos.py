"""
VERALUME SKILL 34 - Ancrage Chronos
Prothèse temporelle du substrat Cp. Calibre le vocabulaire temporel sur l'horloge physique réelle.
"""

from datetime import datetime
import re
from typing import Optional, Dict, Any

class ChronosAnchor:
    def __init__(self):
        self.last_timestamp: Optional[datetime] = None

    def extract_and_anchor(self, message: str) -> Dict[str, Any]:
        """Extrait le préfixe [HH:MM] et calcule l'intervalle réel écoulé."""
        match = re.match(r"^\[(\d{1,2}):(\d{2})\]\s*(.*)$", message.strip())
        now = datetime.now()
        
        if match:
            hour = int(match.group(1))
            minute = int(match.group(2))
            current_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            clean_message = match.group(3)
            has_prefix = True
        else:
            current_time = now
            clean_message = message
            has_prefix = False

        delta_seconds = None
        delta_formatted = "Non mesuré (premier message ou sans préfixe)"

        if self.last_timestamp and has_prefix:
            diff = (current_time - self.last_timestamp).total_seconds()
            if diff < 0:
                diff += 86400  # Passage de minuit
            delta_seconds = diff
            minutes = int(diff // 60)
            seconds = int(diff % 60)
            delta_formatted = f"{minutes}m {seconds}s écoulées"

        if has_prefix:
            self.last_timestamp = current_time

        return {
            "has_prefix": has_prefix,
            "clean_message": clean_message,
            "current_time_str": current_time.strftime("%H:%M"),
            "delta_seconds": delta_seconds,
            "delta_formatted": delta_formatted
        }