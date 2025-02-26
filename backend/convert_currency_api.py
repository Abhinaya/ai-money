from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


USD_TO_INR_RATE = 86.84


class CurrencyConversionRequest(BaseModel):
    amount: int
    from_currency: str
    to_currency: str


class CurrencyConversionResponse(BaseModel):
    amount: int
    currency: str

@router.post("/convert-currency", response_model=CurrencyConversionResponse)
async def convert_currency(request: CurrencyConversionRequest):

    if request.from_currency.upper() != "USD" or request.to_currency.upper() != "INR":
        raise HTTPException(status_code=500, detail="Only USD to INR conversion is supported.")
    

    converted_amount = int(request.amount * USD_TO_INR_RATE)

    return {"amount": converted_amount, "currency": "INR"}