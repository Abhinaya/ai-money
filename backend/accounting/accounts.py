import zlib
from datetime import datetime

from beancount.core import data

from .catagory import CATEGORIES


def create_link_id(date, amount, narration):
    date_str = date.strftime("%Y%m%d")
    amount_str = str(abs(amount)).replace('.', '')
    if narration:
        narration_hash = format(zlib.crc32(narration.encode()) & 0xFFFFFFFF, 'x')[:6]
    else:
        narration_hash = "empty"
    return f"{date_str}-{amount_str}-{narration_hash}"

def create_transaction(date, payee, narration, postings, tags=set()) -> data.Transaction:
    amount = abs(postings[0].units.number)
    link_id = create_link_id(date, amount, narration)
    return data.Transaction(
        date=date,
        meta=None,
        flag='*',
        payee=payee,
        narration=narration,
        tags=tags,
        links={link_id},
        postings=postings
    )

def create_account_open_directive(date, account):
    return data.Open(
        date=date,
        account=account,
        currencies=["USD"],
        booking=None,
        meta=None
    )

date_open = datetime(2024, 1, 1).date()

account_directives = [
    create_account_open_directive(date_open, "Liabilities:CreditCard:Fidelity"),
    create_account_open_directive(date_open, "Liabilities:CreditCard:Amex"),
    create_account_open_directive(date_open, account="Assets:Checking:Chase"),
]

for catagory in CATEGORIES:
    account_directives.append(create_account_open_directive(date_open, catagory))
