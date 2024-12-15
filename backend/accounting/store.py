from beancount.parser import printer
from beancount import loader
from beancount.core import data

FILENAME = 'transactions.beancount'

def first_link(entry):
    """Retrieve the first link from the entry's links attribute, or return an empty string if links are missing or empty."""
    links = getattr(entry, 'links', [])
    if links:
        return sorted(links)[0]
    return ""

def persist(entries, filename=FILENAME):
    entries.sort(key=first_link)
    with open(filename, 'w') as f:
        for entry in entries:
            f.write(printer.format_entry(entry))
            f.write('\n\n')
    print(f"Beancount transactions have been written to {filename}")
    print(f"It has {len(load())} entries")


def load(filename=FILENAME):
    entries, errors, _ = loader.load_file(filename)
    if errors:
        raise ValueError(f"Error loading beancount file: {errors}")
    return entries
