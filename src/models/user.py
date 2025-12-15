from data.database import Database


class User:
    def __init__(self, db_path: str):
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
            return dict(cur.fetchone())

    def create(self, email, password, organization_id=None, role="organization", status=1):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute(
                """
                INSERT INTO users (email, password, organization_id, role, status_id)
                VALUES (?, ?, ?, ?, ?)
            """,
                (email, password, organization_id, role, status),
            )
            con.commit()
            return cur.lastrowid

    def create_new_expert(self, email, password, role="expert", status=1):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute("""
                INSERT INTO users (email, password, role, status_id)
                VALUES (?, ?, ?, ?)
            """, (email, password, role, status))
            con.commit()
            return cur.lastrowid

    def get_user_by_id(self, user_id: int):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            con.commit()
            return cur.fetchone()

    def get_organization_id_by_userid(self, id: int):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute("SELECT organization_id FROM users WHERE id = ?", (id,))
            con.commit()
            return dict(cur.fetchone())