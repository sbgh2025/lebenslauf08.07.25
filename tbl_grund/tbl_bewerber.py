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




# Tkinter Fenster
root = tk.Tk()
root.title("Bewerberverwaltung")
root.geometry("1500x600")

# Eingabefelder
labels = [
    "Vorname", "Nachname", "Geburtsdatum", "Straße", "PLZ",
    "Ort", "E-Mail", "Telefon"
]
entries = {}

for i, label in enumerate(labels):
    tk.Label(root, text=label).grid(row=i, column=0, sticky="e")
    entry = tk.Entry(root, width=30)
    entry.grid(row=i, column=1)
    entries[label] = entry

# Treeview zur Anzeige
tree = ttk.Treeview(root, columns=labels, show="headings")
for label in labels:
    tree.heading(label, text=label)
    tree.column(label, width=100)
tree.grid(row=0, column=3, rowspan=10, padx=10)


def reload_data():
    tree.delete(*tree.get_children())
    cursor.execute("SELECT * FROM tbl_bewerber")
    for row in cursor.fetchall():
        tree.insert("", "end", iid=row[0], values=row[1:])


def clear_fields():
    for entry in entries.values():
        entry.delete(0, tk.END)


def add_record():
    data = [entries[label].get().strip() for label in labels]

    if not data[0] or not data[1]:
        messagebox.showwarning("Pflichtfelder", "Vor- und Nachname sind erforderlich.")
        return

    # Prüfen auf Duplikate (Vorname, Nachname, Geburtsdatum)
    cursor.execute("""
        SELECT COUNT(*) FROM tbl_bewerber
        WHERE bw_vorname = ? AND bw_nachname = ? AND bw_geburtsdatum = ?
    """, (data[0], data[1], data[2]))
    if cursor.fetchone()[0] > 0:
        messagebox.showwarning("Doppelter Eintrag", "Ein Bewerber mit diesen Daten ist bereits vorhanden.")
        return

    cursor.execute("""
        INSERT INTO tbl_bewerber 
        (bw_vorname, bw_nachname, bw_geburtsdatum, bw_strasse, bw_plz, bw_ort, bw_mail, bw_telefon)
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

    bw_id = selected[0]
    data = [entries[label].get().strip() for label in labels]

    cursor.execute("""
        UPDATE tbl_bewerber SET
        bw_vorname = ?, bw_nachname = ?, bw_geburtsdatum = ?, bw_strasse = ?,
        bw_plz = ?, bw_ort = ?, bw_mail = ?, bw_telefon = ?
        WHERE bw_id = ?
    """, data + [bw_id])
    conn.commit()
    reload_data()
    clear_fields()


def delete_record():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Keine Auswahl", "Bitte mindestens einen Datensatz auswählen.")
        return

    if messagebox.askyesno("Löschen", f"{len(selected)} Datensatz/Datasets wirklich löschen?"):
        for bw_id in selected:
            cursor.execute("DELETE FROM tbl_bewerber WHERE bw_id = ?", (bw_id,))
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

        expected_headers = [
            "Vorname", "Nachname", "Geburtsdatum", "Straße",
            "PLZ", "Ort", "E-Mail", "Telefon"
        ]

        if headers != expected_headers:
            messagebox.showerror("Falsches Format", "Die CSV-Datei hat nicht das erwartete Format.")
            return

        rows_imported = 0
        for row in reader:
            row = [field.strip() for field in row]
            if len(row) == len(expected_headers):
                # Doppelte vermeiden
                cursor.execute("""
                    SELECT COUNT(*) FROM tbl_bewerber
                    WHERE bw_vorname = ? AND bw_nachname = ? AND bw_geburtsdatum = ?
                """, (row[0], row[1], row[2]))
                if cursor.fetchone()[0] == 0:
                    cursor.execute("""
                        INSERT INTO tbl_bewerber 
                        (bw_vorname, bw_nachname, bw_geburtsdatum, bw_strasse, bw_plz, bw_ort, bw_mail, bw_telefon)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, row)
                    rows_imported += 1

        conn.commit()
        reload_data()
        messagebox.showinfo("Import abgeschlossen", f"{rows_imported} Datensätze erfolgreich importiert.")


# Treeview Auswahl-Event
tree.bind("<<TreeviewSelect>>", on_select)

# Button-Frame für bessere Organisation
button_frame = tk.Frame(root)
button_frame.grid(row=12, column=0, columnspan=2, pady=20)

# Buttons
tk.Button(button_frame, text="Hinzufügen", width=20, command=add_record).grid(row=0, column=0, padx=5)
tk.Button(button_frame, text="Aktualisieren", width=20, command=update_record).grid(row=0, column=1, padx=5)
tk.Button(button_frame, text="Löschen", width=20, command=delete_record).grid(row=0, column=2, padx=5)
tk.Button(button_frame, text="Felder leeren", width=20, command=clear_fields).grid(row=0, column=3, padx=5)
tk.Button(button_frame, text="CSV importieren", width=20, command=import_from_csv).grid(row=0, column=4, padx=5)

# Startdaten laden
reload_data()
root.mainloop()
