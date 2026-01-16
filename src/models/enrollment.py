from data.database import Database


class Enrollment:
    def __init__(self, db_path: str = None):
        self.db = Database(db_path)

    def count_all(self):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute("SELECT COUNT() FROM enrollments")
            con.commit()
            return cur.fetchone()

    def count_by_user_id(self, user_id):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute("SELECT COUNT() FROM enrollments INNER JOIN profiles ON profiles.id == enrollments.profile_id "
                        "WHERE profiles.user_id == ?", (user_id,))
            con.commit()
            return cur.fetchone()

    def count_by_organization_id(self, organization_id):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute("SELECT count() FROM enrollments "
                        "INNER JOIN studies ON enrollments.study_id == studies.id "
                        "WHERE studies.organization_id == ?", (organization_id,))
            con.commit()
            return cur.fetchone()

    def create(self, study_id, profile_id, status):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute(
                "INSERT INTO enrollments (study_id, profile_id, status_id) VALUES (?, ?, ?)",
                (study_id, profile_id, status),
            )
            con.commit()

    def get_enrolments_by_study_id(self, study_id: int, status_id):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute(
                "SELECT * FROM enrollments WHERE study_id = ? and status_id = ?",
                (study_id, status_id),
            )
            con.commit()

            enrollment_list = cur.fetchall()

            new_enrollment_list = []
            for enrollment in enrollment_list:
                enrollment_dict = dict(enrollment)
                new_enrollment_list.append(enrollment_dict)

            return new_enrollment_list

    def set_enrollment_status(self, enrollment_id, status):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute(
                "UPDATE enrollments SET status_id = ? WHERE id = ?",
                (status, enrollment_id),
            )
            con.commit()
            return cur.lastrowid

    def get_enrollments_by_status(self, status_id):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute(
                """
                SELECT enrollments.*, studies.title as study_title, profiles.first_name as first_name,
                       profiles.last_name as last_name, profiles.user_id as user_id
                FROM enrollments
                INNER JOIN studies ON enrollments.study_id = studies.id
                INNER JOIN profiles ON enrollments.profile_id = profiles.id
                WHERE enrollments.status_id = ?
            """,
                (status_id,),
            )
            con.commit()

            enrollment_list = cur.fetchall()

            new_enrollment_list = []
            for enrollment in enrollment_list:
                enrollment_dict = dict(enrollment)
                new_enrollment_list.append(enrollment_dict)

            return new_enrollment_list

    def get_enrolments_by_profile_id(self, profile_id: int):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM enrollments WHERE profile_id = ?", (profile_id,))
            con.commit()

            enrollment_list = cur.fetchall()

            new_enrollment_list = []
            for enrollment in enrollment_list:
                enrollment_dict = dict(enrollment)
                new_enrollment_list.append(enrollment_dict)

            return new_enrollment_list

    def delete_enrollment(self, study_id: int, profile_id: int):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute(
                "DELETE FROM enrollments WHERE study_id = ? AND profile_id = ?",
                (study_id, profile_id),
            )
            con.commit()

    def enrolment_check(self, study_id: int, profile_id: int):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute(
                "SELECT * FROM enrollments WHERE study_id = ? and profile_id = ?",
                (study_id, profile_id),
            )
            con.commit()
            enrolment = cur.fetchone()
            if enrolment:
                return True
            else:
                return False

    def get_user_id_by_enrollment_id(self, enrollment_id):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute(
                "SELECT user_id FROM enrollments "
                "INNER JOIN profiles on profiles.id == enrollments.profile_id "
                "WHERE enrollments.id = ?",
                (enrollment_id,),
            )
            con.commit()
            row = cur.fetchone()
            return row["user_id"]
