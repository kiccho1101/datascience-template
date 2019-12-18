import inspect

from src.utils.services import timer
from src.features.base import Feature
from src.features.basic import *
from typing import List


class FeaturesServices:
    def read_namespace(self) -> dict:
        features = {}
        namespace = globals()
        for var_name in list(namespace):
            variable = namespace[var_name]
            if (
                inspect.isclass(variable)
                and issubclass(variable, Feature)
                and not inspect.isabstract(variable)
            ):
                features[var_name] = variable
        return features

    def create_features(self, feature_names: List[str]):
        with timer("Create features"):
            all_features = self.read_namespace()

            if len(feature_names) == 0:
                exec_feature_names = list(all_features.keys())
            else:
                exec_feature_names = feature_names

            for fname in exec_feature_names:
                with timer("Create {}".format(fname)):
                    f = all_features[fname]()
                    f.create_features()
