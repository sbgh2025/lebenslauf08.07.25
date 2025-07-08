import os
import sqlite3

# Speicherort: Datenbank soll im gleichen Ordner wie dieses Skript (lb_datenbank.py) liegen
base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, "lebenslauf.db")  # z. B. lb_datenbank/lebenslauf.sqlite

# Verbindung zur SQLite-Datenbank
conn = sqlite3.connect(db_path)

# Aktivieren der Fremdschlüsselunterstützung
conn.execute("PRAGMA foreign_keys = ON")
cursor = conn.cursor()

# Alle Tabellen erstellen
cursor.executescript("""
-- Tabelle: Bewerber
CREATE TABLE IF NOT EXISTS tbl_bewerber (
    bw_id INTEGER PRIMARY KEY AUTOINCREMENT,
    bw_vorname TEXT NOT NULL,
    bw_nachname TEXT NOT NULL,
    bw_geburtsdatum DATE,
    bw_strasse TEXT,
    bw_plz INTEGER,
    bw_ort TEXT,
    bw_mail TEXT,
    bw_telefon TEXT
);

-- Tabelle: Firma
CREATE TABLE IF NOT EXISTS tbl_firma (
    f_id INTEGER PRIMARY KEY AUTOINCREMENT,
    f_datum DATE NOT NULL,
    f_stellenbezeichnung TEXT NOT NULL,
    f_name TEXT NOT NULL,
    f_strasse TEXT,
    f_plz INTEGER,
    f_ort TEXT,
    f_mail TEXT,
    f_telefon TEXT
);

-- Tabelle: Bewerbung
CREATE TABLE IF NOT EXISTS tbl_bewerbung (
    bwg_id INTEGER PRIMARY KEY AUTOINCREMENT,
    bwg_bw_id INTEGER NOT NULL,
    bwg_f_id INTEGER NOT NULL,
    FOREIGN KEY (bwg_bw_id) REFERENCES tbl_bewerber(bw_id) ON DELETE CASCADE,
    FOREIGN KEY (bwg_f_id) REFERENCES tbl_firma(f_id) ON DELETE CASCADE
);

-- Tabelle: Arbeitgeber
CREATE TABLE IF NOT EXISTS tbl_arbeitgeber (
    ag_id INTEGER PRIMARY KEY AUTOINCREMENT,
    ag_datum_von DATE NOT NULL,
    ag_datum_bis DATE,
    ag_name TEXT NOT NULL,
    ag_zeit TEXT,
    ag_funktion TEXT,
    ag_ort TEXT,
    ag_leihfirma TEXT,
    ag_bemerkung TEXT
);

-- Tabelle: Zuordnung Bewerbung <-> Arbeitgeber
CREATE TABLE IF NOT EXISTS tbl_bwg_ag (
    bwg_ag_id INTEGER PRIMARY KEY AUTOINCREMENT,
    bwg_ag_ag_id INTEGER NOT NULL,
    bwg_ag_bwg_id INTEGER NOT NULL,
    FOREIGN KEY (bwg_ag_ag_id) REFERENCES tbl_arbeitgeber(ag_id) ON DELETE CASCADE,
    FOREIGN KEY (bwg_ag_bwg_id) REFERENCES tbl_bewerbung(bwg_id) ON DELETE CASCADE
);

-- Tabelle: Tätigkeit
CREATE TABLE IF NOT EXISTS tbl_taetigkeit (
    t_id INTEGER PRIMARY KEY AUTOINCREMENT,
    t_name TEXT NOT NULL
);

-- Tabelle: Tätigkeiten zu Arbeitgeberzuordnungen
CREATE TABLE IF NOT EXISTS tbl_bwg_ag_t (
    bwg_ag_t_id INTEGER PRIMARY KEY AUTOINCREMENT,
    bwg_ag_t_bwg_ag_id INTEGER NOT NULL,
    bwg_ag_t_t_id INTEGER NOT NULL,
    FOREIGN KEY (bwg_ag_t_bwg_ag_id) REFERENCES tbl_bwg_ag(bwg_ag_id) ON DELETE CASCADE,
    FOREIGN KEY (bwg_ag_t_t_id) REFERENCES tbl_taetigkeit(t_id) ON DELETE CASCADE
);

-- Tabelle: Ausbildung
CREATE TABLE IF NOT EXISTS tbl_ausbildung (
    ab_id INTEGER PRIMARY KEY AUTOINCREMENT,
    ab_datum_von DATE NOT NULL,
    ab_datum_bis DATE,
    ab_name_staette TEXT NOT NULL,
    ab_name_ausbildung TEXT NOT NULL,
    ab_abschluss TEXT,
    ab_zeit TEXT
);

-- Tabelle: Ausbildungsschwerpunkte
CREATE TABLE IF NOT EXISTS tbl_ab_schwerpunkt (
    ab_swp_id INTEGER PRIMARY KEY AUTOINCREMENT,
    ab_swp_name TEXT NOT NULL
);

-- Tabelle: Bewerbung <-> Ausbildung
CREATE TABLE IF NOT EXISTS tbl_bwg_ab (
    bwg_ab_id INTEGER PRIMARY KEY AUTOINCREMENT,
    bwg_ab_bwg_id INTEGER NOT NULL,
    bwg_ab_ab_id INTEGER NOT NULL,
    FOREIGN KEY (bwg_ab_bwg_id) REFERENCES tbl_bewerbung(bwg_id) ON DELETE CASCADE,
    FOREIGN KEY (bwg_ab_ab_id) REFERENCES tbl_ausbildung(ab_id) ON DELETE CASCADE
);


-- Tabelle: Zuordnung Bewerbung <-> Ausbildung <-> Schwerpunkt
CREATE TABLE IF NOT EXISTS tbl_bwg_ab_swp (
    bwg_ab_swp_id INTEGER PRIMARY KEY AUTOINCREMENT,
    bwg_ab_swp_bwg_ab_id INTEGER NOT NULL,
    bwg_ab_swp_ab_swp_id INTEGER NOT NULL,
    FOREIGN KEY (bwg_ab_swp_bwg_ab_id)
        REFERENCES tbl_bwg_ab(bwg_ab_id)
        ON DELETE CASCADE,
    FOREIGN KEY (bwg_ab_swp_ab_swp_id)
        REFERENCES tbl_ab_schwerpunkt(ab_swp_id)
        ON DELETE CASCADE
);


-- Tabelle: Kenntnisse
CREATE TABLE IF NOT EXISTS tbl_kenntnisse (
    k_id INTEGER PRIMARY KEY AUTOINCREMENT,
    k_name TEXT NOT NULL,
    k_stufe TEXT NOT NULL
);

-- Tabelle: Bewerbung <-> Kenntnisse
CREATE TABLE IF NOT EXISTS tbl_bwg_k (
    bwg_k_id INTEGER PRIMARY KEY AUTOINCREMENT,
    bwg_k_bwg_id INTEGER NOT NULL,
    bwg_k_k_id INTEGER NOT NULL,
    FOREIGN KEY (bwg_k_bwg_id) REFERENCES tbl_bewerbung(bwg_id) ON DELETE CASCADE,
    FOREIGN KEY (bwg_k_k_id) REFERENCES tbl_kenntnisse(k_id) ON DELETE CASCADE
);

-- Tabelle: Interessen
CREATE TABLE IF NOT EXISTS tbl_interessen (
    i_id INTEGER PRIMARY KEY AUTOINCREMENT,
    i_name TEXT NOT NULL
);

-- Tabelle: Bewerbung <-> Interessen
CREATE TABLE IF NOT EXISTS tbl_bwg_i (
    bwg_i_id INTEGER PRIMARY KEY AUTOINCREMENT,
    bwg_i_bwg_id INTEGER NOT NULL,
    bwg_i_i_id INTEGER NOT NULL,
    FOREIGN KEY (bwg_i_bwg_id) REFERENCES tbl_bewerbung(bwg_id) ON DELETE CASCADE,
    FOREIGN KEY (bwg_i_i_id) REFERENCES tbl_interessen(i_id) ON DELETE CASCADE
);
""")

# Änderungen speichern und Verbindung schließen
conn.commit()
conn.close()

print("Alle Tabellen wurden erfolgreich erstellt.")


