import sys
import os

from src.features.services import FeaturesServices
from src.db.init.services import init_db
from src.db.kfold.services import split_tables_into_kfold
from src.models.services import Model

if __name__ == "__main__":

    args = sys.argv

    if len(args) <= 1:
        print("Usage: python {service_name} [args]")
        os._exit(0)

    if args[1] == "init_db":
        init_db()

    if args[1] == "kfold":
        for kfold_config_name in args[2:]:
            split_tables_into_kfold(kfold_config_name)

    if args[1] == "feature":
        if len(args) >= 3:
            feature_names = args[2:]
        else:
            feature_names = []
        f = FeaturesServices()
        f.create_features(feature_names)

    if args[1] == "cv":
        config_name = args[2]
        m = Model(config_name)
        m.cross_validation()

    if args[1] == "predict":
        config_name = args[2]
        m = Model(config_name)
        m.predict()
