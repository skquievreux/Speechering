"""
Text Processor - OpenAI GPT Integration
Korrigiert und verbessert transkribierten Text mittels GPT-4.
"""

import logging
import time
from typing import Optional

from openai import OpenAI

from src.config import config

logger = logging.getLogger(__name__)

class TextProcessor:
    """Service für Text-Korrektur und -Verbesserung"""

    def __init__(self):
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.max_retries = 3
        self.retry_delay = 1.0

    def process_text(self, raw_text: str) -> Optional[str]:
        """Verarbeitet und korrigiert den transkribierten Text"""
        if not self._validate_input_text(raw_text):
            return None

        for attempt in range(self.max_retries):
            try:
                logger.info(f"Starte Text-Korrektur (Versuch {attempt + 1}/{self.max_retries})")

                start_time = time.time()

                prompt = self._create_correction_prompt(raw_text)

                response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "Du bist ein professioneller Textkorrektor. Korrigiere Grammatik, Interpunktion und verbessere die Lesbarkeit, aber behalte den originalen Sinn bei."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=1000,
                    temperature=0.3  # Konsistente Ergebnisse
                )

                corrected_text = response.choices[0].message.content.strip()  # type: ignore

                # Entferne Anführungszeichen am Anfang und Ende
                if corrected_text.startswith('"') and corrected_text.endswith('"'):
                    corrected_text = corrected_text[1:-1].strip()
                elif corrected_text.startswith('"'):
                    corrected_text = corrected_text[1:].strip()
                elif corrected_text.endswith('"'):
                    corrected_text = corrected_text[:-1].strip()

                duration = time.time() - start_time
                logger.info(".2f")

                # Validiere Ergebnis
                if self._validate_output_text(corrected_text):
                    return corrected_text
                else:
                    logger.warning("Korrigierter Text ist ungültig")
                    return raw_text  # Fallback auf Original

            except Exception as e:
                logger.error(f"Fehler bei Text-Verarbeitung (Versuch {attempt + 1}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (2 ** attempt))
                else:
                    logger.error("Maximale Anzahl von Versuchen erreicht")
                    return raw_text  # Fallback

        return raw_text  # Fallback bei allen Fehlern

    def _create_correction_prompt(self, text: str) -> str:
        """Erstellt den Prompt für GPT"""
        return f"""Korrigiere folgenden transkribierten Text:

Text: "{text}"

Anweisungen:
- Verbessere Grammatik und Rechtschreibung
- Füge korrekte Interpunktion hinzu
- Mache den Text flüssig und natürlich lesbar
- Behalte den originalen Sinn und Inhalt bei
- Keine zusätzlichen Kommentare oder Erklärungen
- Antworte nur mit dem korrigierten Text

Korrigierter Text:"""

    def _validate_input_text(self, text: str) -> bool:
        """Validiert den Eingabetext"""
        if not text:
            logger.warning("Eingabetext ist leer")
            return False

        cleaned = text.strip()
        if len(cleaned) == 0:
            logger.warning("Eingabetext enthält nur Leerzeichen")
            return False

        if len(cleaned) > 10000:  # Zu langer Text
            logger.warning(f"Eingabetext zu lang: {len(cleaned)} Zeichen")
            return False

        return True

    def _validate_output_text(self, text: str) -> bool:
        """Validiert den Ausgabetext"""
        if not text:
            return False

        cleaned = text.strip()
        return len(cleaned) > 0

    def estimate_cost(self, text_length: int) -> float:
        """Schätzt Kosten für Text-Verarbeitung (GPT-4: ~$0.03/1K tokens)"""
        # Rough estimate: 1 token ≈ 4 characters
        estimated_tokens = text_length / 4
        # Input + output tokens
        total_tokens = estimated_tokens * 2
        return (total_tokens / 1000) * 0.03