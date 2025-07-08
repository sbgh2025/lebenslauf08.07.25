# tbl_ausbildungsschwerpunkte.py
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

# Tkinter-Fenster
root = tk.Tk()
root.title("Ausbildungsschwerpunkte verwalten")
root.geometry("600x400")

# Grid-Konfiguration für bessere Layoutanpassung
root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(1, weight=1)

# Label + Eingabefeld
tk.Label(root, text="Schwerpunkt:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
entry_name = tk.Entry(root, width=40)
entry_name.grid(row=0, column=1, padx=10, pady=5, sticky="w")

# Frame für Treeview + Scrollbar
tree_frame = tk.Frame(root)
tree_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

# Scrollbar
tree_scroll = tk.Scrollbar(tree_frame, orient="vertical")
tree_scroll.grid(row=0, column=1, sticky="ns")

# Treeview mit Scrollbar
labels = ("Schwerpunkt",)
tree = ttk.Treeview(
    tree_frame,
    columns=labels,
    show="headings",
    yscrollcommand=tree_scroll.set,
    selectmode="extended",  # Mehrfachauswahl erlaubt
    height=6
)
tree.grid(row=0, column=0, sticky="nsew")
tree_scroll.config(command=tree.yview)

# Treeview-Spalten
tree.heading("Schwerpunkt", text="Schwerpunkt")
tree.column("Schwerpunkt", width=500)

# Daten neu laden
def reload_data():
    tree.delete(*tree.get_children())
    cursor.execute("SELECT * FROM tbl_ab_schwerpunkt ORDER BY ab_swp_name COLLATE NOCASE")
    for row in cursor.fetchall():
        tree.insert("", "end", iid=row[0], values=(row[1],))

# Eingabefeld leeren
def clear_fields():
    entry_name.delete(0, tk.END)

# Datensatz hinzufügen
def add_record():
    name = entry_name.get().strip()
    if not name:
        messagebox.showwarning("Eingabefehler", "Bitte einen Schwerpunkt eingeben.")
        return

    cursor.execute("SELECT COUNT(*) FROM tbl_ab_schwerpunkt WHERE ab_swp_name = ?", (name,))
    if cursor.fetchone()[0] > 0:
        messagebox.showinfo("Hinweis", "Dieser Schwerpunkt existiert bereits.")
        return

    cursor.execute("INSERT INTO tbl_ab_schwerpunkt (ab_swp_name) VALUES (?)", (name,))
    conn.commit()
    reload_data()
    clear_fields()

# Datensatz aktualisieren
def update_record():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Auswahl fehlt", "Bitte einen Eintrag auswählen.")
        return

    ab_swp_id = selected[0]
    name = entry_name.get().strip()
    if not name:
        messagebox.showwarning("Eingabefehler", "Bitte einen Schwerpunkt eingeben.")
        return

    cursor.execute("UPDATE tbl_ab_schwerpunkt SET ab_swp_name = ? WHERE ab_swp_id = ?", (name, ab_swp_id))
    conn.commit()
    reload_data()
    clear_fields()

# Datensatz löschen
def delete_record():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Keine Auswahl", "Bitte mindestens einen Datensatz auswählen.")
        return

    if messagebox.askyesno("Löschen", f"{len(selected)} Datensätze wirklich löschen?"):
        for ab_swp_id in selected:
            cursor.execute("DELETE FROM tbl_ab_schwerpunkt WHERE ab_swp_id = ?", (ab_swp_id,))
        conn.commit()
        reload_data()
        clear_fields()

# Auswahl anzeigen
def on_select(event):
    selected = tree.selection()
    if selected:
        name = tree.item(selected[0])["values"][0]
        entry_name.delete(0, tk.END)
        entry_name.insert(0, name)

# CSV-Import
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
        if headers != ["Schwerpunkt"]:
            messagebox.showerror("Fehler", "CSV-Datei muss genau eine Spalte namens 'Schwerpunkt' enthalten.")
            return

        rows_imported = 0
        for row in reader:
            if row:
                name = row[0].strip()
                if name:
                    cursor.execute("SELECT COUNT(*) FROM tbl_ab_schwerpunkt WHERE ab_swp_name = ?", (name,))
                    if cursor.fetchone()[0] == 0:
                        cursor.execute("INSERT INTO tbl_ab_schwerpunkt (ab_swp_name) VALUES (?)", (name,))
                        rows_imported += 1

    conn.commit()
    reload_data()
    messagebox.showinfo("Import abgeschlossen", f"{rows_imported} Schwerpunkte importiert.")

# Buttons am linken Rand
tk.Button(root, text="Hinzufügen", command=add_record).grid(row=2, column=0, pady=5, padx=10, sticky="w")
tk.Button(root, text="Aktualisieren", command=update_record).grid(row=3, column=0, pady=5, padx=10, sticky="w")
tk.Button(root, text="Löschen", command=delete_record).grid(row=4, column=0, pady=5, padx=10, sticky="w")
tk.Button(root, text="CSV importieren", command=import_from_csv).grid(row=5, column=0, pady=10, padx=10, sticky="w")

# Auswahlbindung
tree.bind("<<TreeviewSelect>>", on_select)

# Daten laden
reload_data()
root.mainloop()
