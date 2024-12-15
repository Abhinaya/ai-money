import pandas as pd

from accounting import store
from accounting.cc import convert_amex_to_beancount, convert_fidelity_cc_to_beancount
from accounting.accounts import account_directives

def main():
    amex_txns = pd.read_csv('./statements/amex.csv')
    fidelity_txns = pd.read_csv('./statements/Fidelity Credit Card.csv')

    amex_beancount_txns = convert_amex_to_beancount(amex_txns)
    fidelity_beancount_txns = convert_fidelity_cc_to_beancount(fidelity_txns)

    all_entries = account_directives + fidelity_beancount_txns + amex_beancount_txns
    store.persist(all_entries)

if __name__ == "__main__":
    main()
