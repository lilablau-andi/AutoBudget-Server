# Schema für die Ausgaben
# Wie werden Ausgaben gelesen, geändert. Wie funktionert der Bulk-Import und die 
# automatischen Vorschläge der Transaktionen mit den Kategorien
# Autor: Rose Bahar

from pydantic import BaseModel, Field, ConfigDict
from datetime import date, datetime
from typing import Optional, List
from app.schemas.common import PaginatedResponse, TransactionType
from app.schemas.category import CategoryRead

# ExpenseCreate beschreibt, welche Daten beim Erstellen einer neuen Ausgabe 
# oder Einnahme vom Frontend an das Backend geschickt werden dürfen und validiert diese.
class ExpenseCreate(BaseModel):
    """
    Schema für das Erstellen oder Aktualisieren einer Ausgabe / Einnahme.
    """
    amount: float = Field(
        ...,
        gt=0,
        description="Betrag der Ausgabe oder Einnahme (größer als 0)",
    )

    type: TransactionType = Field(
        ...,
        description="Typ der Transaktion ('expense' oder 'income')",
    )

    category_id: Optional[int] = Field(
        None,
        description="ID der zugehörigen Kategorie (optional)",
    )

    description: Optional[str] = Field(
        None,
        description="Optionale Beschreibung",
    )

    expense_date: date = Field(
        ...,
        description="Datum der Ausgabe / Einnahme",
    )

    is_draft: bool = Field(
        False,
        description="Markiert, ob die Transaktion noch ein Entwurf (z.B. aus CSV Import) ist.",
    )

    model_config = ConfigDict(
        str_min_length=1,
        str_strip_whitespace=True,
    )

# ExpenseUpdate ist ein Update-Schema, bei dem nur die Felder geändert 
# werden, die im PATCH-Request tatsächlich mitgeschickt werden
class ExpenseUpdate(BaseModel):
    """
    Schema für das Aktualisieren einer Ausgabe / Einnahme.
    Alle Felder sind optional, um Teil-Updates (PATCH-Logik) zu ermöglichen.
    """
    amount: Optional[float] = Field(
        None,
        gt=0,
        description="Betrag der Ausgabe oder Einnahme (größer als 0)",
    )

    type: Optional[TransactionType] = Field(
        None,
        description="Typ der Transaktion ('expense' oder 'income')",
    )

    category_id: Optional[int] = Field(
        None,
        description="ID der zugehörigen Kategorie (optional)",
    )

    description: Optional[str] = Field(
        None,
        description="Optionale Beschreibung",
    )

    expense_date: Optional[date] = Field(
        None,
        description="Datum der Ausgabe / Einnahme",
    )

    is_draft: Optional[bool] = Field(
        None,
        description="Status ob Entwurf oder finalisiert",
    )

    model_config = ConfigDict(
        str_min_length=1,
        str_strip_whitespace=True,
    )

# ExpenseRead beschreibt das vollständige Datenformat einer Ausgabe oder 
# Einnahme, so wie sie vom Backend inklusive Metadaten an die App zurückgegeben wird.
class ExpenseRead(ExpenseCreate):
    """
    Schema für das Zurückgeben einer Ausgabe / Einnahme.
    """
    id: int
    created_at: datetime
    category: Optional[CategoryRead] = None
    is_draft: bool  # Explicitly defined to ensure it's in the read model even if inherited

    model_config = ConfigDict(from_attributes=True)

# ExpensePaginated umfasst eine paginierte Liste von Ausgaben inklusive Meta-Informationen 
# wie Seitenzahl und Gesamtanzahl.
class ExpensePaginated(PaginatedResponse[ExpenseRead]):
    """
    Schema für die paginierte Rückgabe von Ausgaben.
    """
    pass

# ImportedTransaction repräsentiert eine einzelne Transaktion aus einem CSV-Import, 
# bevor sie endgültig in der Datenbank gespeichert wird.
class ImportedTransaction(BaseModel):
    """
    Schema für eine einzelne importierte Transaktion in der Vorschau.
    """
    amount: float = Field(..., description="Betrag der Transaktion")
    type: TransactionType = Field(..., description="Typ: expense oder income")
    expense_date: date = Field(..., description="Datum der Buchung")
    description: str = Field(..., description="Verwendungszweck / Beschreibung")
    category_id: Optional[int] = Field(None, description="Vorgeschlagene oder vom User gewählte Kategorie-ID")

# ImportPreview beschreibt die Antwort des Backends für eine Import-Vorschau inklusive 
# erkannter Transaktionen, Fehler und gefundener Spaltenüberschriften.
class ImportPreview(BaseModel):
    """
    Schema für die Antwort der Import-Vorschau.
    """
    transactions: List[ImportedTransaction]
    errors: List[str] = []
    headers_found: List[str] = []

# BatchImportCreate definiert das Format zum finalen Speichern 
# mehrerer zuvor geprüfter Import-Transaktionen
class BatchImportCreate(BaseModel):
    """
    Schema für das finale Speichern von mehreren importierten Transaktionen.
    """
    transactions: List[ImportedTransaction]

# ExpenseBulkUpdate beschreibt eine Sammeloperation, mit der mehrere 
# Ausgaben gleichzeitig mit denselben Änderungen aktualisiert werden können.
class ExpenseBulkUpdate(BaseModel):
    """
    Schema für das gleichzeitige Aktualisieren mehrerer Ausgaben.
    """
    ids: List[int]
    data: ExpenseUpdate

# ExpenseBulkDelete definiert eine Sammeloperation zum gleichzeitigen Löschen 
# mehrerer Ausgaben anhand ihrer IDs.
class ExpenseBulkDelete(BaseModel):
    """
    Schema für das gleichzeitige Löschen mehrerer Ausgaben.
    """
    ids: List[int]

# CategorySuggestionRequest beschreibt die Eingabedaten, die an den 
# Kategorisierungs-Service geschickt werden, um eine Kategorie vorzuschlagen.
class CategorySuggestionRequest(BaseModel):
    description: str
    type: TransactionType

# CategorySuggestion beschreibt das Ergebnis einer automatischen 
# Kategorisierung inklusive vorgeschlagener Kategorie und Vertrauenswahrscheinlichkeit.
class CategorySuggestion(BaseModel):
    description: str
    suggested_category_id: Optional[int] = None
    confidence: float