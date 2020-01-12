from src.db.init.step0_col_name_to_snake_case import col_name_to_snake_case
from src.db.init.step1_create_schema import create_schema
from src.db.init.step2_insert_data import insert_data
from src.db.init.step3_create_index import create_index
from src.utils.services import timer


def init_db(service_name: str):

    if service_name == "snake_case":
        with timer("Column names to snake case"):
            col_name_to_snake_case()

    if service_name == "schema":
        with timer("Create schema"):
            create_schema()

    if service_name == "insert":
        with timer("Insert data"):
            insert_data()

    if service_name == "index":
        with timer("Create index"):
            create_index()
