from utils.files import get_files
from pathlib import Path
from typing import Union
import os

def blizzard(path: Union[str, Path], books, metadata):
    filepath = os.path.join(path, metadata)

    text_dict = {}

    with open(filepath, encoding='utf-8') as f  :
        content =  f.readlines()

    for line in content :
        split = line.split('|')
        filename = split[0]
        book_split = filename.split("-")
        bookname = book_split[0]+"-"+book_split[1]

        if bookname in books:
            text_dict[split[0]] = split[-1]

    return text_dict
