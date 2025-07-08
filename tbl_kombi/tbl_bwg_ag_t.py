import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import os
import sys

# Pfad zur Datenbankfunktion einbinden
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../lb_datenbank")))

print(os.path.abspath(os.path.join(os.path.dirname(__file__), "../lb_datenbank")))

# Verbindung zur Datenbank
from db_pfad import get_connection, get_cursor
conn = get_connection()
cursor = get_cursor(conn)


# Hauptfenster
root = tk.Tk()
root.title("Bewerbung/Arbeitgeber <-> Tätigkeit")
root.geometry("1200x600")

# Label
tk.Label(root, text="Bewerbung/Arbeitgeber-Zuordnung:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
tk.Label(root, text="Tätigkeiten (bis zu 3 auswählen):").grid(row=1, column=0, padx=10, pady=5, sticky="ne")

# Combobox für Zuordnung
combo_bwg_ag = ttk.Combobox(root, state="readonly", width=70)
combo_bwg_ag.grid(row=0, column=1, padx=10, pady=5)

# Frame für Listbox
listbox_frame = tk.Frame(root)
listbox_frame.grid(row=1, column=1, padx=10, pady=5, sticky="nsew")

# Scrollbar + Listbox für Tätigkeiten
listbox_scroll = tk.Scrollbar(listbox_frame, orient=tk.VERTICAL)
listbox_scroll.pack(side=tk.RIGHT, fill=tk.Y)

listbox_taetigkeiten = tk.Listbox(listbox_frame, selectmode=tk.MULTIPLE, width=70, height=8,
                                  yscrollcommand=listbox_scroll.set)
listbox_taetigkeiten.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

listbox_scroll.config(command=listbox_taetigkeiten.yview)

bwg_ag_map = {}
taetigkeit_map = {}


# Daten neu laden
def refresh_data():
    global bwg_ag_map, taetigkeit_map

    # Bewerbung/Arbeitgeber-Zuordnungen
    cursor.execute("""
        SELECT ba.bwg_ag_id,
               be.bw_vorname || ' ' || be.bw_nachname || ' -> ' || f.f_name || ' -> ' || ag.ag_name || ' (' || ag.ag_datum_von || ')'
        FROM tbl_bwg_ag ba
        JOIN tbl_bewerbung b ON ba.bwg_ag_bwg_id = b.bwg_id
        JOIN tbl_bewerber be ON b.bwg_bw_id = be.bw_id
        JOIN tbl_firma f ON b.bwg_f_id = f.f_id
        JOIN tbl_arbeitgeber ag ON ba.bwg_ag_ag_id = ag.ag_id
        ORDER BY be.bw_nachname, ag.ag_datum_von DESC
    """)
    results = cursor.fetchall()
    bwg_ag_map = {text: bwg_ag_id for bwg_ag_id, text in results}
    combo_bwg_ag["values"] = list(bwg_ag_map.keys())

    # Tätigkeiten
    cursor.execute("SELECT t_id, t_name FROM tbl_taetigkeit ORDER BY t_name")
    results = cursor.fetchall()
    taetigkeit_map = {}
    listbox_taetigkeiten.delete(0, tk.END)
    for t_id, t_name in results:
        taetigkeit_map[t_name] = t_id
        listbox_taetigkeiten.insert(tk.END, t_name)


# TreeView
tree_frame = tk.Frame(root)
tree_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

tree_scroll = tk.Scrollbar(tree_frame)
tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

tree = ttk.Treeview(tree_frame, columns=("Zuordnung", "Tätigkeit"), show="headings", yscrollcommand=tree_scroll.set,
                    height=15)
tree.heading("Zuordnung", text="Bewerbung/Arbeitgeber")
tree.heading("Tätigkeit", text="Tätigkeit")
tree.column("Zuordnung", width=500)
tree.column("Tätigkeit", width=500)
tree.pack(fill=tk.BOTH, expand=True)

tree_scroll.config(command=tree.yview)


# TreeView neu laden
def reload_tree():
    tree.delete(*tree.get_children())
    cursor.execute("""
        SELECT bat.bwg_ag_t_id,
               be.bw_vorname || ' ' || be.bw_nachname || ' -> ' || f.f_name || ' -> ' || ag.ag_name || ' (' || ag.ag_datum_von || ')',
               t.t_name
        FROM tbl_bwg_ag_t bat
        JOIN tbl_bwg_ag ba ON bat.bwg_ag_t_bwg_ag_id = ba.bwg_ag_id
        JOIN tbl_bewerbung b ON ba.bwg_ag_bwg_id = b.bwg_id
        JOIN tbl_bewerber be ON b.bwg_bw_id = be.bw_id
        JOIN tbl_firma f ON b.bwg_f_id = f.f_id
        JOIN tbl_arbeitgeber ag ON ba.bwg_ag_ag_id = ag.ag_id
        JOIN tbl_taetigkeit t ON bat.bwg_ag_t_t_id = t.t_id
        ORDER BY ag.ag_datum_von DESC, be.bw_nachname
    """)
    for row in cursor.fetchall():
        tree.insert("", "end", iid=row[0], values=(row[1], row[2]))


# Tätigkeiten zuordnen
def add_taetigkeit():
    selected_bwg_ag = combo_bwg_ag.get()
    selected_indices = listbox_taetigkeiten.curselection()

    if not selected_bwg_ag or not selected_indices:
        messagebox.showwarning("Fehler", "Bitte eine Zuordnung und bis zu 3 Tätigkeiten auswählen.")
        return

    if len(selected_indices) > 3:
        messagebox.showwarning("Fehler", "Es dürfen maximal 3 Tätigkeiten ausgewählt werden.")
        return

    bwg_ag_id = bwg_ag_map[selected_bwg_ag]
    selected_t_ids = [taetigkeit_map[listbox_taetigkeiten.get(i)] for i in selected_indices]

    for t_id in selected_t_ids:
        # Vor dem Einfügen prüfen, ob die Zuordnung bereits existiert
        cursor.execute("""
            SELECT 1 FROM tbl_bwg_ag_t
            WHERE bwg_ag_t_bwg_ag_id = ? AND bwg_ag_t_t_id = ?
        """, (bwg_ag_id, t_id))

        if cursor.fetchone():
            messagebox.showwarning("Fehler",
                                   f"Die Zuordnung (Bewerbung/Arbeitgeber: {selected_bwg_ag} -> Tätigkeit: {listbox_taetigkeiten.get(selected_indices[0])}) existiert bereits!")
            return

        # Einfügen der Zuordnung, wenn sie noch nicht existiert
        cursor.execute("""
            INSERT INTO tbl_bwg_ag_t (bwg_ag_t_bwg_ag_id, bwg_ag_t_t_id)
            VALUES (?, ?)
        """, (bwg_ag_id, t_id))

    conn.commit()
    reload_tree()


# Eintrag löschen
def delete_entry():
    selected_items = tree.selection()
    if not selected_items:
        messagebox.showwarning("Fehler", "Bitte mindestens eine Tätigkeit auswählen.")
        return

    if messagebox.askyesno("Löschen", f"{len(selected_items)} Eintrag/Einträge wirklich löschen?"):
        for item_id in selected_items:
            cursor.execute("DELETE FROM tbl_bwg_ag_t WHERE bwg_ag_t_id = ?", (item_id,))
        conn.commit()
        reload_tree()


# Buttons
tk.Button(root, text="Tätigkeiten zuordnen", command=add_taetigkeit).grid(row=2, column=0, padx=10, pady=10, sticky="w")
tk.Button(root, text="Ausgewählte Tätigkeit löschen", command=delete_entry).grid(row=2, column=1, padx=10, pady=10,
                                                                                 sticky="e")

# Initialisieren
refresh_data()
reload_tree()

root.mainloop()
