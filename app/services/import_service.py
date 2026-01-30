# import service der die CSV-Datei handled und validiert
# Autor: Rose Bahar

import csv
import io
import logging
from datetime import datetime
from typing import List
from app.schemas.expense import ImportedTransaction

# logger für Debugging genutzt
logger = logging.getLogger(__name__)

from typing import Dict, Any

class ImportService:
    @staticmethod
    def parse_csv(content: bytes) -> Dict[str, Any]:
        """
        ImportService parst das CSV and returned ein dictionary mit Transaktionen und Errors.
        Erwartetes Input Format: Buchungstag;Betrag;Verwendungszweck
        """
        try:
            # Wir versuchen den Inhalt als UTF-8 Content zu lesen
            text_content = content.decode("utf-8")

            # Logger für Debugging genutzt
            # logger.info(f"Received CSV content length: {len(text_content)}")
            
            #Erste Zeile speichern
            f = io.StringIO(text_content)
            
            sample = f.read(1024)
            f.seek(0)
            
            try:
                #Trennzeichen Erkennen
                dialect = csv.Sniffer().sniff(sample, delimiters=";,")
                # logger.info(f"Trennzeichen erkannt: '{dialect.delimiter}'")
            except csv.Error:
                # Fallback auf Semikolon, wenn kein Trennzeichen gefunden werden konnte
                # logger.warning("Could not sniff delimiter, defaulting to ';'")
                class Dialect(csv.Dialect):
                    delimiter = ';'
                    quotechar = '"'
                    lineterminator = '\n'
                    quoting = csv.QUOTE_MINIMAL
                dialect = Dialect
            
            reader = csv.DictReader(f, dialect=dialect)
            
            transactions = []
            errors = []
            headers_found = reader.fieldnames if reader.fieldnames else []
            
            for i, row in enumerate(reader):
                # Buchungstag -> date
                # Betrag -> amount
                # Verwendungszweck -> description
                
                # Wir erlauben hier mehrere Bezeichnungen für Datum, Betrag und Verwendungszweck. Zukünftig erweiterbar oder mit AI erkennbar.
                date_key = next((k for k in row.keys() if k and ("datum" in k.lower() or "buchungstag" in k.lower() or "date" in k.lower())), None)
                amount_key = next((k for k in row.keys() if k and ("betrag" in k.lower() or "summe" in k.lower() or "amount" in k.lower())), None)
                desc_key = next((k for k in row.keys() if k and ("verwendung" in k.lower() or "beschreibung" in k.lower() or "purpose" in k.lower() or "description" in k.lower())), None)
                
                # Wenn ein Key Fehlt Error anzeigen
                if not (date_key and amount_key and desc_key):
                    msg = f"Row {i+1}: Missing required columns. Found keys: {list(row.keys())}"
                    logger.debug(msg)
                    errors.append(msg)
                    continue
                        
                raw_date = row[date_key]
                raw_amount = row[amount_key]
                description = row[desc_key]
                
                # Werte normalisieren, damit wir damit rechnen können
                try:
                    if "," in raw_amount and "." in raw_amount:
                        clean_amount = raw_amount.replace(".", "").replace(",", ".")
                    elif "," in raw_amount:
                        clean_amount = raw_amount.replace(",", ".")
                    else:
                        clean_amount = raw_amount
                        
                    amount_val = float(clean_amount)
                except ValueError:
                    msg = f"Reihe {i+1}: Werte konnten nicht geparst werden: '{raw_amount}'"
                    logger.debug(msg)
                    errors.append(msg)
                    continue
                    
                expense_date = None
                for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y"):
                    try:
                        expense_date = datetime.strptime(raw_date, fmt).date()
                        break
                    except ValueError:
                        continue
                
                # Wenn kein Datum dann Fehler
                if not expense_date:
                    msg = f"Reihe {i+1}: Datum konnte nicht verarbeitet werden: '{raw_date}'"
                    logger.debug(msg)
                    errors.append(msg)
                    continue
                    
                # Typ erkennen: Wenn Wert über 0 dann Einnahme sonst Ausgabe
                trans_type = "income" if amount_val > 0 else "expense"
                
                transactions.append(ImportedTransaction(
                    amount=abs(amount_val),
                    type=trans_type,
                    expense_date=expense_date,
                    description=description,
                    category_id=None
                ))
            
            return {
                "transactions": transactions,
                "errors": errors,
                "headers_found": headers_found
            }
        # Fehlermeldung wenn CSV Parsing nicht funktioniert.
        except Exception as e:
            logger.error(f"Error parsing CSV: {str(e)}", exc_info=True)
            return {
                "transactions": [],
                "errors": [f"Fatal CSV Error: {str(e)}"],
                "headers_found": []
            }
