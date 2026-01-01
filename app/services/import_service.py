import csv
import io
import logging
from datetime import datetime
from typing import List
from app.schemas.expense import ImportedTransaction

logger = logging.getLogger(__name__)

from typing import List, Dict, Any

class ImportService:
    @staticmethod
    def parse_csv(content: bytes) -> Dict[str, Any]:
        """
        Parses CSV content and returns a dictionary with transactions and errors.
        Expected format: Buchungstag;Betrag;Verwendungszweck
        """
        try:
            # Read content as text
            text_content = content.decode("utf-8")
            logger.info(f"Received CSV content length: {len(text_content)}")
            
            f = io.StringIO(text_content)
            
            # Try to detect delimiter
            sample = f.read(1024)
            f.seek(0)
            
            try:
                dialect = csv.Sniffer().sniff(sample, delimiters=";,")
                logger.info(f"Detected delimiter: '{dialect.delimiter}'")
            except csv.Error:
                # Fallback to semicolon if sniffing fails
                logger.warning("Could not sniff delimiter, defaulting to ';'")
                class Dialect(csv.Dialect):
                    delimiter = ';'
                    quotechar = '"'
                    lineterminator = '\n'
                    quoting = csv.QUOTE_MINIMAL
                dialect = Dialect
            
            reader = csv.DictReader(f, dialect=dialect)
            
            # Log headers
            if reader.fieldnames:
                logger.info(f"CSV Headers found: {reader.fieldnames}")
            else:
                logger.warning("No headers found in CSV!")
            
            transactions = []
            errors = []
            headers_found = reader.fieldnames if reader.fieldnames else []
            
            for i, row in enumerate(reader):
                # Map columns (German bank export style)
                # Buchungstag -> date
                # Betrag -> amount
                # Verwendungszweck -> description
                
                # Find matching keys regardless of casing and handle potential BOM or whitespace
                date_key = next((k for k in row.keys() if k and ("datum" in k.lower() or "buchungstag" in k.lower() or "date" in k.lower())), None)
                amount_key = next((k for k in row.keys() if k and ("betrag" in k.lower() or "summe" in k.lower() or "amount" in k.lower())), None)
                desc_key = next((k for k in row.keys() if k and ("verwendung" in k.lower() or "beschreibung" in k.lower() or "purpose" in k.lower() or "description" in k.lower())), None)
                
                if not (date_key and amount_key and desc_key):
                    msg = f"Row {i+1}: Missing required columns. Found keys: {list(row.keys())}"
                    logger.debug(msg)
                    errors.append(msg)
                    continue
                    
                raw_date = row[date_key]
                raw_amount = row[amount_key]
                description = row[desc_key]
                
                # Normalize amount (handle 1.234,56 and -42.50)
                try:
                    if "," in raw_amount and "." in raw_amount:
                        clean_amount = raw_amount.replace(".", "").replace(",", ".")
                    elif "," in raw_amount:
                        clean_amount = raw_amount.replace(",", ".")
                    else:
                        clean_amount = raw_amount
                        
                    amount_val = float(clean_amount)
                except ValueError:
                    msg = f"Row {i+1}: Could not parse amount '{raw_amount}'"
                    logger.debug(msg)
                    errors.append(msg)
                    continue
                    
                # Normalize date
                expense_date = None
                for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y"):
                    try:
                        expense_date = datetime.strptime(raw_date, fmt).date()
                        break
                    except ValueError:
                        continue
                
                if not expense_date:
                    msg = f"Row {i+1}: Could not parse date '{raw_date}'"
                    logger.debug(msg)
                    errors.append(msg)
                    continue
                    
                # Determine type
                trans_type = "income" if amount_val > 0 else "expense"
                
                transactions.append(ImportedTransaction(
                    amount=abs(amount_val),
                    type=trans_type,
                    expense_date=expense_date,
                    description=description,
                    category_id=None
                ))
            
            logger.info(f"Successfully parsed {len(transactions)} transactions")
            
            return {
                "transactions": transactions,
                "errors": errors,
                "headers_found": headers_found
            }
            
        except Exception as e:
            logger.error(f"Error parsing CSV: {str(e)}", exc_info=True)
            return {
                "transactions": [],
                "errors": [f"Fatal CSV Error: {str(e)}"],
                "headers_found": []
            }
