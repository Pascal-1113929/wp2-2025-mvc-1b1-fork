from data.database import Database


class User:
    def __init__(self, db_path: str = None):
        self.db = Database(db_path)

    def count_all(self):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute("SELECT COUNT() FROM users")
            con.commit()
            return cur.fetchone()

    def check_login(self, email, password):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute(
                "SELECT * FROM users WHERE email = ? AND password = ?",
                (email, password),
            )
            con.commit()
            row = cur.fetchone()
            if row:
                return dict(row)
            else:
                return None

    def get_users_by_status(self, status):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute(
                "SELECT * FROM users INNER JOIN profiles ON users.id = profiles.user_id WHERE users.status_id = ?",
                (status,),
            )
            con.commit()
            result = cur.fetchall()

            users = []
            for row in result:
                user = dict(row)
                users.append(user)

            return users

    def set_user_status(self, user_id, status, approve_notification=1):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute(
                "UPDATE users SET status_id = ?, approve_notification = ? WHERE id = ?",
                (status, approve_notification, user_id),
            )
            con.commit()
            return cur.lastrowid

    def set_user_approve_notifications(self, user_id, approve_notification=1):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute(
                "UPDATE users SET approve_notification = ? WHERE id = ?",
                (approve_notification, user_id),
            )
            con.commit()
            return cur.lastrowid

    def create(
            self, email, password, organization_id=None, role="organization", status=1, approve_notification=1
    ):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute(
                """
                INSERT INTO users (email, password, organization_id, role, status_id, approve_notification)
                VALUES (?, ?, ?, ?, ?)
            """,
                (email, password, organization_id, role, status, approve_notification),
            )
            con.commit()
            return cur.lastrowid

    def create_new_expert(self, email, password, role="expert", status=1):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute(
                """
                INSERT INTO users (email, password, role, status_id)
                VALUES (?, ?, ?, ?)
            """,
                (email, password, role, status),
            )
            con.commit()
            return cur.lastrowid

    def get_user_by_id(self, user_id: int):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            con.commit()
            row = cur.fetchone()
            try:
                return dict(row)
            except TypeError:
                return None

    def get_user_role_by_id(self, user_id: int):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute("SELECT role FROM users WHERE id = ?", (user_id,))
            con.commit()
            row = dict(cur.fetchone())
            return row["role"]

    def delete_expert(self, user_id: int, profile_class):
        with self.db.connect() as con:
            cur = con.cursor()
            profile = profile_class.get_profile_by_userid(user_id)
            profile_id = int(profile["id"])
            print(profile_id, type(profile_id))
            cur.execute(
                "DELETE FROM profile_disabilities WHERE profile_id = ?", (profile_id,)
            )
            cur.execute("DELETE FROM profiles WHERE id = ?", (profile_id,))
            cur.execute("DELETE FROM users WHERE id = ?", (user_id,))

    def update_email(self, user_id: int, email: str):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute("UPDATE users SET email = ? WHERE id = ?", (email, user_id))
            con.commit()
            return cur.lastrowid

    def get_organization_id_by_userid(self, id: int):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute("SELECT organization_id FROM users WHERE id = ?", (id,))
            con.commit()
            row = cur.fetchone()
            if row:
                return dict(row)
            else:
                return None

    def get_email_by_id(self, id: int):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute("SELECT email FROM users WHERE id = ?", (id,))
            con.commit()
            row = dict(cur.fetchone())
            return row["email"]
