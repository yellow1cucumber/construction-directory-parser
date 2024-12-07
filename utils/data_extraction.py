from bs4 import Tag

def extract_text(element: Tag) -> str:
    return ''.join(element.stripped_strings).strip()