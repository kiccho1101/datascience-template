import glob
from tqdm import tqdm
import pandas as pd
from src.db.services import DBServices


def insert_data():
    db = DBServices()
    fnames = glob.glob("./input/*/*/*.csv")

    for fname in tqdm(fnames):
        _, _, schema, table_name, _ = fname.split("/")
        df = pd.read_csv(fname)

        db.df_to_table(
            table_name=table_name,
            schema=schema,
            df=df,
            replace=False,
            csv_fname=fname.replace("./input", "/input"),
        )
