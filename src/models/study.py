from data.database import Database
from datetime import datetime


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
            study_list = cur.fetchall()

            new_study_list = []
            for study in study_list:
                study_dict = dict(study)
                # This is needed fo the narrator pronounces the date correctly
                study_dict["start_date"] = datetime.strptime(study_dict["start_date"], "%Y-%m-%d")
                study_dict["end_date"] = datetime.strptime(study_dict["end_date"], "%Y-%m-%d")
                study_dict["start_date"] = study_dict["start_date"].strftime("%d-%m-%Y")
                study_dict["end_date"] = study_dict["end_date"].strftime("%d-%m-%Y")
                new_study_list.append(study_dict)

            return new_study_list

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
            try:
                study_id = row["study_id"]
            except TypeError:
                study_id = None
            return study_id

    def get_available_study_by_id(self, study_id: int):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM studies WHERE available=1 AND id=?", (study_id,))
            con.commit()
            return dict(cur.fetchone())

    def get_study_by_id(self, study_id: int):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM studies WHERE id=?", (study_id,))
            con.commit()
            return dict(cur.fetchone())

    def create(self, org_id, data):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute("""INSERT INTO studies (organization_id, title, description, study_type, age_min, age_max, reward, start_date, end_date, status_id, available, has_reward)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (org_id, data.get("title"), data.get("description"), data.get("type"), data.get("min_age"),
                  data.get("max_age"), data.get("reward"), data.get("start_date"), data.get("end_date"), 1, 1,
                  1 if data.get("reward") else 0))
            con.commit()
            return cur.lastrowid

    def create_with_organisation(self, organization_id, data):
        if data.get("reward") == "":
            data['has_reward'] = 0

        return self.create(
            org_id=organization_id,
            data=data
        )