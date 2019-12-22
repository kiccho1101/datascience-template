from src.config.exp.exp1 import config as exp1

from src.config.kfold.basic import kfold_basic

TARGET_COL = "survived"
INDEX_COL = "passenger_id"

exp_config = {"exp1": exp1}

kfold_config = {"basic": kfold_basic}
