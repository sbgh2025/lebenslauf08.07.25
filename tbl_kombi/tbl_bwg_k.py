import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

# Verbindung zur SQLite-Datenbank
conn = sqlite3.connect("/home/birgit/PycharmProjects/LebenslaufTest/src/lb_datenbank/lebenslauf.db")
cursor = conn.cursor()

# Hauptfenster
root = tk.Tk()
root.title("Bewerbung <-> Kenntnisse verknüpfen")
root.geometry("950x550")

# GUI-Elemente
tk.Label(root, text="Bewerbung:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
tk.Label(root, text="Kenntnisse (Mehrfachauswahl):").grid(row=1, column=0, padx=10, pady=5, sticky="ne")

combo_bewerbung = ttk.Combobox(root, state="readonly", width=60)
combo_bewerbung.grid(row=0, column=1, padx=10, pady=5)

listbox_kenntnisse = tk.Listbox(root, selectmode=tk.MULTIPLE, width=60, height=8)
listbox_kenntnisse.grid(row=1, column=1, padx=10, pady=5)

bewerbung_map = {}
kenntnisse_map = {}


# Combobox und Listbox befüllen
def refresh_comboboxes():
    global bewerbung_map, kenntnisse_map
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

    # Kenntnisse laden (mit Stufe)
    cursor.execute("""
        SELECT k_id, k_name, k_stufe
        FROM tbl_kenntnisse
        ORDER BY k_name
    """)
    kenntnisse = cursor.fetchall()
    kenntnisse_map.clear()
    listbox_kenntnisse.delete(0, tk.END)

    for k_id, k_name, k_stufe in kenntnisse:
        # Kombiniere den Kenntnisnamen mit der Stufe für die Anzeige
        display_text = f"{k_name} (Stufe: {k_stufe})"
        kenntnisse_map[display_text] = k_id
        listbox_kenntnisse.insert(tk.END, display_text)


# TreeView zur Anzeige vorhandener Verknüpfungen
tree = ttk.Treeview(root, columns=("Bewerbung", "Kenntnisse"), show="headings")
tree.heading("Bewerbung", text="Bewerbung")
tree.heading("Kenntnisse", text="Kenntnisse")
tree.column("Bewerbung", width=400)
tree.column("Kenntnisse", width=400)
tree.grid(row=3, column=0, columnspan=2, padx=10, pady=10)


def reload_data():
    tree.delete(*tree.get_children())
    cursor.execute("""
        SELECT bk.bwg_k_id,
               be.bw_vorname || ' ' || be.bw_nachname || ' -> ' || f.f_name,
               GROUP_CONCAT(k.k_name || ' (Stufe: ' || k.k_stufe || ')', ', ')  -- mehrere Kenntnisse mit Stufe anzeigen
        FROM tbl_bwg_k bk
        JOIN tbl_bewerbung b ON bk.bwg_k_bwg_id = b.bwg_id
        JOIN tbl_bewerber be ON b.bwg_bw_id = be.bw_id
        JOIN tbl_firma f ON b.bwg_f_id = f.f_id
        JOIN tbl_kenntnisse k ON bk.bwg_k_k_id = k.k_id
        GROUP BY bk.bwg_k_id
        ORDER BY be.bw_nachname
    """)
    for row in cursor.fetchall():
        tree.insert("", "end", iid=row[0], values=(row[1], row[2]))


# Verknüpfung hinzufügen mit Duplikatprüfung
def add_k_record():
    b_text = combo_bewerbung.get()
    selected_indices = listbox_kenntnisse.curselection()

    if not b_text or not selected_indices:
        messagebox.showwarning("Fehler", "Bitte Bewerbung und mindestens eine Kenntnis auswählen.")
        return

    bwg_id = bewerbung_map[b_text]
    selected_k_ids = [kenntnisse_map[listbox_kenntnisse.get(i)] for i in selected_indices]

    for k_id in selected_k_ids:
        # Vor dem Einfügen prüfen, ob die Kombination (Bewerbung -> Kenntnis) bereits existiert
        cursor.execute("""
            SELECT 1 FROM tbl_bwg_k
            WHERE bwg_k_bwg_id = ? AND bwg_k_k_id = ?
        """, (bwg_id, k_id))

        if cursor.fetchone():  # Wenn ein Ergebnis gefunden wird, existiert die Kombination bereits
            messagebox.showwarning("Duplikat",
                                   f"Die Zuordnung (Bewerbung: {b_text} -> Kenntnis: {listbox_kenntnisse.get(selected_indices[0])}) existiert bereits!")
            return

        # Einfügen der Zuordnung, wenn sie noch nicht existiert
        cursor.execute("""
            INSERT INTO tbl_bwg_k (bwg_k_bwg_id, bwg_k_k_id)
            VALUES (?, ?)
        """, (bwg_id, k_id))

    conn.commit()
    reload_data()


# Verknüpfung löschen
def delete_k_record():
    selected_items = tree.selection()
    if not selected_items:
        messagebox.showwarning("Fehler", "Bitte mindestens einen Eintrag auswählen.")
        return
    if messagebox.askyesno("Löschen", f"Sind Sie sicher, dass Sie {len(selected_items)} Einträge löschen möchten?"):
        for item_id in selected_items:
            cursor.execute("DELETE FROM tbl_bwg_k WHERE bwg_k_id = ?", (item_id,))
        conn.commit()
        reload_data()


# Buttons
tk.Button(root, text="Zuordnung hinzufügen", command=add_k_record).grid(row=2, column=0, padx=10, pady=10, sticky="w")
tk.Button(root, text="Ausgewählte Zuordnung löschen", command=delete_k_record).grid(row=2, column=1, padx=10, pady=10,
                                                                                    sticky="e")

# Startinitialisierung
refresh_comboboxes()
reload_data()

root.mainloop()
