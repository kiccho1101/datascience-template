from src.config.kfold import kfold_config
from src.config.common import INDEX_COL, TARGET_COL
from src.db.services import DBServices
from src.utils.services import timer

from sklearn.model_selection import StratifiedKFold


def split_tables_into_kfold(kfold_config_name: str):
    db = DBServices()

    n_splits = kfold_config[kfold_config_name]["n_splits"]
    seed = kfold_config[kfold_config_name]["seed"]

    df = db.table_load(
        schema="public", table_name="train", cols=[INDEX_COL, TARGET_COL]
    )
    folds = StratifiedKFold(
        n_splits=n_splits,
        shuffle=True,
        random_state=seed,
    ).split(df[INDEX_COL], df[TARGET_COL])

    for n_fold, (train_index, valid_index) in enumerate(folds):
        with timer("Split No.{}".format(n_fold)):
            schema = "{}_{}".format(
                kfold_config_name,
                n_fold,
            )
            db.exec_query("CREATE SCHEMA IF NOT EXISTS {};".format(schema))
            db.exec_query("DROP TABLE IF EXISTS {}.train;".format(schema))
            db.exec_query("DROP TABLE IF EXISTS {}.valid;".format(schema))

            query = "SELECT * INTO {0}.train FROM public.train WHERE {1} IN ({2}) ORDER BY {1};".format(
                schema, INDEX_COL, ", ".join(df.iloc[train_index][INDEX_COL].astype(str))
            )
            db.exec_query(query)
            query = "SELECT * INTO {0}.valid FROM public.train WHERE {1} IN ({2}) ORDER BY {1};".format(
                schema, INDEX_COL, ", ".join(df.iloc[valid_index][INDEX_COL].astype(str))
            )
            db.exec_query(query)
