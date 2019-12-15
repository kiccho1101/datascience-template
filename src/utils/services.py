import time
import re
from contextlib import contextmanager


@contextmanager
def timer(name: str):
    t0 = time.time()
    print(f"[{name}] start")
    yield
    print(f"[{name}] done in {time.time() - t0:.4f} s")
    print()


def to_snake_case(str_array):
    return [
        re.sub("([A-Z])", lambda x: "_" + x.group(1).lower(), s).lstrip("_")
        for s in str_array
    ]
