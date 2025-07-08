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
root.title("Firmenverwaltung")
root.geometry("1700x700")  # etwas höher wegen Buttons unten

# Eingabefelder
labels = [
    "Datum", "Stellenbezeichnung", "Firmenname", "Straße", "PLZ",
    "Ort", "E-Mail", "Telefon"
]
entries = {}

for i, label in enumerate(labels):
    tk.Label(root, text=label).grid(row=i, column=0, sticky="e", padx=5, pady=2)
    entry = tk.Entry(root, width=30)
    entry.grid(row=i, column=1, pady=2)
    entries[label] = entry

# Frame für Treeview + Scrollbar
tree_frame = tk.Frame(root)
tree_frame.grid(row=0, column=3, rowspan=15, padx=10, pady=10, sticky="n")

# Scrollbar
tree_scroll = tk.Scrollbar(tree_frame, orient="vertical")
tree_scroll.grid(row=0, column=1, sticky="ns")

# Treeview mit Mehrfachauswahl enabled (selectmode="extended")
tree = ttk.Treeview(
    tree_frame,
    columns=labels,
    show="headings",
    yscrollcommand=tree_scroll.set,
    height=15,
    selectmode="extended"
)
tree.grid(row=0, column=0, sticky="n")
tree_scroll.config(command=tree.yview)

# Spaltenüberschriften
for label in labels:
    tree.heading(label, text=label)
    tree.column(label, width=140)

# Daten neu laden (mit Sortierung)
def reload_data(order_by=None):
    tree.delete(*tree.get_children())
    query = "SELECT * FROM tbl_firma"
    if order_by:
        query += f" ORDER BY {order_by}"
    cursor.execute(query)
    for row in cursor.fetchall():
        tree.insert("", "end", iid=row[0], values=row[1:])

# Duplikat-Prüfung: Datum + Stellenbezeichnung + Firmenname
def is_duplicate(datum, stellenbezeichnung, name):
    cursor.execute("""
        SELECT COUNT(*) FROM tbl_firma
        WHERE f_datum = ? AND f_stellenbezeichnung = ? AND f_name = ?
    """, (datum, stellenbezeichnung, name))
    return cursor.fetchone()[0] > 0

# Datensatz hinzufügen mit Duplikat-Prüfung
def add_record():
    data = [entries[label].get().strip() for label in labels]
    if not data[0] or not data[1] or not data[2]:
        messagebox.showwarning("Pflichtfelder", "Datum, Stellenbezeichnung und Firmenname sind erforderlich.")
        return

    if is_duplicate(data[0], data[1], data[2]):
        messagebox.showwarning("Doppelter Eintrag", "Dieser Eintrag existiert bereits.")
        return

    cursor.execute("""
        INSERT INTO tbl_firma 
        (f_datum, f_stellenbezeichnung, f_name, f_strasse, f_plz, f_ort, f_mail, f_telefon)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, data)
    conn.commit()
    reload_data()
    clear_fields()

# Datensatz aktualisieren
def update_record():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Keine Auswahl", "Bitte einen Datensatz auswählen.")
        return
    f_id = selected[0]
    data = [entries[label].get().strip() for label in labels]

    # Optional: Duplikat beim Update vermeiden (außer es ist derselbe Datensatz)
    cursor.execute("""
        SELECT COUNT(*) FROM tbl_firma
        WHERE f_datum = ? AND f_stellenbezeichnung = ? AND f_name = ? AND f_id != ?
    """, (data[0], data[1], data[2], f_id))
    if cursor.fetchone()[0] > 0:
        messagebox.showwarning("Doppelter Eintrag", "Dieser Eintrag existiert bereits.")
        return

    cursor.execute("""
        UPDATE tbl_firma SET
        f_datum = ?, f_stellenbezeichnung = ?, f_name = ?, f_strasse = ?,
        f_plz = ?, f_ort = ?, f_mail = ?, f_telefon = ?
        WHERE f_id = ?
    """, data + [f_id])
    conn.commit()
    reload_data()
    clear_fields()

# Mehrere Datensätze löschen
def delete_record():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Keine Auswahl", "Bitte mindestens einen Datensatz auswählen.")
        return

    if messagebox.askyesno("Löschen", f"{len(selected)} Datensatz/Daten wirklich löschen?"):
        for f_id in selected:
            cursor.execute("DELETE FROM tbl_firma WHERE f_id = ?", (f_id,))
        conn.commit()
        reload_data()
        clear_fields()

# Auswahl anzeigen
def on_select(event):
    selected = tree.selection()
    if selected:
        values = tree.item(selected[0])["values"]
        for i, label in enumerate(labels):
            entries[label].delete(0, tk.END)
            entries[label].insert(0, values[i])

# Felder leeren
def clear_fields():
    for entry in entries.values():
        entry.delete(0, tk.END)

# CSV-Import mit Duplikat-Prüfung
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
        for row in reader:
            row = [field.strip() for field in row]
            if len(row) == len(expected_headers):
                if not is_duplicate(row[0], row[1], row[2]):
                    cursor.execute("""
                        INSERT INTO tbl_firma 
                        (f_datum, f_stellenbezeichnung, f_name, f_strasse, f_plz, f_ort, f_mail, f_telefon)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, row)
                    rows_imported += 1

        conn.commit()
        if rows_imported > 0:
            messagebox.showinfo("Import erfolgreich", f"{rows_imported} Datensätze importiert.")
        else:
            messagebox.showwarning("Keine Daten importiert", "Keine gültigen Zeilen gefunden oder alle waren Duplikate.")
        reload_data()

# Sortierfunktionen
def sort_by_datum():
    reload_data("f_datum")

def sort_by_stellenbezeichnung():
    reload_data("f_stellenbezeichnung")

def sort_by_firmenname():
    reload_data("f_name")

# Buttons über gesamte Breite in zwei Reihen (je 4 Buttons pro Reihe)
button_texts_cmds = [
    ("Hinzufügen", add_record),
    ("Aktualisieren", update_record),
    ("Löschen", delete_record),
    ("Felder leeren", clear_fields),
    ("CSV importieren", import_from_csv),
    ("Sortieren nach Datum", sort_by_datum),
    ("Sortieren nach Stellenbezeichnung", sort_by_stellenbezeichnung),
    ("Sortieren nach Firmenname", sort_by_firmenname),
]

button_frame = tk.Frame(root)
button_frame.grid(row=15, column=0, columnspan=4, pady=20, sticky="ew")

# Spalten konfigurieren für gleichmäßige Verteilung
for col in range(4):
    button_frame.grid_columnconfigure(col, weight=1)

for i, (text, cmd) in enumerate(button_texts_cmds):
    row = i // 4
    col = i % 4
    btn = tk.Button(button_frame, text=text, command=cmd)
    btn.grid(row=row, column=col, padx=10, pady=5, sticky="ew")

# Treeview-Auswahlbindung
tree.bind("<<TreeviewSelect>>", on_select)

# Initialdaten laden
reload_data()

# Hauptloop starten
root.mainloop()
