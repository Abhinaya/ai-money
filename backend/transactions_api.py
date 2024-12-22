from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from accounting.store import load, persist, first_link
from datetime import datetime

router = APIRouter()

class Transaction(BaseModel):
    id: str
    date: str
    description: str
    postings: List[Dict]
    from_account: str  # Credit account
    to_account: str  # Debit account
    links: List[str]

def format_amount(amount):
    if amount is None:
        return "0.00"
    return f"{amount.number}"

@router.get("/api/transactions")
async def get_transactions():
    try:
        entries = load()
        transactions = []

        for entry in entries:
            if hasattr(entry, 'postings'):
                credit_posting = next((p for p in entry.postings if p.units and p.units.number < 0), None)
                debit_posting = next((p for p in entry.postings if p.units and p.units.number > 0), None)
                transactions.append({
                    'id': first_link(entry),
                    'date': str(entry.date),
                    'payee': entry.payee,
                    'narration': entry.narration,
                    'from_account': credit_posting.account,
                    'to_account': debit_posting.account,
                    'amount': f"${abs(float(format_amount(credit_posting.units))):.2f}",
                    'postings': [
                        {'account': p.account, 'amount': str(p.units)}
                        for p in entry.postings
                    ],
                    'links': list(entry.links) if hasattr(entry, 'links') else []
                })

        return transactions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/transactions")
async def create_transaction(transaction: Transaction):
    try:
        entries = load()
        # Convert transaction to beancount format and append
        # Implementation needed here
        persist(entries)
        return {"message": "Transaction created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
