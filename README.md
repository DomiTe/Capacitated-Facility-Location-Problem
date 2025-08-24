# Beschreibung dieses Repositories

Dies ist ein Repository für die Implementierung und den Vergleich von Algorithmen zur Lösung mathematischer Probleme.
Das Repository ist in verschiedene Module (Python-Packages) unterteilt, die jeweils spezifische mathematische Probleme und deren Lösungen behandeln.
Es existiert ein Kernmodul, das generische Funktionen und Basisklassen bereitstellt, die von den spezifischen Modulen verwendet werden.

## Struktur des Repositories

```
.
├── lib/ # Kernbibliothek
├── projects/ # Projekte der Studierenden
│   ├── max_matchings/
│   ├── tsp/
│   ├── graph_coloring/
│   └── ...
├── data/ # Daten
├── docs/ # Dokumentation
│   ├── sphinx/ # Sphinx-Dokumentation
│   ├── projects_list.md # Liste der Projekte
│   └── ...
├── Taskfile.yml # Vordefinierte Tasks
├── dev_lib.code-workspace # Workspace für Lib-Entwicklung
├── dev_projects.code-workspace # Workspace für Entwicklung der Projekte
└── README.md # Diese Datei
```

- `lib/` Enthält die generische Kernbibliothek `problib`, die Utilitys, Basisklassen und Hilfsfunktionen für die Implementierung von Problemen bereitstellt.

- `projects/*` Jedes Projekt ist als Unterordner im `projects/`-Verzeichnis organisiert. Eine Übersicht der Projekte und den verwendeten Kürzeln ist in [`docs/projects_list.md`](docs/projects_list.md) zu finden. Jedes Projekt folgt der folgenden Struktur:
  - Eine eigene `README.md`, die Informationen zu den Implementierungen und den verwendeten Algorithmen enthält.
  - Eine eigene `pyproject.toml`-Datei, die Metadaten zu dem Projekt enthält.
  - Einen eigene `data/`-Ordner, der die Daten für das Projekt enthält.
  - Einen eigene `tests/`-Ordner, der die Tests für das Projekt enthält.
  - Ein eigenes Unterverzeichnis, das den Quellcode des Projektes enthält. Der Name des Unterverzeichnisses ist identisch mit dem Kürzel des Projektes.

```
projects/
├── <projekt_kürzel>/ # Kürzel des Projektes
│   ├── README.md # Spezifische Informationen zu dem Projekt
│   ├── pyproject.toml # Metadaten zu dem Python-Package
│   ├── data/ # Daten (für Datensätze und Benchmark-Daten)
│   ├── tests/
│   └── <projekt_kürzel>/ # Python-Package (Source-Code)
│       ├── __init__.py
│       └── ...
└── ...
```

- `data/` Enthält alle Daten, die für Projektübergreifende Benchmarks benötigt werden.
- `docs/` Enthält die Dokumentation des Repositories. Die Sphinx-Dokumentation wird aus dem `docs/sphinx`-Verzeichnis generiert. Zusätzlich gibt es weitere Markdown-Dateien im `docs/`, die Informationen zu den Projekten und deren Implementierung enthalten.
- `Taskfile.yml` Enthält vordefinierte Commands (Tasks), die mit dem Task-Runner [Task](https://taskfile.dev/) ausgeführt werden können.

## Setup

### Prerequisites

Die folgenden Tools müssen installiert sein:

- [uv](https://docs.astral.sh/uv/) (>= 0.6.14)
- [Task](https://taskfile.dev/) (>= 3.39.2)

### Installation

1. Klone dieses Repository:

```bash
git clone git@gitlab.rz.htw-berlin.de:s0574247/adm-semesterprojekt.git
```

2. Wechsle in das Verzeichnis des geklonten Repositories:

```bash
cd adm-semesterprojekt
```

3. Installiere die Pre-Commit Hooks:

```bash
task install-hooks
```

4. Wechsle in dein Projektverzeichnis (den Kürzel deines Projektes findest du in [`docs/projects_list.md`](docs/projects_list.md)):

```bash
cd projects/<dein_kürzel>
```

5. Installiere die Abhängigkeiten:

```bash
uv sync
```

6. Erstelle einen Branch für die Entwicklung:

```bash
git checkout -b <branch_name>
```

## Entwicklung mit uv

Immer wenn du Python-Code mit `uv` ausführen möchtest, musst du dies in deinem Projektverzeichnis tun. Bitte lese dir dazu die [uv-Dokumentation](https://docs.astral.sh/uv/) durch.

## Entwicklung eines Projektes

Wie in der [lib-README](lib/README.md) beschrieben, wird ein Problem und dessen Algorithmus implementiert, indem eine neue Klasse erstellt wird, die von der Basisklasse `BaseSolver` erbt.

Wenn in einem Projekt mehrere Algorithmen implementiert und verglichen werden, sollten diese jeweils in eigenen `BaseSolver`-Klassen implementiert werden.

Die Implementierung eines Algorithmus erfolgt in der `_solve()`-Methode, die in der erbenden `BaseSolver`-Klasse implementiert werden soll. Diese Methode wird von der `run()`-Methode aufgerufen, die das Aufrufen und Profiling des Algorithmus ermöglicht.

## Pre-Commit Hooks

Pre-Commit Hooks sind Skripte, die vor dem Commit eines Codes ausgeführt werden, um sicherzustellen, dass der Code den festgelegten Standards entspricht.

In diesem Repository sind Pre-Commit Hooks konfiguriert, um sicherzustellen, dass der Code den [PEP 8](https://peps.python.org/pep-0008/) Standards entspricht und keine Fehler enthält.
Konkret ist `ruff` als Checker und Formatter konfiguriert.
Um die Pre-Commit Hooks zu aktivieren, führe, falls nicht schon bei der Installation getan, den folgenden Befehl im Wurzelverzeichnis des Repositories aus:

```bash
task install-hooks
```

Wenn du ab jetzt `git commit` ausführst, werden die folgenden Hooks automatisch ausgeführt:

1. **Check**: Testes alle Python-Dateien den Commits auf Syntaxfehler und PEP-8-Konformität.
2. **Format**: Formatiert alle Python-Dateien. (Wenn eine Datei formatiert wurde, müssen die Änderungen gestaged werden, um die Änderungen auf den Commit zu übernehmen.)

Anschließend kannst du den Commit mit `git commit` abschließen.

## Docs mit Sphinx

Dieses Projekt wird mit einer konfigurierten Sphinx-Instanz Dokumentiert.
Damit euer Projekt (README und Code) in der Dokumentation erscheint, müssen einige Schritte beachtet werden:

- **README**: Jedes Projekt sollte eine eigene `README.md`-Datei im Projektverzeichnis haben, die Informationen zu dem Projekt enthält. Diese Datei wird automatisch in die Sphinx-Dokumentation eingebaut. Der Pfad zu dieser Datei ist z.B.: `/projects/tsp/README.md`.
- **Python-Code**: Der Python-Code (Klassen/ Funktionen) eures Projektes wird automatisch in die Sphinx-Dokumentation eingebaut, wenn er in der `__init__.py`-Datei des Projektes importiert wird. Diese Datei befindet sich im Quellcode-Verzeichnis eures Projektes, z.B. `/projects/tsp/tsp/__init__.py`. Zum Beispiel so:

```python
# Example for /projects/sort/sort/__init__.py
from sort.solver import BubblesortSolver, MergesortSolver
from sort.base import BasesortSolver
from sort.utils import useful_function

__all__ = [
    "BasesortSolver",
    "MergesortSolver",
    "BubblesortSolver",
    "useful_function",
]
```

- **Docstrings**: Jede Klasse oder Funktion, die in der Sphinx-Dokumentation erscheinen soll, sollte mit einem Docstring versehen sein. Die Docstrings sollten im [Google](https://github.com/google/styleguide/blob/gh-pages/pyguide.md#38-comments-and-docstrings) oder reST-Format verfasst sein, damit sie von Sphinx korrekt interpretiert werden können.

### Docs Bauen

Im Wurzelverzeichnis dieses Projektes die folgenden Tasks ausführen

```bash
task docs:gen
```

### HTTP-Server starten

Um die Docs im Browser anzuzeigen, mit folgendem Task einen Python-HTTP-Server starten

```bash
task docs:serve
```

Dann im Browser http://localhost:8000 öffnen.
