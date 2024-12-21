import sys
import pandas as pd

sys.path.append('../')
from accounting import store
from accounting.cc import convert_fidelity_cc_to_beancount
from accounting.accounts import account_directives

def main():
    sample_txns = pd.read_csv('./statements/sample-statement.csv')
    beancount_txns = convert_fidelity_cc_to_beancount(sample_txns)
    all_entries = account_directives + beancount_txns
    store.persist(all_entries)

if __name__ == "__main__":
    main()
