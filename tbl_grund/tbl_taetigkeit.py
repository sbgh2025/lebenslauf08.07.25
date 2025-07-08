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


# Tkinter-Fenster
root = tk.Tk()
root.title("Tätigkeiten verwalten")
root.geometry("800x500")

# Label + Eingabefeld
tk.Label(root, text="Tätigkeit:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
entry_name = tk.Entry(root, width=40)
entry_name.grid(row=0, column=1, padx=10, pady=5)

# Frame für Treeview + Scrollbar
tree_frame = tk.Frame(root)
tree_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky="n")

tree_scroll = tk.Scrollbar(tree_frame, orient="vertical")
tree_scroll.grid(row=0, column=1, sticky="ns")

tree = ttk.Treeview(
    tree_frame,
    columns=("Tätigkeit",),
    show="headings",
    yscrollcommand=tree_scroll.set,
    height=12
)
tree.heading("Tätigkeit", text="Tätigkeit")
tree.column("Tätigkeit", width=600)
tree.grid(row=0, column=0, sticky="nsew")

tree_scroll.config(command=tree.yview)

# Funktionen
def reload_data():
    tree.delete(*tree.get_children())
    cursor.execute("SELECT * FROM tbl_taetigkeit ORDER BY LOWER(t_name) ASC")
    for row in cursor.fetchall():
        tree.insert("", "end", iid=row[0], values=(row[1],))

def add_record():
    name = entry_name.get().strip()
    if not name:
        messagebox.showwarning("Eingabefehler", "Bitte eine Tätigkeit eingeben.")
        return

    # Duplikate prüfen (case-insensitive)
    cursor.execute("SELECT COUNT(*) FROM tbl_taetigkeit WHERE LOWER(t_name) = LOWER(?)", (name,))
    if cursor.fetchone()[0] > 0:
        messagebox.showinfo("Hinweis", "Diese Tätigkeit existiert bereits.")
        return

    cursor.execute("INSERT INTO tbl_taetigkeit (t_name) VALUES (?)", (name,))
    conn.commit()
    reload_data()
    entry_name.delete(0, tk.END)

def update_record():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Auswahl fehlt", "Bitte eine Tätigkeit auswählen.")
        return

    t_id = selected[0]
    name = entry_name.get().strip()
    if not name:
        messagebox.showwarning("Eingabefehler", "Bitte eine Tätigkeit eingeben.")
        return

    # Duplikatprüfung bei anderen IDs
    cursor.execute("SELECT COUNT(*) FROM tbl_taetigkeit WHERE LOWER(t_name) = LOWER(?) AND t_id != ?", (name, t_id))
    if cursor.fetchone()[0] > 0:
        messagebox.showinfo("Hinweis", "Diese Tätigkeit existiert bereits.")
        return

    cursor.execute("UPDATE tbl_taetigkeit SET t_name = ? WHERE t_id = ?", (name, t_id))
    conn.commit()
    reload_data()
    entry_name.delete(0, tk.END)

def delete_record():
    selected_items = tree.selection()
    if not selected_items:
        messagebox.showwarning("Auswahl fehlt", "Bitte mindestens eine Tätigkeit auswählen.")
        return

    if not messagebox.askyesno("Löschen", f"{len(selected_items)} Tätigkeit(en) wirklich löschen?"):
        return

    for item in selected_items:
        cursor.execute("DELETE FROM tbl_taetigkeit WHERE t_id = ?", (item,))
    conn.commit()
    reload_data()
    entry_name.delete(0, tk.END)

def on_select(event):
    selected = tree.selection()
    if selected:
        name = tree.item(selected[0])["values"][0]
        entry_name.delete(0, tk.END)
        entry_name.insert(0, name)

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
        if headers != ["Tätigkeit"]:
            messagebox.showerror("Fehler", "CSV-Datei muss genau eine Spalte namens 'Tätigkeit' enthalten.")
            return

        rows_imported = 0
        for row in reader:
            if row:
                name = row[0].strip()
                if name:
                    cursor.execute("SELECT COUNT(*) FROM tbl_taetigkeit WHERE LOWER(t_name) = LOWER(?)", (name,))
                    if cursor.fetchone()[0] == 0:
                        cursor.execute("INSERT INTO tbl_taetigkeit (t_name) VALUES (?)", (name,))
                        rows_imported += 1

        conn.commit()
        reload_data()
        messagebox.showinfo("Import abgeschlossen", f"{rows_imported} neue Tätigkeit(en) importiert.")

# Buttons
tk.Button(root, text="Hinzufügen", command=add_record).grid(row=2, column=0, pady=5, padx=10, sticky="w")
tk.Button(root, text="Aktualisieren", command=update_record).grid(row=3, column=0, pady=5, padx=10, sticky="w")
tk.Button(root, text="Löschen", command=delete_record).grid(row=4, column=0, pady=5, padx=10, sticky="w")
tk.Button(root, text="CSV importieren", command=import_from_csv).grid(row=5, column=0, pady=10, padx=10, sticky="w")

# Auswahlbindung
tree.bind("<<TreeviewSelect>>", on_select)

# Initiales Laden
reload_data()
root.mainloop()
