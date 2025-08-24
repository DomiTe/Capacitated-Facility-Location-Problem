# Overview

Die `problib`-Bibliothek ist eine Sammlung von Basisklassen, Utilitys und Hilfsfunktionen, die für die Implementierung von algorithmischen Lösungen in verschiedenen Projekten verwendet werden.
Die Bibliothek ist in verschiedene Module unterteilt, die jeweils spezifische Funktionen und Klassen bereitstellen.

## Solver

Das `Solver`-Modul enthält die Basisklasse [`BaseSolver`](#problib.core.solver.BaseSolver), die als Grundlage für alle algorithmischen Lösungen in den Projekten dient.

### Profiling

Die Methode `run()` von der [`BaseSolver`](#problib.core.solver.BaseSolver)-Klasse ist die zentrale Methode, die den Algorithmus aufruft.
Sie kann mit dem `cProfile`-Modul einen algorithmus profilieren, um die Laufzeit und den Aufruf von Funktionen zu analysieren.
Der optionale Parameter `profile` kann auf `True` gesetzt werden, um das Profiling zu aktivieren.

Nach einem erfolgreichen Profiling werden zwei Dateien im Profiling-Ordner gespeichert:

- `stats.dat`: Eine Binärdatei, die die Profiling-Daten enthält.
- `stats.txt`: Eine Textdatei, die die Profiling-Daten in einem lesbaren Format enthält.

Die Profiling-Daten werden in einem Unterverzeichnis des `profiling`-Ordners gespeichert, das mit dem aktuellen Datum und der Uhrzeit benannt ist.

```
<projekt_kürzel>/
├── data/
│   └── profiling/
│       ├── YYYYMMDD_HHMMSS/ # <-- Current run
│       │   ├── stats.dat
│       │   └── stats.txt
│       └── ...
└── ...
```

Die `run()`-Methode ruft dann intern die `_solve()`-Methode auf, die den eigentlichen Algorithmus implementiert.
Nachfolgend ist schematisch dargestellt, wie die `run()`-Methode den Algorithmus aufruft und das Profiling durchführt:

```python
class BaseSolver:
    ...
    def run(self, profile=False) -> None:
        if profile:
            # Run the algorithm with profiling
            cProfile.profile(self._solve())
            return

        # No profiling, just run the algorithm
        self._solve()
```

```{note}
Dabei gibt weder die `run()`- noch die `_solve()`-Methode eine Rückgabe zurück!
```

Es ist vorgesehen, dass Daten mittels über Instanzvariablen gespeichert und abgerufen werden.
Das Laden der Daten könnte demnach mit einer Methode `load_data()` erfolgen, die in der erbenden Klasse implementiert werden muss.
`load_data()` speichert die Daten in Instanzvariablen, zum Beispiel: `self.data`, die dann in der `_solve()`-Methode benutzt werden können.
Anschließend kann das Ergebnis in einer Instanzvariablen gespeichert werden, z.B. `self.result`, das dann über eine Getter-Methode abgerufen werden kann.

```python
from problib.core.solver import BaseSolver

class BubblesortSolver(BaseSolver):
    ...
    def load_data(self):
        # Load data and store it in instance variables
        self.data = ...

    def _solve(self):
        # Implement the algorithm using self.data
        ...
        self.result = ...

    def get_result(self):
        # Return the result
        return self.result

solver = BubblesortSolver()
solver.load_data("data/data.json")
solver.run(profile=True) # Will call _solve() with profiling
result = solver.get_result()
```

## utils.profiling

Die Profilingdaten können mit der Methode `visualize_profiler_results()` visualisiert und interaktiv im Browser angezeigt werden.
Dabei wird die `stats.dat`-Datei als Eingabe verwendet und dem visualizer `snakeviz` übergeben.
Nach ausführen der Methode wird in der Konsole ein Link angezeigt, unter dem die Profilingdaten im Browser angezeigt werden können.

```python
from problib.config import ProfileConfig
from problib.utils.profiling import visualize_profiler_results

run_id = "20231001_120000"  # Beispiel für eine Profiling-ID
conf = ProfileConfig(run_id=run_id)

visualize_profiler_results(conf)
```

Alternativ bietet die BaseSolver-Klasse die Methode `visualize_profile()` an, um die Profilingdaten zu visualisieren.

```python
from .solver import SomeSolverImplementation

solver = SomeSolverImplementation()
solver.run(profile=True)  # Profiling aktivieren
solver.visualize_profile()  # Profilingdaten visualisieren
```

## config

Das `config`-Modul enthält die Basisklasse [`ProfileConfig`](#problib.config.ProfileConfig), die als Grundlage für das Konfigurieren von Profiling-Optionen dient.

## Math

Das `math.mean`-Modul enthält mehrere mathematische Hilfsfunktionen zur Berechnung von durchschnittlichen Werten:

- arithmetic_mean(): Berechnet den arithmetischen Mittelwert einer Liste von Zahlen.
- geometric_mean(): Berechnet den geometrischen Mittelwert einer Liste von Zahlen.

## io.file

Das `io.file`-Modul enthält mehrere Hilfsfunktionen, zum laden und speichern von Daten:

- `read_json(file_path: str) -> dict`: Liest eine JSON-Datei und gibt den Inhalt als Dictionary zurück.
- `read_jsonl(file_path: str, model_type) -> list`: Generator zum zeilenweisen Lesen einer JSONL-Datei.
- `write_json(file_path: str, data: dict | list) -> None`: Schreibt ein Dictionary oder eine Liste in eine JSON-Datei.
- `write_jsonl(file_path: str, data: Iterator[BaseModel | dict]) -> None`: Schreibt in jede Zeile einer JSONL-Datei ein Dictionary oder Pydantic `BaseModel`.
- `read_yaml(file_path: str) -> dict`: Liest eine YAML-Datei und gibt den Inhalt als Dictionary zurück.
- `write_yaml(file_path: str, data: dict | list) -> None`: Schreibt ein Dictionary oder eine Liste in eine YAML-Datei.
