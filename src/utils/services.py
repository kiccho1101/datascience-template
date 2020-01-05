import time
import re
import pandas as pd
from contextlib import contextmanager
import datetime
import pytz


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


def col_name_to_valid(str_array):
    def to_valid(s: str):
        s = s.replace("(", "")
        s = s.replace(")", "")
        s = s.replace(" ", "_")
        s = s.replace(".", "__")
        s = s.replace(",", "___")
        if s[0].isdigit():
            s = "num_" + s
        return s

    return pd.Series(str_array).map(to_valid).tolist()


def now():
    return datetime.datetime.now(pytz.timezone("Asia/Tokyo"))
