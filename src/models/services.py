from sklearn import linear_model
from sklearn import svm
from lightgbm import LGBMClassifier, LGBMRegressor
from xgboost import XGBClassifier, XGBRegressor
from catboost import CatBoostClassifier, CatBoostRegressor

from sklearn.metrics import accuracy_score, mean_squared_log_error

import pandas as pd
import numpy as np
import os
import pickle
import glob

from src.db.services import DBServices
from src.config.services import INDEX_COL, TARGET_COL, exp_config
from src.utils.services import now

models = {
    "LGBMClassifier": LGBMClassifier,
    "LGBMRegressor": LGBMRegressor,
    "XGBClassifier": XGBClassifier,
    "XGBRegressor": XGBRegressor,
    "CatBoostClassifier": CatBoostClassifier,
    "CatBoostRegressor": CatBoostRegressor,
    "LinearRegression": linear_model.LinearRegression,
    "Ridge": linear_model.Ridge,
    "Lasso": linear_model.Lasso,
    "SVC": svm.SVC,
}
metrics = {
    "accuracy_score": accuracy_score,
    "MSLE": mean_squared_log_error,
    "RMSLE": lambda x, y: np.sqrt(mean_squared_log_error(x, y)),
}


class Model:
    def __init__(self, config_name: dict):
        self.config_name = config_name
        self.config = exp_config[config_name]
        self.db = DBServices()
        self.train_cols = self.config["features"]["train"]
        self.target_col = self.config["features"]["target"]
        self.model_name = self.config["model"]["name"]
        self.model = models[self.model_name]()
        self.schemas = self.db.find_schema(like=self.config["kfold_config_name"])[
            "schema_name"
        ].values
        self.metrics = metrics[self.config["metrics"]]

    def cross_validation(self):
        if not os.path.exists("./output/cv_results"):
            os.makedirs("./output/cv_results")

        with open("./output/cv_results/{}.txt".format(self.config_name), "a") as f:
            f.write("==================================================\n")
            f.write("Date: {}\n".format(now().strftime("%Y-%m-%d %H:%M:%S")))

        for schema in self.schemas:
            train = self.db.table_load(
                schema=schema,
                table_name="train",
                cols=self.train_cols + self.target_col + [INDEX_COL],
            )
            test = self.db.table_load(
                schema=schema,
                table_name="test",
                cols=self.train_cols + self.target_col + [INDEX_COL],
            )

            self.model = models[self.model_name](**self.config["model"]["params"])
            self.model.fit(
                train[self.train_cols],
                train[self.target_col].iloc[:, 0],
                **self.config["model"]["fit_params"]
            )
            pred = self.model.predict(test[self.train_cols])

            score = self.metrics(test[self.target_col].iloc[:, 0], pred)
            print()
            print("==================================================")
            print("{}: {} Score ::: {}".format(self.config_name, schema, score))
            print("==================================================")
            with open("./output/cv_results/{}.txt".format(self.config_name), "a") as f:
                f.write("{}: {} Score ::: {}\n".format(self.config_name, schema, score))

            result_df = pd.DataFrame(
                {
                    INDEX_COL: test[INDEX_COL],
                    "pred": pred,
                    "real": test[self.target_col].iloc[:, 0],
                }
            )
            self.db.df_to_table(
                table_name=self.config_name + "_result",
                schema=schema,
                df=result_df,
                replace=True,
            )

            if not os.path.exists("./output/models/{}".format(self.config_name)):
                os.makedirs("./output/models/{}".format(self.config_name))
            with open(
                "./output/models/{}/{}.pickle".format(self.config_name, schema), "wb"
            ) as f:
                pickle.dump(self.model, f)

        with open("./output/cv_results/{}.txt".format(self.config_name), "a") as f:
            f.write("==================================================\n")
            f.write("\n")

    def predict(self):
        schema = "public"
        train = self.db.table_load(
            schema=schema,
            table_name="train",
            cols=self.train_cols + self.target_col + [INDEX_COL],
        )
        test = self.db.table_load(
            schema=schema, table_name="test", cols=self.train_cols + [INDEX_COL]
        )

        self.model = models[self.model_name](**self.config["model"]["params"])
        self.model.fit(train[self.train_cols], train[self.target_col].iloc[:, 0])
        pred = self.model.predict(test[self.train_cols])

        if not os.path.exists("./output/models/{}".format(self.config_name)):
            os.makedirs("./output/models/{}".format(self.config_name))
        with open(
            "./output/models/{}/{}.pickle".format(self.config_name, schema), "wb"
        ) as f:
            pickle.dump(self.model, f)

        result_df = pd.DataFrame({INDEX_COL: test[INDEX_COL], TARGET_COL: pred})

        self.create_submission(result_df=result_df)

    def create_submission(self, result_df: pd.DataFrame):

        submission_file_prefix = "./output/submission/submission_{}".format(
            now().strftime("%Y-%m-%d")
        )

        submission_no = len(glob.glob(submission_file_prefix + "_*.csv")) + 1
        submission_file_name = "{}_{}.csv".format(submission_file_prefix, submission_no)
        result_df.to_csv(submission_file_name, index=False)
        print("Sumission file: {} saved!".format(submission_file_name))
