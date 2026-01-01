from app.services.import_service import ImportService
from datetime import date

def test_parse_csv_semicolon():
    csv_content = (
        "Buchungstag;Betrag;Verwendungszweck\n"
        "2025-01-05;-42.50;REWE Markt Köln\n"
        "2025-01-01;2500.00;GEHALT JANUAR"
    ).encode("utf-8")
    
    result = ImportService.parse_csv(csv_content)
    transactions = result["transactions"]
    
    assert len(transactions) == 2
    
    assert transactions[0].amount == 42.50
    assert transactions[0].type == "expense"
    assert transactions[0].expense_date == date(2025, 1, 5)
    assert transactions[0].description == "REWE Markt Köln"
    
    assert transactions[1].amount == 2500.00
    assert transactions[1].type == "income"
    assert transactions[1].expense_date == date(2025, 1, 1)
    assert transactions[1].description == "GEHALT JANUAR"

def test_parse_csv_comma_and_german_format():
    csv_content = (
        "Datum,Betrag,Beschreibung\n"
        "05.01.2025,\" -42,50 \",REWE\n"
        "01.01.2025,\"2.500,00\",GEHALT"
    ).encode("utf-8")
    
    result = ImportService.parse_csv(csv_content)
    transactions = result["transactions"]
    
    assert len(transactions) == 2
    assert transactions[0].amount == 42.50
    assert transactions[0].expense_date == date(2025, 1, 5)
    
    assert transactions[1].amount == 2500.00
    assert transactions[1].expense_date == date(2025, 1, 1)

def test_parse_csv_invalid_rows():
    csv_content = (
        "Buchungstag;Betrag;Verwendungszweck\n"
        "invalid-date;-42.50;REWE\n"
        "2025-01-01;invalid-amount;GEHALT"
    ).encode("utf-8")
    
    result = ImportService.parse_csv(csv_content)
    transactions = result["transactions"]
    errors = result["errors"]
    
    assert len(transactions) == 0
    assert len(errors) == 2
    assert "Could not parse date" in errors[0]
    assert "Could not parse amount" in errors[1]
