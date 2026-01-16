from data.database import Database


class Organization:
    def __init__(self, db_path: str = None):
        self.db = Database(db_path)

    def count_all(self):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute("SELECT COUNT() FROM organizations")
            con.commit()
            return cur.fetchone()

    def create(self, name, type, website, description, contact_person, email, phone):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute(
                """
                INSERT INTO organizations
                (name, type, website, description, contact_person, email, phone, details)
                VALUES (?, ?, ?, ?, ?, ?, ?, NULL)
                """
                , (name, type, website, description, contact_person, email, phone)
            )
            con.commit()
            return cur.lastrowid

    def get_organization_list(self):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM organizations")
            con.commit()
            rows = cur.fetchall()

            organization_list = []
            for row in rows:
                organization_list.append(dict(row))

            return organization_list

    def get_organization_userid(self, organization_id: int):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute(
                "SELECT id FROM users WHERE organization_id = ?", (organization_id,)
            )
            con.commit()
            row = cur.fetchone()
            if row is None:
                return None
            else:
                return row

    def get_organization_by_id(self, organization_id: int):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM organizations WHERE id = ?", (organization_id,))
            con.commit()
            return cur.fetchone()

    def get_email_by_id(self, id):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute("SELECT email FROM organizations WHERE id = ?", (id,))
            con.commit()
            row = dict(cur.fetchone())
            return row["email"]

    def get_name_by_id(self, id):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute("SELECT name FROM organizations WHERE id = ?", (id,))
            con.commit()
            row = dict(cur.fetchone())
            return row["name"]
