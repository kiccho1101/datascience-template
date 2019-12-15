import pandas as pd
import glob
import re
from tqdm import tqdm


def col_name_to_snake_case():
    file_names = glob.glob("./input/*/*/*.csv")

    for fname in tqdm(file_names):
        df: pd.DataFrame = pd.read_csv(fname)

        col_names_snake_case = [
            re.sub("([A-Z])", lambda x: "_" + x.group(1).lower(), col_name).lstrip("_")
            for col_name in df.columns
        ]

        df.columns = col_names_snake_case

        df.to_csv(fname, header=True, index=False)
