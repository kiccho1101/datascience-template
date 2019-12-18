import pandas as pd
import glob
import re
from tqdm import tqdm
from src.utils.services import to_snake_case


def col_name_to_snake_case():
    file_names = glob.glob("./input/*/*/*.csv")

    print(file_names)
    for fname in tqdm(file_names):
        df: pd.DataFrame = pd.read_csv(fname)
        df.columns = to_snake_case(df.columns)

        if "index" in df.columns:
            df.drop("index", axis=1, inplace=True)

        df.to_csv(fname, header=True, index=True, index_label="index")
