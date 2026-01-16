from data.database import Database


class Disablity:
    def __init__(self, db_path: str = None):
        self.db = Database(db_path)

    def get_all_disabilities(self):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM disabilities")
            rows = cur.fetchall()

            disability_list = []
            for row in rows:
                disability_list.append(dict(row))

            return disability_list

    def get_disability_ids_by_profileid(self, profileid):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute(
                "SELECT disability_id FROM profile_disabilities WHERE profile_id = ?",
                (profileid,),
            )
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

    def get_disability_list_by_studyid(self, studyid):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute(
                "SELECT disabilities.id as id, disabilities.category as category, disabilities.name as name "
                "FROM disabilities "
                "INNER JOIN study_disabilities ON disabilities.id = study_disabilities.disability_id "
                "WHERE study_disabilities.study_id = ?",
                (studyid,),
            )
            con.commit()
            result = cur.fetchall()

            disability_list = []
            for row in result:
                disability_list.append(dict(row))

            return disability_list

    def create_profile_disabilities(self, profileid, disability_id):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute(
                """
            INSERT INTO profile_disabilities (profile_id, disability_id)
                        Values (?, ?)
                        """,
                (profileid, disability_id),
            )
            con.commit()
            return cur.lastrowid

    def update_profile_disabilities(self, profileid, disability_id):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute(
                "UPDATE profile_disabilities SET disability_id = ? WHERE profile_id = ?",
                (disability_id, profileid),
            )
            con.commit()
            return cur.lastrowid

    def update_study_disabilities(self, study_id, new_disabilities):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute("SELECT disability_id FROM study_disabilities WHERE study_id = ?", (study_id,))
            current_ids = {row[0] for row in cur.fetchall()}

            new_ids = {d for d in new_disabilities}

            if current_ids != new_ids:
                cur.execute("DELETE FROM study_disabilities WHERE study_id = ?", (study_id,))
                for d_id in new_ids:
                    cur.execute(
                        "INSERT INTO study_disabilities (study_id, disability_id) VALUES (?, ?)",
                        (study_id, d_id)
                    )
                con.commit()

    def create_study_disabilities(self, study_id, disability_id):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute(
                """
            INSERT INTO study_disabilities (study_id, disability_id)
                        Values (?, ?)
                        """,
                (study_id, disability_id),
            )
            con.commit()
            return cur.lastrowid

    def get_disability_list_by_profileid(self, profileid):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute(
                "SELECT disabilities.id as id, disabilities.category as category, disabilities.name as name "
                "FROM disabilities "
                "INNER JOIN profile_disabilities ON disabilities.id = profile_disabilities.disability_id "
                "WHERE profile_disabilities.profile_id = ?",
                (profileid,),
            )
            con.commit()
            result = cur.fetchall()

            disability_list = []
            for row in result:
                disability_list.append(dict(row))

            return disability_list
