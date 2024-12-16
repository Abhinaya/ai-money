from beancount.core import data
from .store import FILENAME, load, persist
from beancount.core import data

from .store import FILENAME, load, persist


def update_transactions(txns_to_update, beancount_filepath=FILENAME):
    """
    Update transactions in a beancount file based on input transactions.

    Args:
        input_transactions (list): List of new transaction objects to update
        beancount_filepath (str): Path to the beancount file

    Raises:
        ValueError: If a transaction with matching link is not found
        FileNotFoundError: If the beancount file doesn't exist
    """
    try:
        entries = load(beancount_filepath)
        input_trans_map = {
            next(link for link in txn.links) if txn.links else None: txn
            for txn in txns_to_update
        }
        matched_links = set()
        new_entries = []
        for entry in entries:
            if isinstance(entry, data.Transaction):
                entry_link = next(iter(entry.links)) if entry.links else None
                if entry_link in input_trans_map:
                    new_entries.append(input_trans_map[entry_link])
                    matched_links.add(entry_link)
                else:
                    # Keep existing transaction
                    new_entries.append(entry)
            else:
                new_entries.append(entry)

        unmatched_links = set(input_trans_map.keys()) - matched_links
        if unmatched_links:
            raise ValueError(f"Transactions with links {unmatched_links} not found in file")
        persist(new_entries, beancount_filepath)
    except FileNotFoundError:
        raise FileNotFoundError(f"Beancount file not found: {beancount_filepath}")
    except Exception as e:
        raise Exception(f"Error processing beancount file: {str(e)}")

def update_expense_category(id: str, exp_category: str):
    entries = load(FILENAME)
    new_entries = []
    for entry in entries:
        if isinstance(entry, data.Transaction):
            entry_link = next(iter(entry.links)) if entry.links else None
            if entry_link == id:
                new_postings = []
                for posting in entry.postings:
                    if posting.account == "Expenses:Uncategorized":
                        new_posting = posting._replace(account=exp_category)
                        new_postings.append(new_posting)
                    else:
                        new_postings.append(posting)
                new_entry = entry._replace(postings=new_postings)
                new_entries.append(new_entry)
            else:
                new_entries.append(entry)
        else:
            new_entries.append(entry)
    persist(new_entries, FILENAME)

def update_expense_categories(updates: list[dict]):
    print("update_expense_categories: ", updates)
    entries = load(FILENAME)
    new_entries = []
    updated_ids = set()
    for entry in entries:
        if isinstance(entry, data.Transaction):
            txn_id = next(iter(entry.links)) if entry.links else None
            matching_update = next(
                (u for u in updates if u['id'] == txn_id),
                None
            )

            if matching_update:
                new_postings = []
                for posting in entry.postings:
                    if posting.account == "Expenses:Uncategorized":
                        updated_account = matching_update['rectified_category']
                        new_posting = posting._replace(account=updated_account)
                        print(f"Updating txn id: {txn_id} to expense account {updated_account}")
                        new_postings.append(new_posting)
                    else:
                        new_postings.append(posting)
                # Add vendor as metadata
                meta = dict(entry.meta or {})
                meta['vendor'] = matching_update['rectified_vendor']
                new_entry = entry._replace(postings=new_postings, meta=meta)
                new_entries.append(new_entry)
                updated_ids.add(txn_id)
            else:
                new_entries.append(entry)
        else:
            new_entries.append(entry)

    # Do we need this check ?
    # if len(updated_ids) != len(updates):
    #     missing = set(u['id'] for u in updates) - updated_ids
    #     raise ValueError(f"Transactions with links {missing} not found")

    persist(new_entries, FILENAME)
