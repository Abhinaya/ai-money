from beancount import loader
from beancount.parser import printer
import os

FILENAME = 'transactions.beancount'

def first_link(entry):
    """Retrieve the first link from the entry's links attribute, or return an empty string if links are missing or empty."""
    links = getattr(entry, 'links', [])
    if links:
        return sorted(links)[0]
    return ""

def persist(entries, filepath=FILENAME):
    # root_dir = os.path.dirname(os.path.abspath(__file__))
    # root_dir = os.path.abspath(os.path.join(root_dir, os.pardir))

    # file_path = os.path.join(root_dir, filename)
    entries.sort(key=first_link)

    with open(filepath, 'w') as f:
        for entry in entries:
            f.write(printer.format_entry(entry))
            f.write('\n\n')

    print(f"Entries have been saved to {filepath}")
    print(f"It has {len(load())} entries")

def load(filepath=FILENAME):
    # root_dir = os.path.dirname(os.path.abspath(__file__))
    # root_dir = os.path.abspath(os.path.join(root_dir, os.pardir))

    # file_path = os.path.join(root_dir, filename)

    entries, errors, _ = loader.load_file(filepath)
    if errors:
        raise ValueError(f"Error loading beancount file: {errors}")
    return entries
