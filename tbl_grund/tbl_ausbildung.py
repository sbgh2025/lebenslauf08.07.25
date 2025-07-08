# tbl_ausbildung.py
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



# Tabelle erstellen (falls noch nicht vorhanden)
cursor.execute("""
CREATE TABLE IF NOT EXISTS tbl_ausbildung (
    ab_id INTEGER PRIMARY KEY AUTOINCREMENT,
    ab_datum_von DATE NOT NULL,
    ab_datum_bis DATE,
    ab_name_staette TEXT NOT NULL,
    ab_name_ausbildung TEXT NOT NULL,
    ab_abschluss TEXT,
    ab_zeit TEXT
);
""")
conn.commit()

# GUI-Fenster
root = tk.Tk()
root.title("Ausbildung verwalten")
root.geometry("1400x400")

# Eingabefelder
labels = [
    "Datum von", "Datum bis", "Ausbildungsstätte", "Ausbildung",
    "Abschluss", "Zeitraum"
]
entries = {}

# Eingabefelder und Labels linksbündig anordnen
for i, label in enumerate(labels):
    tk.Label(root, text=label).grid(row=i, column=0, sticky="e", padx=5, pady=2)
    entry = tk.Entry(root, width=40)
    entry.grid(row=i, column=1, padx=5, pady=2, sticky="w")
    entries[label] = entry

# Frame für Treeview + Scrollbar
tree_frame = tk.Frame(root)
tree_frame.grid(row=0, column=3, rowspan=20, padx=10, pady=10, sticky="nsew")

# Scrollbar
tree_scroll = tk.Scrollbar(tree_frame, orient="vertical")
tree_scroll.grid(row=0, column=1, sticky="ns")

# Treeview (mit kleinerer Höhe)
tree = ttk.Treeview(
    tree_frame,
    columns=labels,
    show="headings",
    yscrollcommand=tree_scroll.set,
    selectmode="extended",  # NEU: erlaubt Mehrfachauswahl
    height=6
)

tree.grid(row=0, column=0, sticky="nsew")
tree_scroll.config(command=tree.yview)

# Spaltenüberschriften
for label in labels:
    tree.heading(label, text=label)
    tree.column(label, width=140)

# Funktionen

# Diese Funktion lädt alle Daten aus der Datenbank in das Treeview
def reload_data():
    tree.delete(*tree.get_children())
    cursor.execute("SELECT * FROM tbl_ausbildung ORDER BY ab_datum_bis DESC")
    for row in cursor.fetchall():
        tree.insert("", "end", iid=row[0], values=row[1:])

# Diese Funktion überprüft, ob ein Datensatz mit den gleichen Werten bereits existiert
def is_duplicate_record(data):
    cursor.execute("""
        SELECT COUNT(*) FROM tbl_ausbildung 
        WHERE TRIM(ab_datum_von) = ? 
        AND TRIM(ab_name_staette) = ? 
        AND TRIM(ab_name_ausbildung) = ?
    """, (data[0], data[2], data[3]))
    result = cursor.fetchone()
    return result[0] > 0

# Diese Funktion fügt einen neuen Datensatz hinzu
def add_record():
    data = [entries[label].get().strip() for label in labels]

    # Überprüfen, ob die Pflichtfelder ausgefüllt sind
    if not data[0] or not data[2] or not data[3]:
        messagebox.showwarning("Pflichtfelder", "Datum von, Ausbildungsstätte und Ausbildung sind erforderlich.")
        return

    # Duplikatprüfung
    if is_duplicate_record(data):
        messagebox.showwarning("Duplikat", "Dieser Datensatz existiert bereits!")
        return

    # Einfügen des Datensatzes, falls kein Duplikat gefunden wurde
    cursor.execute("""
        INSERT INTO tbl_ausbildung 
        (ab_datum_von, ab_datum_bis, ab_name_staette, ab_name_ausbildung, ab_abschluss, ab_zeit)
        VALUES (?, ?, ?, ?, ?, ?)
    """, data)
    conn.commit()
    reload_data()
    clear_fields()

# Diese Funktion aktualisiert einen bestehenden Datensatz
def update_record():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Keine Auswahl", "Bitte einen Datensatz auswählen.")
        return
    ab_id = selected[0]
    data = [entries[label].get().strip() for label in labels]
    cursor.execute("""
        UPDATE tbl_ausbildung SET
        ab_datum_von = ?, ab_datum_bis = ?, ab_name_staette = ?, 
        ab_name_ausbildung = ?, ab_abschluss = ?, ab_zeit = ?
        WHERE ab_id = ?
    """, data + [ab_id])
    conn.commit()
    reload_data()
    clear_fields()

# Diese Funktion löscht einen oder mehrere Datensätze
def delete_record():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Keine Auswahl", "Bitte mindestens einen Datensatz auswählen.")
        return

    if messagebox.askyesno("Löschen", f"{len(selected)} Datensätze wirklich löschen?"):
        for ab_id in selected:
            cursor.execute("DELETE FROM tbl_ausbildung WHERE ab_id = ?", (ab_id,))
        conn.commit()
        reload_data()
        clear_fields()

# Diese Funktion lädt die Daten aus der Treeview-Auswahl in die Eingabefelder
def on_select(event):
    selected = tree.selection()
    if selected:
        values = tree.item(selected[0])["values"]
        for i, label in enumerate(labels):
            entries[label].delete(0, tk.END)
            entries[label].insert(0, values[i])

# Diese Funktion leert alle Eingabefelder
def clear_fields():
    for entry in entries.values():
        entry.delete(0, tk.END)

# Diese Funktion importiert Daten aus einer CSV-Datei
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
            messagebox.showerror("Fehler", f"CSV-Datei muss diese Spalten enthalten:\n{expected_headers}")
            return

        rows_imported = 0
        for row in reader:
            row = [field.strip() for field in row]
            if len(row) == len(expected_headers):
                if not is_duplicate_record(row):
                    cursor.execute("""
                        INSERT INTO tbl_ausbildung 
                        (ab_datum_von, ab_datum_bis, ab_name_staette, ab_name_ausbildung, ab_abschluss, ab_zeit)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, row)
                    rows_imported += 1

        conn.commit()
        reload_data()
        messagebox.showinfo("Import abgeschlossen", f"{rows_imported} Datensätze importiert.")

# Buttons links unter den Eingabefeldern
tk.Button(root, text="Hinzufügen", command=add_record).grid(row=6, column=0, pady=5, padx=10, sticky="w")
tk.Button(root, text="Aktualisieren", command=update_record).grid(row=7, column=0, pady=5, padx=10, sticky="w")
tk.Button(root, text="Löschen", command=delete_record).grid(row=8, column=0, pady=5, padx=10, sticky="w")
tk.Button(root, text="Felder leeren", command=clear_fields).grid(row=9, column=0, pady=5, padx=10, sticky="w")
tk.Button(root, text="CSV importieren", command=import_from_csv).grid(row=10, column=0, pady=10, padx=10, sticky="w")

# Treeview-Auswahlbindung
tree.bind("<<TreeviewSelect>>", on_select)

# Initiales Laden der Daten
reload_data()
root.mainloop()
