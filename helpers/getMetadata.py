def get_metadata_from_file(text: str, str_to_find: str):
    metadata = {}
    metadata['Length of whole text'] = len(text)
    metadata['Amount of alphanumeric symbols'] = len([symb for symb in text if symb.isalnum()])
    metadata['Number of occurrences of that string in the text'] = text.lower().count(str_to_find.lower())
    return metadata