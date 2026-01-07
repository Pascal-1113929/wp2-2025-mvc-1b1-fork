from data.database import Database


class Profile:
    def __init__(self, db_path: str):
        self.db = Database(db_path)

    def get_profile_by_userid(self, userid: int):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM profiles WHERE user_id = ?", (userid,))
            con.commit()
            try:
                profile = dict(cur.fetchone())
            except TypeError:
                profile = None

            return profile

    def create(self, userid: int, firstname, lastname, gender, postal, intro, phone, birthdate, atools,
               contact, researchtype, availability, aterms):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute("""
            INSERT INTO profiles (user_id, first_name, last_name, postcode, gender, phone, birth_date, assistive_tools, 
                                  intro, agreed_terms, contact_preference, preferred_study_type, availability)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""", (userid, firstname, lastname, postal, gender, phone,
                        birthdate, atools, intro, aterms, contact, researchtype, availability))
            con.commit()
            return cur.lastrowid

    def get_user_name(self, userid):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM profiles WHERE user_id = ?", (userid,))
            con.commit()
            try:
                profile = dict(cur.fetchone())
                return profile["first_name"] + " " + profile["last_name"]

            except TypeError:
                return None
