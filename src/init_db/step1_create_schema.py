import glob
from src.db.services import DBServices


def create_schema():
    db = DBServices()
    dirs = glob.glob("./input/*")

    for dir_name in dirs:
        schema = dir_name.split("/")[-1]
        db.exec_query("CREATE SCHEMA IF NOT EXISTS {};".format(schema))
