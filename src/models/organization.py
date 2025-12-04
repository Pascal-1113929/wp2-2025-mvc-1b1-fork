from data.database import Database

class Organization:
    def __init__(self, db_path: str):
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
            cur.execute("""
                INSERT INTO organizations (name, type, website, description, contact_person, email, phone)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (name, type, website, description, contact_person, email, phone))
            con.commit()
            return cur.lastrowid

    def get_organization_by_id(self, organization_id: int):
        with self.db.connect() as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM organizations WHERE id = ?", (organization_id,))
            con.commit()
            return cur.fetchone()
