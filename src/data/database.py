import os
import sqlite3

BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, "app.db")

class Database:
    def __init__(self, path: str):
        self.path = path
        self._setup_tables()

    def connect(self):
        con = sqlite3.connect(self.path)
        con.row_factory = sqlite3.Row
        con.execute('PRAGMA foreign_keys = ON')
        return con

    def _setup_tables(self):
        with self.connect() as con:
            cur = con.cursor()

            # ORGANIZATIONS
            cur.execute('''
                CREATE TABLE IF NOT EXISTS organizations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    type TEXT CHECK (type IN ('commercieel','non-profit')),
                    website TEXT,
                    description TEXT,
                    contact_person TEXT,
                    email TEXT,
                    phone TEXT,
                    details TEXT
                )
            ''')

            # USERS
            cur.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL CHECK (role IN ('expert','admin','organization')),
                    status TEXT NOT NULL DEFAULT 'nieuw' CHECK (status IN ('nieuw','goedgekeurd')),
                    organization_id INTEGER,
                    FOREIGN KEY (organization_id) REFERENCES organizations(id)
                )
            ''')

            # DISABILITIES
            cur.execute('''
                CREATE TABLE IF NOT EXISTS disabilities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    name TEXT NOT NULL,
                    UNIQUE(category, name)
                )
            ''')

            # PROFILES (Ervaringsdeskundigen)
            cur.execute('''
                CREATE TABLE IF NOT EXISTS profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL UNIQUE,
                    first_name TEXT,
                    last_name TEXT,
                    postcode TEXT,
                    gender TEXT,
                    phone TEXT,
                    birth_date TEXT,                                    -- ISO yyyy-mm-dd
                    assistive_tools TEXT,
                    intro TEXT,
                    notes TEXT,
                    agreed_terms INTEGER NOT NULL DEFAULT 0,            -- 0/1
                    has_guardian INTEGER NOT NULL DEFAULT 0,            -- 0/1
                    guardian_name TEXT,
                    guardian_email TEXT,
                    guardian_phone TEXT,
                    contact_preference TEXT CHECK (contact_preference IN ('telefoon','e-mail')),
                    preferred_study_type TEXT CHECK (preferred_study_type IN ('telefonisch','online','op locatie')),
                    availability TEXT,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )
            ''')

            # PROFILE ↔ DISABILITY
            cur.execute('''
                CREATE TABLE IF NOT EXISTS profile_disabilities (
                    profile_id INTEGER NOT NULL,
                    disability_id INTEGER NOT NULL,
                    PRIMARY KEY (profile_id, disability_id),
                    FOREIGN KEY(profile_id) REFERENCES profiles(id) ON DELETE CASCADE,
                    FOREIGN KEY(disability_id) REFERENCES disabilities(id) ON DELETE CASCADE
                )
            ''')

            # STUDIES (Onderzoeken)
            cur.execute('''
                CREATE TABLE IF NOT EXISTS studies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    organization_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'nieuw' CHECK (status IN ('nieuw','goedgekeurd','afgekeurd','gesloten')),
                    available INTEGER NOT NULL DEFAULT 1,                -- 0/1
                    description TEXT,
                    start_date TEXT,                                     -- ISO yyyy-mm-dd
                    end_date TEXT,                                       -- ISO yyyy-mm-dd
                    study_type TEXT CHECK (study_type IN ('telefonisch','online','op locatie')),
                    location TEXT,
                    has_reward INTEGER NOT NULL DEFAULT 0,               -- 0/1
                    reward TEXT,
                    age_min INTEGER,
                    age_max INTEGER,
                    FOREIGN KEY(organization_id) REFERENCES organizations(id)
                )
            ''')

            # Ensure uniqueness for study seeds (idempotency)
            try:
                cur.execute('CREATE UNIQUE INDEX IF NOT EXISTS ux_studies_org_title_start '
                            'ON studies(organization_id, title, start_date)')
            except sqlite3.OperationalError:
                # If duplicates already exist, the index creation can fail; keep going.
                pass

            # STUDY ↔ DISABILITY (doelgroep)
            cur.execute('''
                CREATE TABLE IF NOT EXISTS study_disabilities (
                    study_id INTEGER NOT NULL,
                    disability_id INTEGER NOT NULL,
                    PRIMARY KEY (study_id, disability_id),
                    FOREIGN KEY(study_id) REFERENCES studies(id) ON DELETE CASCADE,
                    FOREIGN KEY(disability_id) REFERENCES disabilities(id) ON DELETE CASCADE
                )
            ''')

            # ENROLLMENTS (Inschrijvingen)
            cur.execute('''
                CREATE TABLE IF NOT EXISTS enrollments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    study_id INTEGER NOT NULL,
                    profile_id INTEGER NOT NULL,
                    status TEXT NOT NULL DEFAULT 'nieuw' CHECK (status IN ('nieuw','goedgekeurd','afgekeurd')),
                    created_at TEXT DEFAULT (DATE('now')),
                    UNIQUE(study_id, profile_id),
                    FOREIGN KEY(study_id) REFERENCES studies(id) ON DELETE CASCADE,
                    FOREIGN KEY(profile_id) REFERENCES profiles(id) ON DELETE CASCADE
                )
            ''')

            # Indexes
            cur.execute('CREATE INDEX IF NOT EXISTS idx_users_status_role ON users(status, role)')
            cur.execute('CREATE INDEX IF NOT EXISTS idx_profiles_birthdate ON profiles(birth_date)')
            cur.execute('CREATE INDEX IF NOT EXISTS idx_studies_status_dates ON studies(status, start_date, end_date)')
            cur.execute('CREATE INDEX IF NOT EXISTS idx_enrollments_study ON enrollments(study_id)')
            cur.execute('CREATE INDEX IF NOT EXISTS idx_enrollments_profile ON enrollments(profile_id)')

            # ---------- SEED DATA ----------
            # Organizations
            cur.executemany('''
                INSERT OR IGNORE INTO organizations
                (id, name, type, website, description, contact_person, email, phone, details)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', [
                (1, 'Stichting Accessibility', 'non-profit', 'https://www.accessibility.nl',
                 'Stichting voor digitale toegankelijkheid.', 'Team Onderzoek',
                 'info@accessibility.nl', '+31 20 123 4567', None),
                (2, 'Albert Heijn', 'commercieel', 'https://www.ah.nl',
                 'Supermarktketen, UX research.', 'Research Team',
                 'onderzoek@ah.nl', '+31 88 659 2222', None),
                (3, 'VGZ', 'commercieel', 'https://www.vgz.nl',
                 'Zorgverzekeraar, klantonderzoek.', 'Onderzoeksteam',
                 'onderzoek@vgz.nl', '+31 24 123 4567', None),
            ])

            # Users
            cur.executemany('''
                INSERT OR IGNORE INTO users (email, password, role, status, organization_id)
                VALUES (?, ?, ?, ?, ?)
            ''', [
                ("admin@hub.com", "admin", "admin", "goedgekeurd", None),
                ("org-ah@hub.com", "secret", "organization", "goedgekeurd", 2),
                ("sanne@example.com", "secret", "expert", "goedgekeurd", None),
                ("jamal@example.com", "secret", "expert", "goedgekeurd", None),
                ("lotte@example.com", "secret", "expert", "nieuw", None),
            ])

            # Disabilities (complete list from spec)
            cur.executemany('''
                INSERT OR IGNORE INTO disabilities (category, name) VALUES (?, ?)
            ''', [
                # Auditief
                ('Auditief','Doof'),
                ('Auditief','Slechthorend'),
                ('Auditief','Doofblind'),
                # Visueel
                ('Visueel','Blind'),
                ('Visueel','Slechtziend'),
                ('Visueel','Kleurenblind'),
                ('Visueel','Doofblind'),
                # Motorisch/lichamelijk
                ('Motorisch/lichamelijk','Amputatie en mismaaktheid'),
                ('Motorisch/lichamelijk','Artritis'),
                ('Motorisch/lichamelijk','Fibromyalgie'),
                ('Motorisch/lichamelijk','Reuma'),
                ('Motorisch/lichamelijk','Verminderde handvaardigheid'),
                ('Motorisch/lichamelijk','Spierdystrofie'),
                ('Motorisch/lichamelijk','RSI'),
                ('Motorisch/lichamelijk','Tremor en Spasmen'),
                ('Motorisch/lichamelijk','Quadriplegie/tetraplegie'),
                # Cognitief/neurologisch
                ('Cognitief/neurologisch','ADHD'),
                ('Cognitief/neurologisch','Autisme'),
                ('Cognitief/neurologisch','Dyslexie'),
                ('Cognitief/neurologisch','Dyscalculie'),
                ('Cognitief/neurologisch','Leerstoornis'),
                ('Cognitief/neurologisch','Geheugenbeperking'),
                ('Cognitief/neurologisch','Multiple Sclerose'),
                ('Cognitief/neurologisch','Epilepsie'),
                ('Cognitief/neurologisch','Migraine'),
            ])

            # Profiles
            cur.execute('''
                INSERT OR IGNORE INTO profiles
                (user_id, first_name, last_name, postcode, gender, phone, birth_date,
                 assistive_tools, intro, notes, agreed_terms, has_guardian,
                 guardian_name, guardian_email, guardian_phone, contact_preference,
                 preferred_study_type, availability)
                SELECT id, 'Sanne','Jansen','1012AB','V','+31 6 11111111','1990-04-15',
                       'Screenreader','Ik test graag webshops.', NULL, 1, 0,
                       NULL, NULL, NULL, 'e-mail', 'online', 'Ma-Wo overdag'
                FROM users WHERE email='sanne@example.com'
            ''')
            cur.execute('''
                INSERT OR IGNORE INTO profiles
                (user_id, first_name, last_name, postcode, gender, phone, birth_date,
                 assistive_tools, intro, notes, agreed_terms, has_guardian,
                 guardian_name, guardian_email, guardian_phone, contact_preference,
                 preferred_study_type, availability)
                SELECT id, 'Jamal','El Idrissi','3032CD','M','+31 6 22222222','1988-08-20',
                       'Toetsenbord-only','Focus op formulieren.', NULL, 1, 0,
                       NULL, NULL, NULL, 'telefoon', 'op locatie', 'Do-Vr middag'
                FROM users WHERE email='jamal@example.com'
            ''')
            cur.execute('''
                INSERT OR IGNORE INTO profiles
                (user_id, first_name, last_name, postcode, gender, phone, birth_date,
                 assistive_tools, intro, notes, agreed_terms, has_guardian,
                 guardian_name, guardian_email, guardian_phone, contact_preference,
                 preferred_study_type, availability)
                SELECT id, 'Lotte','van Dijk','3511EF','V','+31 6 33333333','2005-01-10',
                       NULL,'Student, veel tijd in de avond.','Mogelijk toezichthouder nodig.', 1, 0,
                       NULL, NULL, NULL, 'e-mail', 'telefonisch', 'Avonden en weekend'
                FROM users WHERE email='lotte@example.com'
            ''')

            # Profile ↔ Disabilities
            cur.execute('''
                INSERT OR IGNORE INTO profile_disabilities (profile_id, disability_id)
                SELECT p.id, d.id
                FROM profiles p
                JOIN users u ON u.id=p.user_id
                JOIN disabilities d ON d.name='Blind'
                WHERE u.email='sanne@example.com'
            ''')
            cur.execute('''
                INSERT OR IGNORE INTO profile_disabilities (profile_id, disability_id)
                SELECT p.id, d.id
                FROM profiles p
                JOIN users u ON u.id=p.user_id
                JOIN disabilities d ON d.name='Verminderde handvaardigheid'
                WHERE u.email='jamal@example.com'
            ''')
            cur.execute('''
                INSERT OR IGNORE INTO profile_disabilities (profile_id, disability_id)
                SELECT p.id, d.id
                FROM profiles p
                JOIN users u ON u.id=p.user_id
                JOIN disabilities d ON d.name='Dyslexie'
                WHERE u.email='lotte@example.com'
            ''')

            # ---- Seed studies only if table empty (prevents duplicates) ----
            cur.execute('SELECT COUNT(*) AS c FROM studies')
            if cur.fetchone()['c'] == 0:
                # Studies
                cur.executemany('''
                    INSERT OR IGNORE INTO studies
                    (organization_id, title, status, available, description, start_date, end_date, study_type,
                     location, has_reward, reward, age_min, age_max)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', [
                    (2, 'Gebruikersonderzoek AH app', 'goedgekeurd', 1,
                     'Test de toegankelijkheid van de boodschappen-app.',
                     '2025-11-15', '2025-12-15', 'online',
                     None, 1, '€25 cadeaubon', 18, 75),
                    (1, 'Toegankelijkheid gemeentelijke website', 'nieuw', 1,
                     'Toptaken testen met screenreader.',
                     '2025-12-01', '2026-01-15', 'op locatie',
                     'Amsterdam', 1, '€50 vergoeding + reiskosten', 18, 99),
                    (3, 'Zorgportaal formulierenreview', 'goedgekeurd', 1,
                     'Formulieren doorlopen met motorische beperking.',
                     '2025-11-20', '2025-12-20', 'telefonisch',
                     None, 1, "€50 vergoeding", 21, 80),
                ])

                # Study ↔ Disabilities
                cur.execute('''
                    INSERT OR IGNORE INTO study_disabilities (study_id, disability_id)
                    SELECT s.id, d.id
                    FROM studies s
                    JOIN disabilities d ON d.name IN ('Slechtziend','Kleurenblind')
                    WHERE s.title='Gebruikersonderzoek AH app'
                ''')
                cur.execute('''
                    INSERT OR IGNORE INTO study_disabilities (study_id, disability_id)
                    SELECT s.id, d.id
                    FROM studies s
                    JOIN disabilities d ON d.name IN ('Blind','Slechtziend')
                    WHERE s.title='Toegankelijkheid gemeentelijke website'
                ''')
                cur.execute('''
                    INSERT OR IGNORE INTO study_disabilities (study_id, disability_id)
                    SELECT s.id, d.id
                    FROM studies s
                    JOIN disabilities d ON d.name IN ('Verminderde handvaardigheid','RSI')
                    WHERE s.title='Zorgportaal formulierenreview'
                ''')

                # Enrollments for seeded studies
                cur.execute('''
                    INSERT OR IGNORE INTO enrollments (study_id, profile_id, status)
                    SELECT s.id, p.id, 'nieuw'
                    FROM studies s
                    JOIN profiles p ON 1=1
                    JOIN users u ON u.id=p.user_id
                    WHERE s.title='Gebruikersonderzoek AH app' AND u.email='sanne@example.com'
                ''')

            con.commit()
