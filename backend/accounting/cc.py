from datetime import datetime

import pandas as pd
from beancount.core import data
from beancount.core.amount import Amount
from beancount.core.number import D

from .accounts import create_transaction


def convert_fidelity_cc_to_beancount(df):
    transactions = []
    for _, row in df.iterrows():
        date = datetime.strptime(row['Date'], '%Y-%m-%d').date()
        payee = row['Name']
        narration = row['Memo'] if pd.notna(row['Memo']) else ""
        amount = D(str(abs(row['Amount'])))  # Use absolute value
        txn_category = "Uncategorized"

        if row['Transaction'] == 'DEBIT':
            # For purchases: debit Expenses, credit Liabilities:CreditCard
            postings = [
                data.Posting(f"Expenses:{txn_category}", Amount(amount, "USD"), None, None, None, None),
                data.Posting("Liabilities:CreditCard:Fidelity", Amount(-amount, "USD"), None, None, None, None)
            ]
        else:  # CREDIT
            # For payments or refunds: debit Liabilities:CreditCard, credit Assets:Checking:Chase
            postings = [
                data.Posting("Liabilities:CreditCard:Fidelity", Amount(amount, "USD"), None, None, None, None),
                data.Posting("Assets:Checking:Chase", Amount(-amount, "USD"), None, None, None, None)
            ]

        transactions.append(create_transaction(date, payee, narration, postings))
    return transactions


def convert_amex_to_beancount(df):
    transactions = []
    def is_repayment(description):
        return "PAYMENT" in description.upper() or "THANK YOU" in description.upper()
    for _, row in df.iterrows():
        date = datetime.strptime(row['Date'], '%m/%d/%Y').date()
        payee = row['Description']
        narration = row['Extended Details']
        amount = D(str(abs(row['Amount'])))
        card_holder = row['Card Member'].replace(" ", "_").lower()
        amex_category = f"amex_category_{row['Account #']}"
        txn_category = "Uncategorized"
        tags = {card_holder, amex_category}

        if row['Amount'] < 0 and not is_repayment(row['Description']):
            # Expense transaction
            postings = [
                data.Posting(f"Expenses:{txn_category}", Amount(amount, "USD"), None, None, None, None),
                data.Posting("Liabilities:CreditCard:Amex", Amount(-amount, "USD"), None, None, None, None)
            ]
        elif is_repayment(row['Description']):
            # Repayment transaction
            postings = [
                data.Posting("Liabilities:CreditCard:Amex", Amount(amount, "USD"), None, None, None, None),
                data.Posting("Assets:Checking:Chase", Amount(-amount, "USD"), None, None, None, None)
            ]
        else:
            # Refund transaction
            postings = [
                data.Posting("Liabilities:CreditCard:Amex", Amount(amount, "USD"), None, None, None, None),
                data.Posting("Expenses:Uncategorized", Amount(-amount, "USD"), None, None, None, None)
            ]

        transactions.append(create_transaction(date, payee, narration, postings, tags))

    return transactions
