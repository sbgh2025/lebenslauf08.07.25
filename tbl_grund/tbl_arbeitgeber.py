# tbl_arbeitgeber.py
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import csv
import sys
import os

# Datenbankmodul importieren
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../lb_datenbank")))
from db_pfad import get_connection

# Verbindung zur Datenbank
conn = get_connection()
cursor = conn.cursor()

# Tkinter GUI
root = tk.Tk()
root.title("Arbeitgeberverwaltung")
root.geometry("1600x450")

# Eingabefelder
labels = [
    "Datum von", "Datum bis", "Firmenname", "Zeitraum", "Funktion",
    "Ort", "Leihfirma", "Bemerkung"
]
entries = {}

for i, label in enumerate(labels):
    tk.Label(root, text=label).grid(row=i, column=0, sticky="e", padx=5, pady=2)
    entry = tk.Entry(root, width=30)
    entry.grid(row=i, column=1, pady=2, sticky="w")
    entries[label] = entry

# TreeView mit Scrollbar
tree_frame = tk.Frame(root)
tree_frame.grid(row=0, column=3, rowspan=20, padx=10, pady=10, sticky="nsew")

tree_scroll = tk.Scrollbar(tree_frame, orient="vertical")
tree_scroll.grid(row=0, column=1, sticky="ns")

tree = ttk.Treeview(
    tree_frame,
    columns=labels,
    show="headings",
    yscrollcommand=tree_scroll.set,
    selectmode="extended",
    height=6
)
tree.grid(row=0, column=0, sticky="nsew")
tree_scroll.config(command=tree.yview)

for label in labels:
    tree.heading(label, text=label)
    tree.column(label, width=140)

tree_frame.grid_columnconfigure(0, weight=1)

# Funktionen
def reload_data():
    tree.delete(*tree.get_children())
    cursor.execute("SELECT * FROM tbl_arbeitgeber")
    for row in cursor.fetchall():
        tree.insert("", "end", iid=row[0], values=row[1:])

def is_duplicate_record(data):
    cursor.execute("""
        SELECT COUNT(*) FROM tbl_arbeitgeber
        WHERE ag_datum_von = ? AND ag_name = ? AND ag_funktion = ?
    """, (data[0], data[2], data[4]))
    return cursor.fetchone()[0] > 0

def add_record():
    data = [entries[label].get().strip() for label in labels]
    if not data[0] or not data[2]:
        messagebox.showwarning("Pflichtfelder", "Datum von und Firmenname sind erforderlich.")
        return
    if is_duplicate_record(data):
        messagebox.showinfo("Bereits vorhanden", "Ein identischer Datensatz ist bereits vorhanden.")
        return
    cursor.execute("""
        INSERT INTO tbl_arbeitgeber 
        (ag_datum_von, ag_datum_bis, ag_name, ag_zeit, ag_funktion, ag_ort, ag_leihfirma, ag_bemerkung)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, data)
    conn.commit()
    reload_data()
    clear_fields()

def update_record():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Keine Auswahl", "Bitte einen Datensatz auswählen.")
        return
    ag_id = selected[0]
    data = [entries[label].get().strip() for label in labels]
    cursor.execute("""
        UPDATE tbl_arbeitgeber SET
        ag_datum_von = ?, ag_datum_bis = ?, ag_name = ?, ag_zeit = ?,
        ag_funktion = ?, ag_ort = ?, ag_leihfirma = ?, ag_bemerkung = ?
        WHERE ag_id = ?
    """, data + [ag_id])
    conn.commit()
    reload_data()
    clear_fields()

def delete_record():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Keine Auswahl", "Bitte mindestens einen Datensatz auswählen.")
        return
    if messagebox.askyesno("Löschen", f"{len(selected)} Datensatz/Datasets wirklich löschen?"):
        for ag_id in selected:
            cursor.execute("DELETE FROM tbl_arbeitgeber WHERE ag_id = ?", (ag_id,))
        conn.commit()
        reload_data()
        clear_fields()

def on_select(event):
    selected = tree.selection()
    if selected:
        values = tree.item(selected[0])["values"]
        for i, label in enumerate(labels):
            entries[label].delete(0, tk.END)
            entries[label].insert(0, values[i])

def clear_fields():
    for entry in entries.values():
        entry.delete(0, tk.END)

def import_from_csv():
    filepath = filedialog.askopenfilename(
        title="CSV-Datei auswählen",
        filetypes=[("CSV-Dateien", "*.csv")]
    )
    if not filepath:
        return

    with open(filepath, mode="r", newline="", encoding="utf-8") as file:
        reader = csv.reader(file)
        headers = next(reader)
        expected_headers = labels

        if headers != expected_headers:
            messagebox.showerror("Falsche CSV-Datei", f"Die CSV-Datei hat nicht das erwartete Format:\n{expected_headers}")
            return

        rows_imported = 0
        rows_skipped = 0

        for row in reader:
            row = [field.strip() for field in row]
            if len(row) == len(expected_headers):
                if not is_duplicate_record(row):
                    cursor.execute("""
                        INSERT INTO tbl_arbeitgeber 
                        (ag_datum_von, ag_datum_bis, ag_name, ag_zeit, ag_funktion, ag_ort, ag_leihfirma, ag_bemerkung)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, row)
                    rows_imported += 1
                else:
                    rows_skipped += 1

        conn.commit()
        messagebox.showinfo(
            "CSV Import",
            f"{rows_imported} Datensätze importiert.\n{rows_skipped} Duplikate übersprungen."
        )
        reload_data()

# Buttons
tk.Button(root, text="Hinzufügen", command=add_record).grid(row=8, column=0, pady=5, padx=10, sticky="w")
tk.Button(root, text="Aktualisieren", command=update_record).grid(row=9, column=0, pady=5, padx=10, sticky="w")
tk.Button(root, text="Löschen", command=delete_record).grid(row=10, column=0, pady=5, padx=10, sticky="w")
tk.Button(root, text="Felder leeren", command=clear_fields).grid(row=11, column=0, pady=5, padx=10, sticky="w")
tk.Button(root, text="CSV importieren", command=import_from_csv).grid(row=12, column=0, pady=5, padx=10, sticky="w")

tree.bind("<<TreeviewSelect>>", on_select)

# Initialdaten laden
reload_data()
root.mainloop()
