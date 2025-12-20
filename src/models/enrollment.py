from data.database import Database


class Enrollment:
    def __init__(self, db_path: str):
        self.db = Database(db_path)

    def count_all(self):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute("SELECT COUNT() FROM enrollments")
            con.commit()
            return cur.fetchone()
    
    def create(self, study_id, user_id, status):
        with self.db.connect () as con:
            cur = con.cursor()
            cur.execute(
                "INSERT INTO enrollments (study_id, user_id, status) VALUES (?, ?, ?)",
                (study_id, user_id, status)
            )
            con.commit()
        

