from src.db.services import DBServices


def create_index():
    db = DBServices()

    db.exec_query("CREATE INDEX IF NOT EXISTS train_index_idx ON train (index);")
    db.exec_query("CREATE INDEX IF NOT EXISTS test_index_idx ON test (index);")
    db.exec_query(
        "CREATE INDEX IF NOT EXISTS train_passenger_id_idx ON train (passenger_id);"
    )
    db.exec_query(
        "CREATE INDEX IF NOT EXISTS test_passenger_id_idx ON test (passenger_id);"
    )
