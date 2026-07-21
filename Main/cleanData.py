import re

def clean_text(text):
    # Remove "Yellow Revised 5/14/08"
    text = re.sub(r'Yellow Revised.*?\n', '', text)

    # Remove page numbers that appear alone
    text = re.sub(r'^\d+[A-Z]?\s*$', '', text, flags=re.MULTILINE)

    # Remove scene/page markers like (238), (31), (403 1/2)
    text = re.sub(r'\(\d+[^\)]*\)', '', text)

    # Remove multiple blank lines
    text = re.sub(r'\n\s*\n+', '\n\n', text)

    # Remove repeated spaces/tabs
    text = re.sub(r'[ \t]+', ' ', text)

    return text.strip()