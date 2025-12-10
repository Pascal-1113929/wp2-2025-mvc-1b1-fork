from data.database import Database


class Disablity:
    def __init__(self, db_path: str):
        self.db = Database(db_path)

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

    def get_disability_list_by_studyid(self, studyid):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute("SELECT disabilities.id as id, disabilities.category as category, disabilities.name as name "
                        "FROM disabilities "
                        "INNER JOIN study_disabilities ON disabilities.id = study_disabilities.disability_id "
                        "WHERE study_disabilities.study_id = ?", (studyid,))
            con.commit()
            result = cur.fetchall()

            disability_list = []
            for row in result:
                disability_list.append(dict(row))

            return disability_list

    def get_disability_list_by_profileid(self, profileid):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute("SELECT disabilities.id as id, disabilities.category as category, disabilities.name as name "
                        "FROM disabilities "
                        "INNER JOIN study_disabilities ON disabilities.id = profile_disabilities.disability_id "
                        "WHERE profile_disabilities.profile_id = ?", (profileid,))
            con.commit()
            result = cur.fetchall()

            disability_list = []
            for row in result:
                disability_list.append(dict(row))

            return disability_list