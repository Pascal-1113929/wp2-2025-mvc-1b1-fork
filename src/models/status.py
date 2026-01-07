from data.database import Database


class Status:
    def __init__(self, db_path: str):
        self.db = Database(db_path)

    def get_status_name(self, status_id):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute("SELECT 'status' FROM status where id = ?", (status_id,))
            con.commit()
            row = cur.fetchone()
            row = dict(row)
            print(row)
            return row["'status'"]

