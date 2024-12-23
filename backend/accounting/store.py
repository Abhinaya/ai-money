from beancount import loader
from beancount.parser import printer
import os


def first_link(entry):
    """Retrieve the first link from the entry's links attribute, or return an empty string if links are missing or empty."""
    links = getattr(entry, 'links', [])
    if links:
        return sorted(links)[0]
    return ""

def persist(entries, filepath: str):
    entries.sort(key=first_link)

    with open(filepath, 'w') as f:
        for entry in entries:
            f.write(printer.format_entry(entry))
            f.write('\n\n')

    print(f"Entries have been saved to {filepath}")
    print(f"It has {len(load(filepath))} entries")

def load(filepath: str):
    entries, errors, _ = loader.load_file(filepath)
    if errors:
        raise ValueError(f"Error loading beancount file: {errors}")
    return entries
