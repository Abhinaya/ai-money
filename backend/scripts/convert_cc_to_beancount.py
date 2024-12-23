import sys
import os
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from accounting import store
from accounting.cc import convert_fidelity_cc_to_beancount
from accounting.accounts import account_directives
import os

def main():
    sample_txns = pd.read_csv(os.path.join(os.path.dirname(__file__), './statements/sample-statement.csv'))
    beancount_txns = convert_fidelity_cc_to_beancount(sample_txns)
    all_entries = account_directives + beancount_txns
    beancount_filepath = os.path.join(os.path.dirname(__file__), 'transactions.beancount')
    store.persist(all_entries, beancount_filepath)

if __name__ == "__main__":
    main()
