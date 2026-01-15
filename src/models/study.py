from data.database import Database
from datetime import datetime
from models.status import Status


class Study:
    def __init__(self, db_path: str = None):
        self.db = Database(db_path)
        self.statuses = Status(db_path)

    def count_all(self):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute("SELECT COUNT() FROM studies")
            con.commit()
            return cur.fetchone()

    def set_research_status(self, user_id, status):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute(
                "UPDATE studies SET status_id = ? WHERE id = ?",
                (status, user_id),
            )
            con.commit()
            return cur.lastrowid

    def get_study_by_organization_id(self, organization_id: int):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute(
                "SELECT * FROM studies WHERE organization_id=?", (organization_id,)
            )
            con.commit()
            study_list = cur.fetchall()

            new_study_list = []
            for study in study_list:
                study_dict = dict(study)
                # This is needed fo the narrator pronounces the date correctly
                study_dict["start_date"] = datetime.strptime(
                    study_dict["start_date"], "%Y-%m-%d"
                )
                study_dict["end_date"] = datetime.strptime(
                    study_dict["end_date"], "%Y-%m-%d"
                )
                study_dict["start_date"] = study_dict["start_date"].strftime("%d-%m-%Y")
                study_dict["end_date"] = study_dict["end_date"].strftime("%d-%m-%Y")
                study_dict["status"] = self.statuses.get_status_name(
                    study_dict["status_id"]
                )
                new_study_list.append(study_dict)

            return new_study_list

    def get_all_available(self):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM studies WHERE available=1")
            con.commit()
            study_list = cur.fetchall()

            new_study_list = []
            for study in study_list:
                study_dict = dict(study)
                new_study_list.append(study_dict)

            return new_study_list

    def get_study_id_by_disability_id(self, disability_id: int):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute(
                "SELECT study_id FROM study_disabilities WHERE disability_id=?",
                (disability_id,),
            )
            con.commit()
            study_id_list = cur.fetchall()

            new_study_id_list = []
            for study_id in study_id_list:
                study_id_dict = dict(study_id)
                study_id = study_id_dict["study_id"]
                # This is needed fo the narrator pronounces the date correctly
                new_study_id_list.append(study_id)

            return new_study_id_list

    def get_available_study_by_id(self, study_id: int):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute(
                "SELECT * FROM studies "
                "WHERE available=1 "
                "AND DATE(end_date) > DATE('now') "
                "AND id=? ",
                (study_id,),
            )
            con.commit()
            row = cur.fetchone()
            try:
                return dict(row)
            except TypeError:
                return None

    def get_available_enrolled_study_by_id(self, study_id: int):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute(
                "SELECT * FROM studies "
                "WHERE available=1 "
                "AND DATE(end_date) > DATE('now') "
                "AND id=? ",
                (study_id,),
            )
            con.commit()
            row = cur.fetchone()
            try:
                return dict(row)
            except TypeError:
                return None

    def get_study_by_id(self, study_id: int):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM studies WHERE id=?", (study_id,))
            con.commit()
            return dict(cur.fetchone())

    def get_study_by_status(self, status_id: int):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM studies WHERE status_id=?", (status_id,))
            con.commit()
            study_status_id_list = cur.fetchall()

            new_study_status_id_list = []
            for study_status_id in study_status_id_list:
                new_study_status_id_list.append(dict(study_status_id))

            return new_study_status_id_list

    def create(self, org_id, data):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute(
                """INSERT INTO studies (organization_id, title, description, study_type, location,age_min, age_max, reward, start_date, end_date, status_id, available, has_reward)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    org_id,
                    data.get("title"),
                    data.get("description"),
                    data.get("type"),
                    data.get("location"),
                    data.get("min_age"),
                    data.get("max_age"),
                    data.get("reward"),
                    data.get("start_date"),
                    data.get("end_date"),
                    1,
                    1,
                    1 if data.get("reward") else 0,
                ),
            )
            con.commit()
            return cur.lastrowid

    def create_with_organisation(self, organization_id, data):
        if data.get("reward") == "":
            data["has_reward"] = 0

        return self.create(org_id=organization_id, data=data)

    def get_organization_id_by_id(self, id):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute(
                "SELECT organization_id FROM studies WHERE id=?", (id,)
            )
            row = dict(cur.fetchone())
            return row["organization_id"]

    def update_study(self, study_id: int, title: str,
                     description: str, start_date: str, end_date: str, study_type: str,
                     location: str | None, has_reward: int, reward: str,
                     age_min: int, age_max: int):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute("""
                        UPDATE studies
                        SET title       = ?,
                            description = ?,
                            start_date  = ?,
                            end_date    = ?,
                            study_type  = ?,
                            location    = ?,    
                            has_reward  = ?,
                            reward      = ?,
                            age_min     = ?,
                            age_max     = ?
                        WHERE id = ?
                        """, (
                            title,
                            description,
                            start_date,
                            end_date,
                            study_type,
                            location,
                            has_reward,
                            reward,
                            age_min,
                            age_max,
                            study_id
                        ))
            con.commit()
            return cur.lastrowid

