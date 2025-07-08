import sqlite3
import tkinter as tk
from tkinter import ttk

def fetch_all(cursor, table):
    cursor.execute(f"SELECT * FROM {table}")
    return cursor.fetchall()

def get_column_names(cursor, table):
    cursor.execute(f"SELECT * FROM {table} LIMIT 1")
    return [desc[0] for desc in cursor.description]

def create_table_tab(notebook, title, columns, rows):
    # Vorherige Tabs löschen, damit nur ein Tab angezeigt wird
    for tab in notebook.tabs():
        notebook.forget(tab)

    frame = ttk.Frame(notebook)
    notebook.add(frame, text=title)

    tree = ttk.Treeview(frame, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=150, anchor="w")

    for row in rows:
        tree.insert("", "end", values=row)

    tree.pack(expand=True, fill="both")

    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    return frame

def get_simple_table_data(cursor, table):
    rows = fetch_all(cursor, table)
    if not rows:
        return [], []
    columns = get_column_names(cursor, table)
    return columns, rows

def get_bewerbung_data(cursor):
    cursor.execute("""
        SELECT b.bwg_id, bw.bw_vorname || ' ' || bw.bw_nachname AS Bewerber,
               f.f_stellenbezeichnung || ' bei ' || f.f_name AS Firma
        FROM tbl_bewerbung b
        JOIN tbl_bewerber bw ON b.bwg_bw_id = bw.bw_id
        JOIN tbl_firma f ON b.bwg_f_id = f.f_id
        ORDER BY b.bwg_id
    """)
    rows = cursor.fetchall()
    columns = ["ID", "Bewerber", "Firma"]
    return columns, rows

def get_bwg_ag_data(cursor):
    cursor.execute("""
        SELECT bwg.bwg_ag_id,
               bw.bw_vorname || ' ' || bw.bw_nachname AS Bewerber,
               f.f_stellenbezeichnung || ' bei ' || f.f_name AS Firma,
               ag.ag_name, ag.ag_datum_von, ag.ag_datum_bis
        FROM tbl_bwg_ag bwg
        JOIN tbl_bewerbung b ON bwg.bwg_ag_bwg_id = b.bwg_id
        JOIN tbl_bewerber bw ON b.bwg_bw_id = bw.bw_id
        JOIN tbl_firma f ON b.bwg_f_id = f.f_id
        JOIN tbl_arbeitgeber ag ON bwg.bwg_ag_ag_id = ag.ag_id
        ORDER BY bwg.bwg_ag_id
    """)
    rows = cursor.fetchall()
    columns = ["ID", "Bewerber", "Firma", "Arbeitgeber", "Von", "Bis"]
    return columns, rows

def get_bwg_ag_t_data(cursor):
    cursor.execute("""
        SELECT t.bwg_ag_t_id,
               bw.bw_vorname || ' ' || bw.bw_nachname AS Bewerber,
               f.f_stellenbezeichnung || ' bei ' || f.f_name AS Firma,
               ag.ag_name,
               ta.t_name
        FROM tbl_bwg_ag_t t
        JOIN tbl_bwg_ag bwg_ag ON t.bwg_ag_t_bwg_ag_id = bwg_ag.bwg_ag_id
        JOIN tbl_bewerbung b ON bwg_ag.bwg_ag_bwg_id = b.bwg_id
        JOIN tbl_bewerber bw ON b.bwg_bw_id = bw.bw_id
        JOIN tbl_firma f ON b.bwg_f_id = f.f_id
        JOIN tbl_arbeitgeber ag ON bwg_ag.bwg_ag_ag_id = ag.ag_id
        JOIN tbl_taetigkeit ta ON t.bwg_ag_t_t_id = ta.t_id
        ORDER BY t.bwg_ag_t_id
    """)
    rows = cursor.fetchall()
    columns = ["ID", "Bewerber", "Firma", "Arbeitgeber", "Tätigkeit"]
    return columns, rows

def get_bwg_ab_data(cursor):
    cursor.execute("""
        SELECT bwg_ab.bwg_ab_id,
               bw.bw_vorname || ' ' || bw.bw_nachname AS Bewerber,
               f.f_stellenbezeichnung || ' bei ' || f.f_name AS Firma,
               ab.ab_name_staette,
               ab.ab_name_ausbildung
        FROM tbl_bwg_ab bwg_ab
        JOIN tbl_bewerbung b ON bwg_ab.bwg_ab_bwg_id = b.bwg_id
        JOIN tbl_bewerber bw ON b.bwg_bw_id = bw.bw_id
        JOIN tbl_firma f ON b.bwg_f_id = f.f_id
        JOIN tbl_ausbildung ab ON bwg_ab.bwg_ab_ab_id = ab.ab_id
        ORDER BY bwg_ab.bwg_ab_id
    """)
    rows = cursor.fetchall()
    columns = ["ID", "Bewerber", "Firma", "Ausbildungsstätte", "Ausbildung"]
    return columns, rows

def get_bwg_ab_swp_data(cursor):
    cursor.execute("""
        SELECT s.bwg_ab_swp_id,
               bw.bw_vorname || ' ' || bw.bw_nachname AS Bewerber,
               f.f_stellenbezeichnung || ' bei ' || f.f_name AS Firma,
               ab.ab_name_ausbildung,
               swp.ab_swp_name
        FROM tbl_bwg_ab_swp s
        JOIN tbl_bwg_ab abw ON s.bwg_ab_swp_bwg_ab_id = abw.bwg_ab_id
        JOIN tbl_bewerbung b ON abw.bwg_ab_bwg_id = b.bwg_id
        JOIN tbl_bewerber bw ON b.bwg_bw_id = bw.bw_id
        JOIN tbl_firma f ON b.bwg_f_id = f.f_id
        JOIN tbl_ausbildung ab ON abw.bwg_ab_ab_id = ab.ab_id
        JOIN tbl_ab_schwerpunkt swp ON s.bwg_ab_swp_ab_swp_id = swp.ab_swp_id
        ORDER BY s.bwg_ab_swp_id
    """)
    rows = cursor.fetchall()
    columns = ["ID", "Bewerber", "Firma", "Ausbildung", "Schwerpunkt"]
    return columns, rows

def get_bwg_k_data(cursor):
    cursor.execute("""
        SELECT bwg_k.bwg_k_id,
               bw.bw_vorname || ' ' || bw.bw_nachname AS Bewerber,
               f.f_stellenbezeichnung || ' bei ' || f.f_name AS Firma,
               k.k_name,
               k.k_stufe
        FROM tbl_bwg_k bwg_k
        JOIN tbl_bewerbung b ON bwg_k.bwg_k_bwg_id = b.bwg_id
        JOIN tbl_bewerber bw ON b.bwg_bw_id = bw.bw_id
        JOIN tbl_firma f ON b.bwg_f_id = f.f_id
        JOIN tbl_kenntnisse k ON bwg_k.bwg_k_k_id = k.k_id
        ORDER BY bwg_k.bwg_k_id
    """)
    rows = cursor.fetchall()
    columns = ["ID", "Bewerber", "Firma", "Kenntnis", "Stufe"]
    return columns, rows

def get_bwg_i_data(cursor):
    cursor.execute("""
        SELECT bwg_i.bwg_i_id,
               bw.bw_vorname || ' ' || bw.bw_nachname AS Bewerber,
               f.f_stellenbezeichnung || ' bei ' || f.f_name AS Firma,
               i.i_name
        FROM tbl_bwg_i bwg_i
        JOIN tbl_bewerbung b ON bwg_i.bwg_i_bwg_id = b.bwg_id
        JOIN tbl_bewerber bw ON b.bwg_bw_id = bw.bw_id
        JOIN tbl_firma f ON b.bwg_f_id = f.f_id
        JOIN tbl_interessen i ON bwg_i.bwg_i_i_id = i.i_id
        ORDER BY bwg_i.bwg_i_id
    """)
    rows = cursor.fetchall()
    columns = ["ID", "Bewerber", "Firma", "Interesse"]
    return columns, rows

def main():
    db_path = "/home/birgit/PycharmProjects/LebenslaufTest/src/lb_datenbank/lebenslauf.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    root = tk.Tk()
    root.title("Tabellenansicht - Lebenslauf Datenbank")
    root.geometry("1700x600")

    left_frame = ttk.Frame(root, width=200)
    left_frame.pack(side="left", fill="y")

    right_frame = ttk.Frame(root)
    right_frame.pack(side="right", expand=True, fill="both")

    listbox = tk.Listbox(left_frame)
    listbox.pack(expand=True, fill="both", padx=5, pady=5)

    notebook = ttk.Notebook(right_frame)
    notebook.pack(expand=True, fill="both")

    # Tabellen mit ihren Datenfunktionen (cursor wird als Argument übergeben)
    tables = []

    simple_tables = [
        "tbl_bewerber", "tbl_firma", "tbl_arbeitgeber", "tbl_taetigkeit",
        "tbl_ausbildung", "tbl_ab_schwerpunkt", "tbl_kenntnisse", "tbl_interessen"
    ]

    for t in simple_tables:
        tables.append((t, lambda cur=cursor, tab=t: get_simple_table_data(cur, tab)))

    tables += [
        ("tbl_bewerbung", lambda cur=cursor: get_bewerbung_data(cur)),
        ("tbl_bwg_ag", lambda cur=cursor: get_bwg_ag_data(cur)),
        ("tbl_bwg_ag_t", lambda cur=cursor: get_bwg_ag_t_data(cur)),
        ("tbl_bwg_ab", lambda cur=cursor: get_bwg_ab_data(cur)),
        ("tbl_bwg_ab_swp", lambda cur=cursor: get_bwg_ab_swp_data(cur)),
        ("tbl_bwg_k", lambda cur=cursor: get_bwg_k_data(cur)),
        ("tbl_bwg_i", lambda cur=cursor: get_bwg_i_data(cur)),
    ]

    # Liste füllen
    for name, _ in tables:
        listbox.insert("end", name)

    def on_listbox_select(event):
        selection = listbox.curselection()
        if not selection:
            return
        index = selection[0]
        table_name, data_func = tables[index]

        # Daten holen und neuen Tab mit Tabelle erstellen
        columns, rows = data_func()
        if not columns:
            return

        create_table_tab(notebook, table_name, columns, rows)

    listbox.bind("<<ListboxSelect>>", on_listbox_select)

    # Start-Anzeige: gleich ersten Eintrag laden
    if tables:
        listbox.selection_set(0)
        listbox.event_generate("<<ListboxSelect>>")

    root.mainloop()

    conn.close()

if __name__ == "__main__":
    main()
