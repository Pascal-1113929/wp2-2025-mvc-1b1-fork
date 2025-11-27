from data.database import Database


class Disablity:
    def __init__(self, db_path: str):
        self.db = Database(db_path)

    def get_disabilities_by_profileid(self, profileid):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute("SELECT disability_id FROM profile_disabilities WHERE profile_id = ?", (profileid,))
            con.commit()
            rows = cur.fetchall()
            disability_ids = [row["disability_id"] for row in rows]

            disabilities = []
            for disability_id in disability_ids:
                cur.execute("SELECT * from disabilities WHERE id = ?", (disability_id,))
                con.commit()
                row = cur.fetchone()
                disability = dict(row)
                disabilities.append(disability)

            return disabilities

    def get_disability_ids_by_profileid(self, profileid):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute("SELECT disability_id FROM profile_disabilities WHERE profile_id = ?", (profileid,))
            con.commit()
            rows = cur.fetchall()
            disability_ids = [row["disability_id"] for row in rows]

            return disability_ids

    def get_disability_by_id(self, disability_id):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute("SELECT * from disabilities WHERE id = ?", (disability_id,))
            con.commit()
            disability = dict(cur.fetchone())
            return disability
