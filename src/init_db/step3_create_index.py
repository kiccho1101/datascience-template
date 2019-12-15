from src.db.services import DBServices


def create_index():
    db = DBServices()

    db.exec_query("CREATE INDEX train_passenger_id_idx ON train (passenger_id);")
    db.exec_query("CREATE INDEX test_passenger_id_idx ON test (passenger_id);")
