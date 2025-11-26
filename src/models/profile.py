from data.database import Database

class Profile:
    def __init__(self, db_path: str):
        self.db = Database(db_path)

    def get_profile_by_userid(self, userid: int):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM profiles WHERE user_id = ?", (userid,))
            con.commit()
            return cur.fetchone()