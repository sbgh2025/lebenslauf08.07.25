import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import os
import sys

# Pfad zur Datenbankfunktion (hier anpassen, falls nötig)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../lb_datenbank")))

# Verbindung zur DB importieren
from db_pfad import get_connection, get_cursor
conn = get_connection()
cursor = get_cursor(conn)

root = tk.Tk()
root.title("Bewerbung/Arbeitgeber <-> Ausbildung/Schwerpunkt")
root.geometry("1000x600")

# Dynamische Größenanpassung
root.grid_rowconfigure(3, weight=1)
root.grid_columnconfigure(1, weight=1)

# UI-Elemente
tk.Label(root, text="Bewerbung/Arbeitgeber-Zuordnung:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
tk.Label(root, text="Schwerpunkte (bis zu 3 auswählen):").grid(row=1, column=0, padx=10, pady=5, sticky="ne")

combo_bwg_ab = ttk.Combobox(root, state="readonly", width=70)
combo_bwg_ab.grid(row=0, column=1, padx=10, pady=5)

listbox_frame = tk.Frame(root)
listbox_frame.grid(row=1, column=1, padx=10, pady=5, sticky="w")

listbox_schwerpunkte = tk.Listbox(listbox_frame, selectmode=tk.MULTIPLE, width=68, height=8)
listbox_schwerpunkte.pack(side=tk.LEFT, fill=tk.BOTH)

scrollbar_schwerpunkte = tk.Scrollbar(listbox_frame, orient=tk.VERTICAL)
scrollbar_schwerpunkte.pack(side=tk.RIGHT, fill=tk.Y)

listbox_schwerpunkte.config(yscrollcommand=scrollbar_schwerpunkte.set)
scrollbar_schwerpunkte.config(command=listbox_schwerpunkte.yview)

# Maps für Auswahl und Zuordnung
bwg_ab_map = {}
schwerpunkt_map = {}

def refresh_data():
    global bwg_ab_map, schwerpunkt_map

    # Alle Bewerbung-Ausbildung-Zuordnungen mit lesbarem Text laden
    cursor.execute("""
        SELECT ba.bwg_ab_id,
               be.bw_vorname || ' ' || be.bw_nachname || ' -> ' || f.f_name || 
               ' (' || ab.ab_name_staette || ' – ' || ab.ab_name_ausbildung || ')'
        FROM tbl_bwg_ab ba
        JOIN tbl_bewerbung b ON ba.bwg_ab_bwg_id = b.bwg_id
        JOIN tbl_bewerber be ON b.bwg_bw_id = be.bw_id
        JOIN tbl_firma f ON b.bwg_f_id = f.f_id
        JOIN tbl_ausbildung ab ON ba.bwg_ab_ab_id = ab.ab_id
        ORDER BY ab.ab_datum_von DESC
    """)
    results = cursor.fetchall()
    bwg_ab_map = {text: bwg_ab_id for bwg_ab_id, text in results}
    combo_bwg_ab["values"] = list(bwg_ab_map.keys())
    combo_bwg_ab.set('')  # Auswahl löschen

    # Schwerpunkte laden (sortiert)
    cursor.execute("SELECT ab_swp_id, ab_swp_name FROM tbl_ab_schwerpunkt ORDER BY ab_swp_name")
    results = cursor.fetchall()
    schwerpunkt_map = {}
    listbox_schwerpunkte.delete(0, tk.END)
    for ab_swp_id, ab_swp_name in results:
        schwerpunkt_map[ab_swp_name] = ab_swp_id
        listbox_schwerpunkte.insert(tk.END, ab_swp_name)

def reload_tree():
    tree.delete(*tree.get_children())
    cursor.execute("""
        SELECT bas.bwg_ab_swp_id,
               be.bw_vorname || ' ' || be.bw_nachname || ' -> ' || f.f_name || 
               ' (' || ab.ab_name_staette || ' – ' || ab.ab_name_ausbildung || ')',
               swp.ab_swp_name
        FROM tbl_bwg_ab_swp bas
        JOIN tbl_bwg_ab ba ON bas.bwg_ab_swp_bwg_ab_id = ba.bwg_ab_id
        JOIN tbl_bewerbung b ON ba.bwg_ab_bwg_id = b.bwg_id
        JOIN tbl_bewerber be ON b.bwg_bw_id = be.bw_id
        JOIN tbl_firma f ON b.bwg_f_id = f.f_id
        JOIN tbl_ausbildung ab ON ba.bwg_ab_ab_id = ab.ab_id
        JOIN tbl_ab_schwerpunkt swp ON bas.bwg_ab_swp_ab_swp_id = swp.ab_swp_id
        ORDER BY ab.ab_datum_von DESC
    """)
    for row in cursor.fetchall():
        # "(Keine)" wird im Baum als "❌ Keine Schwerpunkte" angezeigt
        anzeige_text = row[2] if row[2] != "(Keine)" else "❌ Keine Schwerpunkte"
        tree.insert("", "end", iid=row[0], values=(row[1], anzeige_text))

def add_schwerpunkt():
    selected_bwg_ab = combo_bwg_ab.get()
    if not selected_bwg_ab:
        messagebox.showwarning("Fehler", "Bitte eine Zuordnung auswählen.")
        return

    bwg_ab_id = bwg_ab_map[selected_bwg_ab]
    selected_indices = listbox_schwerpunkte.curselection()

    # Wenn keine Auswahl -> Dummy "(Keine)" zuordnen
    if len(selected_indices) == 0:
        dummy_id = 0  # ID vom Dummy-Schwerpunkt "(Keine)"

        cursor.execute("""
            SELECT 1 FROM tbl_bwg_ab_swp
            WHERE bwg_ab_swp_bwg_ab_id = ? AND bwg_ab_swp_ab_swp_id = ?
        """, (bwg_ab_id, dummy_id))
        if cursor.fetchone():
            messagebox.showinfo("Hinweis", "Dieser Datensatz enthält bereits die Kennzeichnung '(Keine)'.")
            return

        # Vorher alle anderen Schwerpunkte für diesen Eintrag löschen, um Konflikte zu vermeiden
        cursor.execute("""
            DELETE FROM tbl_bwg_ab_swp WHERE bwg_ab_swp_bwg_ab_id = ? AND bwg_ab_swp_ab_swp_id != ?
        """, (bwg_ab_id, dummy_id))

        cursor.execute("""
            INSERT INTO tbl_bwg_ab_swp (bwg_ab_swp_bwg_ab_id, bwg_ab_swp_ab_swp_id)
            VALUES (?, ?)
        """, (bwg_ab_id, dummy_id))
        conn.commit()
        reload_tree()
        messagebox.showinfo("Hinweis", "Es wurde gespeichert: Keine Schwerpunkte ausgewählt.")
        return

    if len(selected_indices) > 3:
        messagebox.showwarning("Fehler", "Es dürfen maximal 3 Schwerpunkte ausgewählt werden.")
        return

    # Wenn Schwerpunkte ausgewählt sind, vorher den Dummy-Eintrag löschen
    cursor.execute("""
        DELETE FROM tbl_bwg_ab_swp WHERE bwg_ab_swp_bwg_ab_id = ? AND bwg_ab_swp_ab_swp_id = 0
    """, (bwg_ab_id,))

    selected_swp_ids = [schwerpunkt_map[listbox_schwerpunkte.get(i)] for i in selected_indices]

    bereits_vorhanden = []
    for swp_id in selected_swp_ids:
        cursor.execute("""
            SELECT 1 FROM tbl_bwg_ab_swp
            WHERE bwg_ab_swp_bwg_ab_id = ? AND bwg_ab_swp_ab_swp_id = ?
        """, (bwg_ab_id, swp_id))
        if cursor.fetchone():
            bereits_vorhanden.append(swp_id)
            continue

        cursor.execute("""
            INSERT INTO tbl_bwg_ab_swp (bwg_ab_swp_bwg_ab_id, bwg_ab_swp_ab_swp_id)
            VALUES (?, ?)
        """, (bwg_ab_id, swp_id))

    conn.commit()
    reload_tree()

    if bereits_vorhanden:
        namen = [name for name, sid in schwerpunkt_map.items() if sid in bereits_vorhanden]
        messagebox.showinfo("Hinweis ❗", "❗ Folgende Schwerpunkte wurden nicht gespeichert, da sie bereits vorhanden sind:\n- " + "\n- ".join(namen))
    else:
        messagebox.showinfo("Erfolg", "✅ Alle Schwerpunkte wurden erfolgreich gespeichert.")

# delete entry
def delete_entry():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Fehler", "Bitte einen oder mehrere Schwerpunkte im Baum auswählen.")
        return

    if not messagebox.askyesno("Löschen",
                               f"{len(selected)} Eintrag{'e' if len(selected) > 1 else ''} wirklich löschen?"):
        return

    for bwg_ab_swp_id in selected:
        cursor.execute("DELETE FROM tbl_bwg_ab_swp WHERE bwg_ab_swp_id = ?", (bwg_ab_swp_id,))

    conn.commit()
    reload_tree()
    messagebox.showinfo("Erfolg", f"{len(selected)} Eintrag{'e' if len(selected) > 1 else ''} gelöscht.")


# Buttons
tk.Button(root, text="Schwerpunkte zuordnen", command=add_schwerpunkt).grid(row=2, column=0, padx=10, pady=10, sticky="w")
tk.Button(root, text="Ausgewählten Schwerpunkt löschen", command=delete_entry).grid(row=2, column=1, padx=10, pady=10, sticky="e")

# Treeview
tree_frame = tk.Frame(root)
tree_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

tree_scrollbar = tk.Scrollbar(tree_frame, orient="vertical")
tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

tree = ttk.Treeview(tree_frame, columns=("Zuordnung", "Schwerpunkt"), show="headings", yscrollcommand=tree_scrollbar.set)
tree.heading("Zuordnung", text="Bewerbung/Arbeitgeber")
tree.heading("Schwerpunkt", text="Schwerpunkt")
tree.column("Zuordnung", width=450)
tree.column("Schwerpunkt", width=450)
tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

tree_scrollbar.config(command=tree.yview)

# Initiales Laden
refresh_data()
reload_tree()

root.mainloop()
