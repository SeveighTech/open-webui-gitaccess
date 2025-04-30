**# GitAccess**

![GitAccess Logo](https://i.imgur.com/1PxbyHA.png)

**GitAccess** ist ein Tool, das es LLM-Modellen ermöglicht, sich mit GitHub-Repositories innerhalb eines bestimmten Accounts oder einer Organisation zu verbinden, um deren Inhalte, Issues, Pull Requests und mehr abzurufen. So kannst du das Modell über den aktuellen Stand eines Projekts befragen und stets auf dem neuesten Stand bleiben.

**## 📦 Beschreibung**

*   **Autoren:** ErrorRExorY/CptExorY, [SeveighTech](https://seveightech.com)), [Josetseph](https://github.com/josetseph))
*   **Autoren Website:** [pascal-frerks.de](https://pascal-frerks.de)
*   **GitHub Repository:** [GitAccess auf GitHub](https://github.com/WhyWaitServices/open-webui-gitaccess.git)
*   **Erforderliche OpenWebUI-Version:** 0.6.0
*   **Version:** 0.2.0 (Aktualisiert von SeveighTech)
*   **Lizenz:** MIT

**Wichtige Aktualisierungen von SeveighTech (Version 0.2.0):**

*   Unterstützung für das Abrufen von Issues, Pull Requests, Kommentaren und Dateiänderungen in Pull Requests hinzugefügt.
*   Repository-Suche nach Teilnamen implementiert.
*   Konfigurierbare Limits für die Anzahl der abgerufenen Elemente und Kommentare eingeführt.
*   Verbesserte Fehlerbehandlung und Statusaktualisierungen.

**## 🚀 Installation**

Um GitAccess in deiner selbst gehosteten OpenWebUI-Instanz zu installieren, kannst du den folgenden Schritten folgen:

**### Über den Marktplatz**

1.  Öffne deine OpenWebUI Instanz.
2.  Gehe zum [Marktplatz](https://openwebui.com/t/cptexory/gitaccess "Marktplatz").
3.  Füge den Link zu GitAccess hinzu: `https://github.com/WhyWaitServices/open-webui-gitaccess.git`.

**### Manuelle Installation**

1.  Kopiere den Code aus der `GitAccess.py` Datei.
2.  Füge den kopierten Code zu deiner OpenWebUI-Instanz hinzu, indem du unter Arbeitsbereich > Werkzeuge ein neues Tool erstellst.
3.  Füge den kopierten Code aus der `GitAccess.py` Datei im großen Eingabefeld ein und vergib einen Namen und eine Beschreibung.
4.  Speichere das Tool.

**## ⚙️ Konfiguration**

**### Umgebungsvariablen (Valves)**

*   **Zugang zu den Valves:** Die Umgebungsvariablen für das Tool werden in der OpenWebUI gesetzt. Klicke auf den Zahnrad-Button, wenn du das Tool öffnest, um die Valves zu konfigurieren.

*   **access_token:** Ein persönlicher Zugriffstoken von GitHub, das die erforderlichen Zugriffsrechte auf das Repository hat.
*   **owner:** Der Name des GitHub-Accounts/der Organisation (z.B. `SeveighTech`).

**### UserValves**

*   **Setzen der UserValves:** Wenn du das Tool in einem Chat oder Modell aktiviert hast, kannst du die UserValves über den „Controls“-Button (oben rechts, direkt links neben dem Profilbild) setzen. Ein Sheet wird geöffnet, wo du die UserValves des Tools konfigurieren kannst.

*   **max_files:** Maximale Anzahl von Dateien pro Verzeichnis, die abgerufen werden sollen.
*   **truncate_content:** Ob große Dateien zur besseren Lesbarkeit gekürzt werden sollen.
*   **max_content_length:** Maximale Zeichenlänge für Dateiinhalte, wenn die Kürzung aktiviert ist.
*   **max_items:** Maximale Anzahl von Issues, Pull Requests usw., die pro Status (offen/geschlossen) abgerufen werden sollen.
*   **max_comments:** Maximale Anzahl von Kommentaren, die für Issues und Pull Requests abgerufen werden sollen.

**## 🛠️ Nutzung**

Nach der Installation kannst du GitAccess wie folgt nutzen:

1.  Stelle sicher, dass du richtig konfiguriert bist (Zugriffstoken und Owner).
2.  Starte das Tool in deiner OpenWebUI-Instanz.
3.  Verwende einfache Prompts wie:

*   "Was sind die Pull Requests, Pull Request Kommentare und die Pull Request Dateiänderungen im `{repository_name}` Repository?"
*   "Erzähl mir mehr über das `{repository_name}` Repository."
*   "Gib mir alle Kommentare zu jedem Issue im `{repository_name}` Repository."
*   "Gibt es irgendwelche Issues oder Pull Requests im Repository: `{repository_name}`"
*   "Kannst du mir mehr Details über PR #{PR_number}: "{PR_title}" Pull Request im `{repository_name}` Repository geben?"

Die Antwort könnte wie folgt aussehen:
![Example Screenshot](https://i.imgur.com/1PxbyHA.png)

Der Status der Aktionen wird in der Benutzeroberfläche durch Statusmeldungen angezeigt.

**## 🤖 Funktionen**

*   **Repository Inhalte abrufen:** Lese die Struktur und die Dateien eines angegebenen GitHub-Repositories.
*   **Dynamische Filter:** Unterscheidung zwischen Verzeichnissen und Dateien, um die gewünschten Daten effizient abzurufen.
*   **Ereignis-Emitter:** Echtzeit-Feedback über die Progression der Abfragen und andere Aktionen.
*   **Issue- und Pull Request-Analyse:** Abrufen und Analysieren von Issues, Pull Requests und zugehörigen Kommentaren.
*   **Repository-Suche:** Finden von Repositories anhand von Teilnamen innerhalb des konfigurierten Owners.

**## 📋 Lizenz**

Dieses Projekt steht unter der MIT Lizenz. Weitere Informationen findest du in der [LICENSE](LICENSE) Datei.

**## 🤝 Mitwirken**

Beiträge sind willkommen! Bitte öffne ein Issue oder eine Pull-Request, um Anregungen zu teilen oder Verbesserungen vorzuschlagen.

**## 📞 Kontakt**

Bei Fragen oder Feedback kannst du ein Issue eröffnen.

Vielen Dank, dass du GitAccess nutzt!