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

    def get_enrolments_by_study_id(self, study_id: int, status):
        #TODO: change status to staus id after enrolment create is done
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM enrollments WHERE study_id = ? and status = ?", (study_id, status))# QUESTIONS: Do we want this with an id?
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
