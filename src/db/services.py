import os
import re

import numpy as np
import pandas as pd
import psycopg2
from sqlalchemy import create_engine
from tqdm import tqdm


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

    def df_to_table(
        self, table_name: str, schema: str, df: pd.DataFrame, replace: bool
    ):

        dtype_mapper = self.dtype_mapper()
        dtypes = df.dtypes.map(dtype_mapper)

        if dtypes.isnull().sum() > 0:
            print(dtypes)
            raise ValueError(
                "There's unknown type in df. Please add the type definition into 'dtype_mapper'"
            )

        query = "CREATE TABLE IF NOT EXISTS {}.{} ( {} );".format(
            schema,
            table_name,
            ", ".join(
                [
                    "{} {}".format(col_name, dtype)
                    for col_name, dtype in dtypes.iteritems()
                ]
            ),
        )

        if replace:
            self.exec_query("DROP TABLE IF EXISTS {}.{};".format(schema, table_name))
        self.exec_query(query)

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
                query = "INSERT INTO {}.{} VALUES {};".format(
                    schema, table_name, ",".join(values[i * 10000 : (i + 1) * 10000])
                )
                self.exec_query(query)

    def insert_cols(self, table_name: str, schema: str, df: pd.DataFrame, on: str):
        self.df_to_table(
            table_name=table_name + "_tmp", schema="public", df=df, replace=True
        )

        dtype_mapper = self.dtype_mapper()

        queries = [
            """
          -- ALTER TABLE {0} DROP COLUMN IF EXISTS {1};
          ALTER TABLE {0} ADD COLUMN IF NOT EXISTS {1} {2};
          UPDATE {0} t1
          SET    {1} = t2.{1}
          FROM   {0}_tmp t2
          WHERE  t1.{3} = t2.{3}
          """.format(
                table_name, col_name, dtype, on
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

            cur.execute("DROP TABLE {}_tmp;".format(table_name))
            conn.commit()

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

    def find_table_name(self, like: str, unlike=None) -> pd.DataFrame:
        with psycopg2.connect(
            user=os.environ["POSTGRES_USER"],
            password=os.environ["POSTGRES_PASSWORD"],
            host=os.environ["POSTGRES_HOST"],
            port=5432,
            database=os.environ["PROJECT_NAME"],
        ) as conn:
            query = "SELECT table_name"
            query += " FROM information_schema.tables"
            query += " WHERE table_schema='public'"
            query += " AND table_type='BASE TABLE'"
            query += " AND table_name LIKE '%{}%'".format(like)
            if unlike is not None:
                query += " AND table_name NOT ILIKE '%{}%'".format(unlike)
            query += " ORDER BY table_name; "
            df = pd.read_sql(query, con=conn)
            return df

    def table_load(self, table_name: str, cols=None) -> pd.DataFrame:

        with psycopg2.connect(
            user=os.environ["POSTGRES_USER"],
            password=os.environ["POSTGRES_PASSWORD"],
            host=os.environ["POSTGRES_HOST"],
            port=5432,
            database=os.environ["PROJECT_NAME"],
        ) as conn:

            if cols is None:
                df = pd.read_sql(
                    "SELECT * FROM {} ORDER BY index;".format(table_name), con=conn
                ).set_index("index")

            else:
                col_names_snake_case = [
                    re.sub(
                        "([A-Z])", lambda x: "_" + x.group(1).lower(), col_name
                    ).lstrip("_")
                    for col_name in cols
                ]
                df = pd.read_sql(
                    "SELECT index, {} FROM {} ORDER BY index;".format(
                        ", ".join(col_names_snake_case), table_name
                    ),
                    con=conn,
                ).set_index("index")
            return df

    def table_write(
        self,
        table_name: str,
        df: pd.DataFrame,
        schema: str = None,
        if_exists: str = "replace",
    ):

        # Rename cols to snake_case
        df.columns = (
            pd.Series(df.columns)
            .map(
                lambda col: re.sub(
                    "([A-Z])", lambda x: "_" + x.group(1).lower(), col
                ).lstrip("_")
            )
            .tolist()
        )

        engine = create_engine(
            "postgresql://{}:{}@{}:5432/{}".format(
                os.environ["POSTGRES_USER"],
                os.environ["POSTGRES_PASSWORD"],
                os.environ["POSTGRES_HOST"],
                os.environ["PROJECT_NAME"],
            )
        )
        df.to_sql(
            name=table_name, schema=schema, con=engine, if_exists=if_exists, index=True
        )
