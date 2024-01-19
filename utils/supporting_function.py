import os
from pathlib import Path


def get_file_exension(path):
    if isinstance(path, str):
        ext = os.path.splitext(path)[1]
    elif isinstance(path, Path):
        ext = path.suffix
    else:
        raise TypeError("path must be a string or Path object")

    return ext or ""
