import pathlib
import sys
def set_path():
    d = pathlib.Path.resolve(pathlib.Path(__file__).parent.parent)
    dirname = str(d)
    if dirname not in sys.path:
        sys.path.insert(0, dir)
    return d
