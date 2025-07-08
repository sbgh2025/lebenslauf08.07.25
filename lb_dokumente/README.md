

# 🗂 Lebenslauf-Datenbank-System mit Python, SQLite & GUI

Dieses Projekt ist ein vollständiges System zur Verwaltung und Bearbeitung von Lebensläufen mit **Python**, **SQLite** und **Tkinter**. Es bietet eine relationale Datenbankstruktur, ein GUI-Frontend, CSV-Importmöglichkeiten und einen strukturierten Excel-Export von Lebensläufen.

---

## 📁 Projektstruktur

```plaintext
src/
├── lb_index.py                         # Hauptstartpunkt (GUI)
├── lb_datenbank/
│   ├── lb_datenbank.py                # Erstellt die SQLite-Datenbank
│   └── lb_db_inhalt.py                # Zeigt den aktuellen Datenbankinhalt
├── lb_dokumente/
│   └── README.md                      # Projektdokumentation
├── lb_lebenslauf/
│   ├── lebenslauf_erstellen.py       # Exportiert Lebenslauf als Excel-Datei
│   ├── foto.png                       # Beispiel-Profilfoto
│   └── unterschrift.png              # Beispiel-Unterschrift
├── tbl_grund/
│   ├── tbl_bewerber.py
│   ├── tbl_firma.py
│   ├── tbl_arbeitgeber.py
│   ├── tbl_taetigkeit.py
│   ├── tbl_ausbildung.py
│   ├── tbl_ab_schwerpunkt.py
│   ├── tbl_kenntnisse.py
│   └── tbl_interessen.py
├── tbl_kombi/
│   ├── tbl_bewerbung.py
│   ├── tbl_bwg_ag.py
│   ├── tbl_bwg_ag_t.py
│   ├── tbl_bwg_ab.py
│   ├── tbl_bwg_ab_swp.py
│   ├── tbl_bwg_k.py
│   └── tbl_bwg_i.py

🔧 Technologien
Technologie	Beschreibung	Installation nötig
Python 3.x	Programmiersprache	✅ erforderlich
Tkinter	GUI-Toolkit (Standardbibliothek)	❌ nein
sqlite3	SQLite-Datenbank (Standardbibliothek)	❌ nein
csv	CSV-Unterstützung (Standardbibliothek)	❌ nein
os, sys	Systemoperationen und Prozesssteuerung (Standard)	❌ nein
openpyxl	Excel-Dateien lesen und schreiben	✅ ja
📦 Installation

Nur eine externe Bibliothek muss installiert werden:

pip install openpyxl

Alle anderen verwendeten Module stammen aus der Standardbibliothek von Python 3.x und müssen nicht separat installiert werden.
⚙️ Anwendung starten

GUI starten:

python src/lb_index.py

Datenbank erstellen:

python src/lb_datenbank/lb_datenbank.py

Datenbankinhalt anzeigen:

python src/lb_datenbank/lb_db_inhalt.py

🧩 Datenbankstruktur

Die relationale Datenbank lebenslauf.db besteht aus logisch verknüpften Tabellen:
Tabelle	Inhalt
tbl_bewerber	Persönliche Daten
tbl_firma	Zielunternehmen
tbl_bewerbung	Bewerbung
tbl_arbeitgeber	Berufliche Stationen
tbl_taetigkeit	Tätigkeiten
tbl_ausbildung	Ausbildungsstationen
tbl_ab_schwerpunkt	Ausbildungsschwerpunkte
tbl_kenntnisse	Fachliche Kenntnisse
tbl_interessen	Persönliche Interessen
🔗 Verknüpfungstabellen

Diese Tabellen verbinden Bewerbungen mit Arbeitgebern, Tätigkeiten, Ausbildungen, Kenntnissen und Interessen:
Tabelle	Zweck
tbl_bwg_ag	Bewerbung ↔ Arbeitgeber
tbl_bwg_ag_t	Bewerbung ↔ Arbeitgeber ↔ Tätigkeit (1 bis zu 3 Tätigkeiten)
tbl_bwg_ab	Bewerbung ↔ Ausbildungsstation
tbl_bwg_ab_swp	Bewerbung ↔ Ausbildungsstätte ↔ Schwerpunkt (0 bis zu 3 Schwerpunkte)
tbl_bwg_k	Bewerbung ↔ Kenntnisse
tbl_bwg_i	Bewerbung ↔ Interessen
🖼 GUI-Funktionalität

Das Tkinter-Frontend ermöglicht:

    Hinzufügen, Bearbeiten, Anzeigen und Löschen von Datensätzen

    Import von CSV-Dateien in alle Grundtabellen

📄 Unterstützte CSV-Formate

# tbl_bewerber
Vorname,Nachname,Geburtsdatum,Straße,PLZ,Ort,E-Mail,Telefon

# tbl_firma
Datum,Stellenbezeichnung,Firmenname,Straße,PLZ,Ort,E-Mail,Telefon
(Datumseingabe in Form JJJJ-MM-TT)

# tbl_arbeitgeber
Datum von,Datum bis,Firmenname,Zeitraum,Funktion,Ort,Leihfirma,Bemerkung
(Datumseingabe in Form JJJJ-MM-TT)

# tbl_taetigkeit
Tätigkeit

# tbl_ausbildung
Datum von,Datum bis,Ausbildungsstätte,Ausbildung,Abschluss,Zeitraum

# tbl_ab_schwerpunkt
Schwerpunkt

# tbl_kenntnisse
Kenntnis,Stufe

# tbl_interessen
Interesse

📤 Lebenslauf-Export (Excel)

Ein strukturierter Lebenslauf kann inkl. Foto und Unterschrift erstellt werden mit:

python src/lb_lebenslauf/lebenslauf_erstellen.py

Die Datei wird gespeichert als:

Lebenslauf_Bewerbung_<ID>_<Datum>.xlsx

Enthaltene Daten:

    Titel: Lebenslauf

    Persönliche Daten + Foto

    Berufserfahrung + Tätigkeiten

    Ausbildung + Schwerpunkte

    Kenntnisse + Einstufungen

    Interessen

    Ort, Datum, Unterschrift (optional)

🔮 Zukünftige Erweiterungen

    Validierung von Datumsfeldern

    Such- und Sortierfunktionen im GUI

    PDF-Export

    Benutzer-Login und -Verwaltung

  
