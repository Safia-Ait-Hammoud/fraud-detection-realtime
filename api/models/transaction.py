from pydantic import BaseModel, Field
from typing import Optional

class Transaction(BaseModel):
    transaction_id: str = Field(..., example="TXN-123456")
    timestamp: Optional[str] = None
    amount: float = Field(..., example=250.50)
    transaction_hour: int = Field(..., ge=0, le=23, example=14)
    merchant_category: str = Field(..., example="Electronics")
    foreign_transaction: int = Field(..., ge=0, le=1, example=0)
    location_mismatch: int = Field(..., ge=0, le=1, example=0)
    device_trust_score: float = Field(..., example=0.85)
    velocity_last_24h: float = Field(..., example=3.0)
    cardholder_age: int = Field(..., example=35)