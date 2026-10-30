import re


SEARCHABLE_FIELDS = [
    "title",
    "description",
    "category",
    "subcategory",
    "tags"
]


def clean_text(text):
    """
    Basic text normalization for EventIQ retrieval.
    """

    if text is None:
        return ""

    text = str(text)

    # Convert to lowercase
    text = text.lower()

    # Replace punctuation with spaces
    text = re.sub(r"[^a-z0-9\s]", " ", text)

    # Remove extra whitespace
    text = re.sub(r"\s+", " ", text).strip()

    return text


def build_searchable_document(event):
    """
    Combine the main textual fields of an event
    into a single searchable document.
    """

    parts = []

    for field in SEARCHABLE_FIELDS:
        value = event.get(field)

        if value is not None:
            parts.append(str(value))

    document = " ".join(parts)

    return clean_text(document)