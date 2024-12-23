from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from accounting.store import load, persist, first_link
from accounting import store
from accounting.cc import convert_fidelity_cc_to_beancount
from accounting.accounts import account_directives
from datetime import datetime
import pandas as pd
from fastapi import UploadFile
import os
import traceback

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
async def get_transactions(beancount_filepath: str):
    try:
        entries = load(beancount_filepath)
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
        traceback.print_exc()
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

@router.post("/api/upload")
async def upload_file(file: UploadFile):
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs("/tmp", exist_ok=True)
        filename = f"/tmp/upload_{timestamp}.csv"

        content = await file.read()
        with open(filename, "wb") as f:
            f.write(content)

        sample_txns = pd.read_csv(filename)
        beancount_txns = convert_fidelity_cc_to_beancount(sample_txns)
        all_entries = account_directives + beancount_txns
        beancount_filepath = f"/tmp/transactions_{timestamp}.beancount"
        store.persist(all_entries, beancount_filepath)
        return {"beancount_filepath": beancount_filepath, "message": f"File uploaded successfully as {filename}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
