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

    def create(self, study_id, profile_id, status):
        with self.db.connect () as con:
            cur = con.cursor()
            cur.execute(
                "INSERT INTO enrollments (study_id, profile_id, status_id) VALUES (?, ?, ?)",
                (study_id, profile_id, status)
            )
            con.commit()

    def get_enrolments_by_study_id(self, study_id: int, status_id):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM enrollments WHERE study_id = ? and status_id = ?", (study_id, status_id))
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
            cur.execute("DELETE FROM enrollments WHERE study_id = ? AND profile_id = ?", (study_id, profile_id))
            con.commit()

    def enrolment_check(self, study_id: int, profile_id: int):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM enrollments WHERE study_id = ? and profile_id = ?", (study_id, profile_id))
            con.commit()
            enrolment = cur.fetchone()
            if enrolment:
                return True
            else:
                return False
