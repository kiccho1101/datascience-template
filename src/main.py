import sys
import os

from src.features.services import FeaturesServices
from src.init_db.services import init_db

if __name__ == "__main__":

    args = sys.argv

    if len(args) <= 1:
        print("Usage: python {service_name} [args]")
        os._exit(0)

    if args[1] == "init_db":
        init_db()

    if args[1] == "feature":
        if len(args) >= 3:
            feature_names = args[2:]
        else:
            feature_names = []
        f = FeaturesServices()
        f.create_features(feature_names)
