import pandas as pd

from src.features.base import Feature


class FamilySize(Feature):
    def create_features(self):
        for schema in self.schemas:
            for table_name in ["train", "test"]:
                df = self.db.get_df(
                    """
                    SELECT
                        passenger_id,
                        sib_sp + parch AS family_size
                    FROM {}.{}
                """.format(
                        schema, table_name
                    )
                )
                self.db.insert_cols(
                    schema=schema, table_name=table_name, df=df, on="passenger_id"
                )


class PclassOhe(Feature):
    def create_features(self):
        for schema in self.schemas:
            train = self.db.table_load(schema, "train", ["passenger_id", "pclass"])
            test = self.db.table_load(schema, "test", ["passenger_id", "pclass"])
            combined = pd.concat([train, test], axis=0, sort=True)
            combined = pd.concat(
                [combined, pd.get_dummies(combined["pclass"], prefix="pclass")], axis=1
            )
            train, test = combined.iloc[: len(train)], combined[len(train) :]
            self.db.insert_cols(schema, "train", train, "passenger_id")
            self.db.insert_cols(schema, "test", test, "passenger_id")
