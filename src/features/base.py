import re
from abc import ABCMeta, abstractmethod
from src.db.services import DBServices


class Feature(metaclass=ABCMeta):
    def __init__(self):
        self.db = DBServices()
        df = self.db.find_schema(like="", unlike="pg_")
        self.schemas = df[df["schema_name"] != "information_schema"][
            "schema_name"
        ].values
        if self.__class__.__name__.isupper():
            self.name = self.__class__.__name__.lower()
        else:
            # Rename to snake_case
            self.name = re.sub(
                "([A-Z])", lambda x: "_" + x.group(1).lower(), self.__class__.__name__
            ).lstrip("_")

    @abstractmethod
    def create_features(self):
        raise NotImplementedError
