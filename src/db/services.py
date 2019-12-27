import os
import re

import numpy as np
import pandas as pd
import psycopg2
from sqlalchemy import create_engine
from tqdm import tqdm
from src.utils.services import to_snake_case
from typing import List


class DBServices:
    def dtype_mapper(self):
        dtype_mapper = {
            np.dtype("object"): "TEXT",
            np.dtype("int32"): "BIGINT",
            np.dtype("int64"): "BIGINT",
            np.dtype("uint8"): "BIGINT",
            np.dtype("float64"): "DOUBLE PRECISION",
            np.dtype("datetime64[ns]"): "TIMESTAMP",
        }
        return dtype_mapper

    def conn(self):
        conn = psycopg2.connect(
            user=os.environ["POSTGRES_USER"],
            password=os.environ["POSTGRES_PASSWORD"],
            host=os.environ["POSTGRES_HOST"],
            port=5432,
            database=os.environ["PROJECT_NAME"],
        )
        cur = conn.cursor()
        return conn, cur

    def exec_query(self, query: str):

        with psycopg2.connect(
            user=os.environ["POSTGRES_USER"],
            password=os.environ["POSTGRES_PASSWORD"],
            host=os.environ["POSTGRES_HOST"],
            port=5432,
            database=os.environ["PROJECT_NAME"],
        ) as conn, conn.cursor() as cur:
            cur.execute(query)
            conn.commit()

    def get_df(self, query: str):

        with psycopg2.connect(
            user=os.environ["POSTGRES_USER"],
            password=os.environ["POSTGRES_PASSWORD"],
            host=os.environ["POSTGRES_HOST"],
            port=5432,
            database=os.environ["PROJECT_NAME"],
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
        table_name: str,
        schema: str,
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
            query = "COPY {} FROM '{}' DELIMITER ',' CSV HEADER".format(
                table_name, csv_fname
            )
            self.exec_query(query)

        else:
            values = [
                "({})".format(
                    ", ".join(
                        [
                            # If it's NaN, set NULL
                            "NULL" if value != value
                            # If it's number, set str without ''
                            else "{}".format(str(value))
                            if dtypes[key] in ["DOUBLE PRECISION", "BIGINT"]
                            # If else, set str with ''
                            else "'{}'".format(str(value).replace("'", "''"))
                            for key, value in d.items()
                        ]
                    )
                )
                for d in df.to_dict(orient="records")
            ]

            for i in tqdm(range(int(len(values) / 10000) + 1)):
                if len(values[i * 10000 : (i + 1) * 10000]) > 0:
                    query = "INSERT INTO {}.{} ({}) VALUES {};".format(
                        schema,
                        table_name,
                        ", ".join(to_snake_case(df.columns)),
                        ",".join(values[i * 10000 : (i + 1) * 10000]),
                    )
                    self.exec_query(query)

    def insert_cols(self, schema: str, table_name: str, df: pd.DataFrame, on: str):
        self.df_to_table(
            table_name=table_name + "_tmp", schema=schema, df=df, replace=True
        )

        dtype_mapper = self.dtype_mapper()

        queries = [
            """
          -- ALTER TABLE {4}.{0} DROP COLUMN IF EXISTS {1};
          ALTER TABLE {4}.{0} ADD COLUMN IF NOT EXISTS {1} {2};
          UPDATE {4}.{0} AS t1
          SET    {1} = t2.{1}
          FROM   {4}.{0}_tmp AS t2
          WHERE  t1.{3} = t2.{3}
          """.format(
                table_name, col_name, dtype, on, schema
            )
            for col_name, dtype in df.dtypes.map(dtype_mapper).iteritems()
        ]

        with psycopg2.connect(
            user=os.environ["POSTGRES_USER"],
            password=os.environ["POSTGRES_PASSWORD"],
            host=os.environ["POSTGRES_HOST"],
            port=5432,
            database=os.environ["PROJECT_NAME"],
        ) as conn, conn.cursor() as cur:
            for query in queries:
                cur.execute(query)
            conn.commit()

        self.exec_query("DROP TABLE {}.{}_tmp;".format(schema, table_name))

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
