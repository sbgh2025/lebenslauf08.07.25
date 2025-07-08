import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import os
import sys

# Datenbankpfad einbinden
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../lb_datenbank")))

# Verbindung zur Datenbank
from db_pfad import get_connection, get_cursor
conn = get_connection()
cursor = get_cursor(conn)

# Hauptfenster
root = tk.Tk()
root.title("Bewerbung <-> Ausbildung verknüpfen")
root.geometry("1200x600")

root.grid_rowconfigure(3, weight=1)
root.grid_columnconfigure(1, weight=1)

# GUI-Elemente
tk.Label(root, text="Bewerbung:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
tk.Label(root, text="Ausbildung (Mehrfachauswahl):").grid(row=1, column=0, padx=10, pady=5, sticky="ne")

combo_bewerbung = ttk.Combobox(root, state="readonly", width=80)
combo_bewerbung.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

# Frame für Listbox + Scrollbars
listbox_frame = tk.Frame(root)
listbox_frame.grid(row=1, column=1, padx=10, pady=5, sticky="nsew")
listbox_frame.grid_rowconfigure(0, weight=1)
listbox_frame.grid_columnconfigure(0, weight=1)

scrollbar_y = tk.Scrollbar(listbox_frame, orient="vertical")
scrollbar_y.grid(row=0, column=1, sticky="ns")
scrollbar_x = tk.Scrollbar(listbox_frame, orient="horizontal")
scrollbar_x.grid(row=1, column=0, sticky="ew")

listbox_ab = tk.Listbox(
    listbox_frame,
    selectmode=tk.MULTIPLE,
    width=100,
    height=8,
    yscrollcommand=scrollbar_y.set,
    xscrollcommand=scrollbar_x.set
)
listbox_ab.grid(row=0, column=0, sticky="nsew")
scrollbar_y.config(command=listbox_ab.yview)
scrollbar_x.config(command=listbox_ab.xview)

# Mappings
bewerbung_map = {}
ausbildung_map = {}

def refresh_comboboxes():
    global bewerbung_map, ausbildung_map
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

    # Ausbildungen laden
    cursor.execute("""
        SELECT ab_id, ab_name_staette, ab_name_ausbildung, ab_datum_von, ab_datum_bis
        FROM tbl_ausbildung
        ORDER BY ab_datum_von DESC
    """)
    ausbildungen = cursor.fetchall()
    ausbildung_map.clear()
    listbox_ab.delete(0, tk.END)

    for ab_id, staette, ausbildung, von, bis in ausbildungen:
        display_text = f"{staette} – {ausbildung} ({von} bis {bis or 'heute'})"
        ausbildung_map[display_text] = ab_id
        listbox_ab.insert(tk.END, display_text)

# TreeView + Scrollbar
tree_frame = tk.Frame(root)
tree_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
tree_frame.grid_rowconfigure(0, weight=1)
tree_frame.grid_columnconfigure(0, weight=1)

scrollbar_tree = tk.Scrollbar(tree_frame, orient="vertical")
scrollbar_tree.grid(row=0, column=1, sticky="ns")

tree = ttk.Treeview(tree_frame, columns=("Bewerbung", "Ausbildung"), show="headings", selectmode="extended", yscrollcommand=scrollbar_tree.set)
tree.heading("Bewerbung", text="Bewerbung")
tree.heading("Ausbildung", text="Ausbildung")
tree.column("Bewerbung", width=500)
tree.column("Ausbildung", width=500)
tree.grid(row=0, column=0, sticky="nsew")
scrollbar_tree.config(command=tree.yview)

def reload_data():
    tree.delete(*tree.get_children())
    cursor.execute("""
        SELECT ba.bwg_ab_id,
               be.bw_vorname || ' ' || be.bw_nachname || ' -> ' || f.f_name,
               ab.ab_name_staette || ' – ' || ab.ab_name_ausbildung || ' (' || ab.ab_datum_von || ' bis ' || IFNULL(ab.ab_datum_bis, 'heute') || ')'
        FROM tbl_bwg_ab ba
        JOIN tbl_bewerbung b ON ba.bwg_ab_bwg_id = b.bwg_id
        JOIN tbl_bewerber be ON b.bwg_bw_id = be.bw_id
        JOIN tbl_firma f ON b.bwg_f_id = f.f_id
        JOIN tbl_ausbildung ab ON ba.bwg_ab_ab_id = ab.ab_id
        ORDER BY be.bw_nachname, ab.ab_datum_von DESC
    """)
    for row in cursor.fetchall():
        tree.insert("", "end", iid=row[0], values=(row[1], row[2]))

#add ab record

def add_ab_record():
    b_text = combo_bewerbung.get()
    selected_indices = listbox_ab.curselection()

    if not b_text or not selected_indices:
        messagebox.showwarning("Fehler", "Bitte Bewerbung und mindestens eine Ausbildung auswählen.")
        return

    bwg_id = bewerbung_map[b_text]
    selected_ab_ids = [ausbildung_map[listbox_ab.get(i)] for i in selected_indices]

    bereits_vorhanden = []

    for ab_id in selected_ab_ids:
        cursor.execute("""
            SELECT 1 FROM tbl_bwg_ab WHERE bwg_ab_bwg_id = ? AND bwg_ab_ab_id = ?
        """, (bwg_id, ab_id))
        if cursor.fetchone() is None:
            cursor.execute("""
                INSERT INTO tbl_bwg_ab (bwg_ab_bwg_id, bwg_ab_ab_id) VALUES (?, ?)
            """, (bwg_id, ab_id))
        else:
            # Anzeige-Text für Listbox-Eintrag finden
            for text, aid in ausbildung_map.items():
                if aid == ab_id:
                    bereits_vorhanden.append(text)
                    break

    conn.commit()
    reload_data()

    if bereits_vorhanden:
        info_text = "Folgende Verknüpfung(en) existierten bereits und wurden nicht erneut eingefügt:\n\n"
        info_text += "\n".join(bereits_vorhanden)
        messagebox.showinfo("Hinweis", info_text)


#add ab record ende


def delete_ab_record():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Fehler", "Bitte mindestens einen Eintrag auswählen.")
        return

    if not messagebox.askyesno("Löschen", f"{len(selected)} Eintrag(e) wirklich löschen?"):
        return

    for bwg_ab_id in selected:
        cursor.execute("DELETE FROM tbl_bwg_ab WHERE bwg_ab_id = ?", (bwg_ab_id,))

    conn.commit()
    reload_data()

# Buttons
tk.Button(root, text="Zuordnung hinzufügen", command=add_ab_record).grid(row=2, column=0, padx=10, pady=10, sticky="w")
tk.Button(root, text="Ausgewählte Zuordnung löschen", command=delete_ab_record).grid(row=2, column=1, padx=10, pady=10, sticky="e")

# Initialisierung
refresh_comboboxes()
reload_data()

# Hauptloop
root.mainloop()
