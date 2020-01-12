import psycopg2
import pandas as pd
import numpy as np
import os
from tqdm import tqdm
from src.utils.services import to_snake_case
import json

from typing import List


class DBServices:
    def __init__(
        self,
        user: str = os.environ["POSTGRES_USER"],
        password: str = os.environ["POSTGRES_PASSWORD"],
        host: str = os.environ["POSTGRES_HOST"],
        port: int = int(os.environ["POSTGRES_PORT"]),
        database: str = os.environ["POSTGRES_DATABASE"],
    ):
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.database = database

    def dtype_mapper(self):
        dtype_mapper = {
            np.dtype("object"): "TEXT",
            np.dtype("int32"): "BIGINT",
            np.dtype("int64"): "BIGINT",
            np.dtype("uint8"): "BIGINT",
            np.dtype("float32"): "DOUBLE PRECISION",
            np.dtype("float64"): "DOUBLE PRECISION",
            np.dtype("datetime64[ns]"): "TIMESTAMP",
        }
        return dtype_mapper

    def conn(self):
        conn = psycopg2.connect(
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.database,
        )
        cur = conn.cursor()
        return conn, cur

    def exec_query(self, query: str):
        with psycopg2.connect(
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.database,
        ) as conn, conn.cursor() as cur:
            cur.execute(query)
            conn.commit()

    def get_df(self, query: str) -> pd.DataFrame:
        with psycopg2.connect(
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.database,
        ) as conn:
            df = pd.read_sql(query, con=conn)
            return df

    def create_index(self, schema: str, table_name: str, cols: List[str]):
        query = """
            CREATE INDEX IF NOT EXISTS
            {0}_{1}_{2}_idx ON {0}.{1} ({3})
        """.format(
            schema, table_name, "_".join(cols), ", ".join(cols)
        )
        self.exec_query(query)

    def df_to_table(
        self,
        schema: str,
        table_name: str,
        df: pd.DataFrame,
        replace: bool,
        csv_fname: str = "",
    ):

        dtype_mapper = self.dtype_mapper()
        dtypes = df.dtypes.map(dtype_mapper)

        if dtypes.isnull().sum() > 0:
            print(dtypes)
            raise ValueError(
                "There's unknown type in df. Please add the type definition into 'dtype_mapper'"
            )

        create_cols = []
        if "index" not in df.columns:
            create_cols.append("index serial")
        create_cols += [
            "{} {}".format(col_name, dtype) for col_name, dtype in dtypes.iteritems()
        ]
        query = "CREATE TABLE IF NOT EXISTS {}.{} ( {} );".format(
            schema, table_name, ", ".join(create_cols)
        )

        if replace:
            self.exec_query("DROP TABLE IF EXISTS {}.{};".format(schema, table_name))
        self.exec_query(query)

        if csv_fname != "":
            query = "COPY {}.{} FROM '{}' DELIMITER ',' CSV HEADER".format(
                schema, table_name, csv_fname
            )
            self.exec_query(query)

        else:
            df.to_csv("./input/tmp.csv", header=True, index=True, index_label="index")
            query = "COPY {}.{} FROM '{}' DELIMITER ',' CSV HEADER".format(
                schema, table_name, "/input/tmp.csv"
            )
            self.exec_query(query)

    def insert_cols(
        self,
        schema: str,
        table_name: str,
        df: pd.DataFrame,
        on: List[str],
        split_num: int = 100,
    ):

        dtype_mapper = self.dtype_mapper()
        dtypes = df.dtypes.map(dtype_mapper)

        self.create_index(schema, table_name, on)

        for col_name, dtype in tqdm(df.dtypes.map(dtype_mapper).iteritems()):
            if col_name not in on:
                print(col_name)
                self.exec_query(
                    "ALTER TABLE {0}.{1} ADD COLUMN IF NOT EXISTS {2} {3};".format(
                        schema, table_name, col_name, dtype
                    )
                )

                values = [
                    "({})".format(
                        ", ".join(
                            [
                                "{}".format(str(v))
                                if dtypes[k] in ["DOUBLE PRECISION", "BIGINT"]
                                else "'{}'".format(str(v).replace("'", "''"))
                                for k, v in d.items()
                            ]
                        )
                    )
                    for d in json.loads(df[on + [col_name]].to_json(orient="records"))
                ]

                for i in tqdm(range(int(len(values) / split_num) + 1)):
                    if len(values[i * split_num : (i + 1) * split_num]) > 0:
                        query = """
                            UPDATE {0}.{1} AS t1
                            SET {2} = t2.{2}
                            FROM (VALUES
                                {3}
                            ) AS t2({4}, {2})
                            WHERE
                                {5}
                        """.format(
                            schema,
                            table_name,
                            col_name,
                            ",".join(values[i * split_num : (i + 1) * split_num]),
                            ", ".join(on),
                            " AND ".join(["t1.{0} = t2.{0}".format(col) for col in on]),
                        )
                        self.exec_query(query)

    def find_schema(self, like: str, unlike=None) -> pd.DataFrame:
        query = "SELECT schema_name FROM information_schema.schemata"
        query += " WHERE schema_name LIKE '%{}%'".format(like)
        if unlike is not None:
            query += " AND schema_name NOT ILIKE '%{}%'".format(unlike)
        query += " ORDER BY schema_name; "
        df = self.get_df(query)
        return df

    def find_table_name(self, like: str, unlike=None) -> pd.DataFrame:
        query = "SELECT table_name"
        query += " FROM information_schema.tables"
        query += " WHERE table_schema='public'"
        query += " AND table_type='BASE TABLE'"
        query += " AND table_name LIKE '%{}%'".format(like)
        if unlike is not None:
            query += " AND table_name NOT ILIKE '%{}%'".format(unlike)
        query += " ORDER BY table_name; "
        df = self.get_df(query)
        return df

    def table_load(self, schema: str, table_name: str, cols=None) -> pd.DataFrame:

        if cols is None:
            df = self.get_df(
                "SELECT * FROM {}.{} ORDER BY index;".format(schema, table_name)
            )

        else:
            col_names_snake_case = to_snake_case(cols)
            df = self.get_df(
                "SELECT index, {} FROM {}.{} ORDER BY index;".format(
                    ", ".join(col_names_snake_case), schema, table_name
                )
            )
        return df
