from init_db.step0_col_name_to_snake_case import col_name_to_snake_case
from init_db.step1_create_schema import create_schema
from init_db.step2_insert_data import insert_data
from init_db.step3_create_index import create_index
from src.utils.services import timer


def init_db():

    with timer("Column names to snake case"):
        col_name_to_snake_case()

    with timer("Create schema"):
        create_schema()

    with timer("Insert data"):
        insert_data()

    with timer("Create index"):
        create_index()
