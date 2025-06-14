
import os


def ensure_path(path):
    if not os.path.exists(path=path):
        os.makedirs(path, exist_ok=True)
    return path


def ensure_file(file):
    if not os.path.exists(file):
        f = open(file, "w")
        f.close()
    return file
