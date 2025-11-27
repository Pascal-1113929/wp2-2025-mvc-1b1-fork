from data.database import Database


class Study:
    def __init__(self, db_path: str):
        self.db = Database(db_path)

    def count_all(self):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute("SELECT COUNT() FROM studies")
            con.commit()
            return cur.fetchone()

    def get_study_by_organization_id(self, organization_id: int):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM studies WHERE organization_id=?", (organization_id,))
            con.commit()
            return cur.fetchall()

    def get_all_available(self):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM studies WHERE available=1")
            con.commit()
            return cur.fetchall()

    def get_study_id_by_disability_id(self, disability_id: list):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute("SELECT study_id FROM study_disabilities WHERE disability_id=?", (disability_id,))
            con.commit()
            row = cur.fetchone()
            study_id = row["study_id"]
            return study_id

    def get_available_study_by_id(self, study_id: int):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM studies WHERE available=1 AND id=?", (study_id,))
            con.commit()
            return dict(cur.fetchone())
