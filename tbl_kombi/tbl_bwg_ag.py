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
root.title("Bewerbung <-> Arbeitgeber verknüpfen")
root.geometry("950x550")

# GUI-Elemente
tk.Label(root, text="Bewerbung:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
tk.Label(root, text="Arbeitgeber (Mehrfachauswahl):").grid(row=1, column=0, padx=10, pady=5, sticky="ne")

combo_bewerbung = ttk.Combobox(root, state="readonly", width=60)
combo_bewerbung.grid(row=0, column=1, padx=10, pady=5)

# Frame für Arbeitgeber-Liste und Scrollbar
frame_ag = tk.Frame(root)
frame_ag.grid(row=1, column=1, padx=10, pady=5, sticky="nsew")

scrollbar_ag = tk.Scrollbar(frame_ag, orient="vertical")
scrollbar_ag.pack(side="right", fill="y")

listbox_ag = tk.Listbox(frame_ag, selectmode=tk.MULTIPLE, width=60, height=8, yscrollcommand=scrollbar_ag.set)
listbox_ag.pack(side="left", fill="both", expand=True)

scrollbar_ag.config(command=listbox_ag.yview)

bewerbung_map = {}
arbeitgeber_map = {}

# Combobox und Listbox befüllen
def refresh_comboboxes():
    global bewerbung_map, arbeitgeber_map

    # Bewerbungen laden
    cursor.execute("""
        SELECT b.bwg_id, be.bw_vorname || ' ' || be.bw_nachname || ' -> ' || f.f_name
        FROM tbl_bewerbung b
        JOIN tbl_bewerber be ON b.bwg_bw_id = be.bw_id
        JOIN tbl_firma f ON b.bwg_f_id = f.f_id
    """)
    bewerbungen = cursor.fetchall()
    bewerbung_map = {text: bwg_id for bwg_id, text in bewerbungen}
    combo_bewerbung["values"] = list(bewerbung_map.keys())

    # Arbeitgeber laden, sortiert nach ag_datum_bis DESC
    cursor.execute("""
        SELECT ag_id, ag_name, ag_datum_bis FROM tbl_arbeitgeber
        ORDER BY ag_datum_bis DESC
    """)
    arbeitgeber = cursor.fetchall()
    arbeitgeber_map.clear()
    listbox_ag.delete(0, tk.END)

    for ag_id, ag_name, ag_datum_bis in arbeitgeber:
        display_text = f"{ag_name} ({ag_datum_bis})"
        arbeitgeber_map[display_text] = ag_id
        listbox_ag.insert(tk.END, display_text)

# TreeView zur Anzeige vorhandener Verknüpfungen
tree_frame = tk.Frame(root)  # Frame für Treeview und Scrollbar
tree_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

scrollbar_tree = tk.Scrollbar(tree_frame, orient="vertical")
scrollbar_tree.pack(side="right", fill="y")

tree = ttk.Treeview(tree_frame, columns=("Bewerbung", "Arbeitgeber"), show="headings", yscrollcommand=scrollbar_tree.set, selectmode="extended")
tree.heading("Bewerbung", text="Bewerbung")
tree.heading("Arbeitgeber", text="Arbeitgeber")
tree.column("Bewerbung", width=400)
tree.column("Arbeitgeber", width=400)
tree.pack(side="left", fill="both", expand=True)

scrollbar_tree.config(command=tree.yview)

# TreeView Daten aktualisieren
def reload_data():
    tree.delete(*tree.get_children())
    cursor.execute("""
        SELECT ba.bwg_ag_id,
               be.bw_vorname || ' ' || be.bw_nachname || ' -> ' || f.f_name,
               ag.ag_name || ' (' || ag.ag_datum_bis || ')'
        FROM tbl_bwg_ag ba
        JOIN tbl_bewerbung b ON ba.bwg_ag_bwg_id = b.bwg_id
        JOIN tbl_bewerber be ON b.bwg_bw_id = be.bw_id
        JOIN tbl_firma f ON b.bwg_f_id = f.f_id
        JOIN tbl_arbeitgeber ag ON ba.bwg_ag_ag_id = ag.ag_id
        ORDER BY ag.ag_datum_bis DESC
    """)
    for row in cursor.fetchall():
        tree.insert("", "end", iid=row[0], values=(row[1], row[2]))

# Verknüpfung hinzufügen
def add_ag_record():
    b_text = combo_bewerbung.get()
    selected_indices = listbox_ag.curselection()

    if not b_text or not selected_indices:
        messagebox.showwarning("Fehler", "Bitte Bewerbung und mindestens einen Arbeitgeber auswählen.")
        return

    bwg_id = bewerbung_map[b_text]
    selected_ag_ids = [arbeitgeber_map[listbox_ag.get(i)] for i in selected_indices]

    existing = []
    to_add = []

    # Prüfen, welche Zuordnungen schon existieren und welche neu sind
    for ag_id in selected_ag_ids:
        cursor.execute("""
            SELECT 1 FROM tbl_bwg_ag
            WHERE bwg_ag_bwg_id = ? AND bwg_ag_ag_id = ?
        """, (bwg_id, ag_id))
        if cursor.fetchone():
            # Arbeitgeber-Name für die Warnung holen
            ag_name = [key for key, val in arbeitgeber_map.items() if val == ag_id][0]
            existing.append(ag_name)
        else:
            to_add.append(ag_id)

    if existing:
        messagebox.showwarning(
            "Warnung",
            f"Die folgenden Zuordnungen existieren bereits und werden nicht erneut hinzugefügt:\n- " +
            "\n- ".join(existing)
        )

    # Neue Zuordnungen hinzufügen
    for ag_id in to_add:
        cursor.execute("""
            INSERT INTO tbl_bwg_ag (bwg_ag_ag_id, bwg_ag_bwg_id) VALUES (?, ?)
        """, (ag_id, bwg_id))

    if to_add:
        conn.commit()
        reload_data()
    else:
        messagebox.showinfo("Info", "Keine neuen Zuordnungen zum Hinzufügen vorhanden.")
















# Verknüpfung löschen
def delete_ag_record():
    selected_items = tree.selection()
    if not selected_items:
        messagebox.showwarning("Fehler", "Bitte mindestens einen Eintrag auswählen.")
        return

    if not messagebox.askyesno("Löschen", "Ausgewählte Einträge wirklich löschen?"):
        return

    for item_id in selected_items:
        cursor.execute("DELETE FROM tbl_bwg_ag WHERE bwg_ag_id = ?", (item_id,))

    conn.commit()
    reload_data()

# Buttons
tk.Button(root, text="Zuordnung hinzufügen", command=add_ag_record).grid(row=2, column=0, padx=10, pady=10, sticky="w")
tk.Button(root, text="Ausgewählte Zuordnung löschen", command=delete_ag_record).grid(row=2, column=1, padx=10, pady=10, sticky="e")

# Startinitialisierung
refresh_comboboxes()
reload_data()

# GUI starten
root.mainloop()
