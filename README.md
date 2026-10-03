# Wyniki spraw o nadużycie uprawnień — MVP

Mały, powtarzalny projekt analizy danych o **wynikach spraw**, a nie narzędzie do ustalania winy. Pokazuje, jak opisać odsetek skazań i uniewinnień, uwzględnić niepewność oraz nie mylić wyniku postępowania z rzeczywistym wystąpieniem nadużycia.

## Pytanie analityczne

Jaki jest rozkład końcowych rozstrzygnięć spraw w badanym zbiorze i jak bardzo niepewny jest oszacowany odsetek skazań? Sama przewaga uniewinnień nie dowodzi ani nadużyć, ani ich braku. Na wynik wpływają m.in. selekcja spraw, materiał dowodowy, kwalifikacja prawna, standard dowodu i sposób kodowania rozstrzygnięć.

## Szybki start

Wymagany Python 3.10+.

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
misconduct-mvp --input data/demo_cases.csv --output reports
```

Jeśli PowerShell blokuje aktywację środowiska, pomiń aktywację i uruchom polecenia przez `.\.venv\Scripts\python.exe` oraz `.\.venv\Scripts\misconduct-mvp.exe`.

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
misconduct-mvp --input data/demo_cases.csv --output reports
```

Polecenie tworzy `reports/summary.json` i `reports/outcomes.png`. Dane demonstracyjne są syntetyczne i nie opisują rzeczywistych osób ani spraw. Nie wolno przedstawiać ich jako wyników badań empirycznych.

## Docker

Wymagany jest uruchomiony Docker Desktop (Windows/macOS) lub Docker Engine (Linux). Wszystkie polecenia budowania wykonuj z głównego katalogu projektu — tego, w którym znajduje się `Dockerfile`. Obraz uruchamia analizę demonstracyjną domyślnie.

### Windows PowerShell

Uruchom polecenia po kolei w tym samym oknie PowerShell. Pierwsze sprawdzenie powinno zwrócić `True`:

```powershell
Test-Path .\Dockerfile
docker build --tag police-misconduct-outcomes-mvp:local .
New-Item -ItemType Directory -Force .\reports | Out-Null
$reportsPath = (Resolve-Path .\reports).Path
docker run --rm --user 10001:10001 --mount "type=bind,source=$reportsPath,target=/reports" police-misconduct-outcomes-mvp:local
```

Nie zamykaj okna ani nie pomijaj ustawienia `$reportsPath` przed `docker run`. Jeśli zmienna jest pusta, Docker zgłosi `invalid spec` dla ścieżki `:/reports`.

Aby uruchomić analizę na własnym CSV, skopiuj go do folderu `data` i podaj jego nazwę (plik musi istnieć):

```powershell
$dataPath = (Resolve-Path .\data).Path
docker run --rm --user 10001:10001 --mount "type=bind,source=$dataPath,target=/input,readonly" --mount "type=bind,source=$reportsPath,target=/reports" police-misconduct-outcomes-mvp:local --input /input/moje-sprawy.csv --output /reports
```

Zamień `moje-sprawy.csv` na nazwę pliku umieszczonego w `data`.

### macOS / Linux

```bash
docker build --tag police-misconduct-outcomes-mvp:local .
mkdir -p reports
docker run --rm --user "$(id -u):$(id -g)" --volume "$(pwd)/reports:/reports" police-misconduct-outcomes-mvp:local
```

### Wyświetlanie wyników

Raporty są zapisywane na komputerze w `reports`, a nie wyświetlane w oknie Dockera. W PowerShellu:

```powershell
Get-Content .\reports\summary.json
Invoke-Item .\reports\outcomes.png
```

JSON zawiera liczby, udziały i przedział Wilsona; wykres PNG pokazuje liczebności rozstrzygnięć. Żeby wyświetlić tabelę liczebności i udziałów w PowerShellu:

```powershell
$summary = Get-Content .\reports\summary.json -Raw | ConvertFrom-Json
$summary.outcomes.PSObject.Properties | Select-Object @{Name='Wynik';Expression={$_.Name}}, @{Name='Liczba';Expression={$_.Value.count}}, @{Name='Udział (%)';Expression={[math]::Round($_.Value.share * 100, 1)}} | Format-Table -AutoSize
```

Na macOS/Linux użyj `cat reports/summary.json`; wykres otwórz poleceniem `open reports/outcomes.png` (macOS) lub `xdg-open reports/outcomes.png` (Linux).

### Typowe błędy

- **`failed to read dockerfile` / brak `Dockerfile`** — przejdź do katalogu `police_misconduct_mvp`, nie do innego projektu. `Test-Path .\Dockerfile` powinno zwrócić `True`.
- **`invalid spec: :/reports`** — `$reportsPath` nie został ustawiony w bieżącym oknie PowerShell. Wykonaj ponownie `New-Item ...` i `$reportsPath = (Resolve-Path .\reports).Path`, a następnie uruchom kontener.
- **Docker nie może połączyć się z daemonem** — uruchom Docker Desktop i poczekaj, aż będzie gotowy.
- **Nie znaleziono CSV** — sprawdź, czy plik znajduje się w `data`, a jego nazwa w `--input /input/...` jest taka sama.

## Jenkins

`Jenkinsfile` buduje obraz Docker, uruchamia analizę demonstracyjną, a następnie archiwizuje `reports/summary.json` i `reports/outcomes.png`. Agent Jenkins musi mieć dostęp do polecenia `docker` oraz działać na systemie obsługującym krok `sh`.

## Własne dane

Podaj plik CSV przez `--input`. Minimalny schemat:

| Kolumna | Znaczenie |
| --- | --- |
| `case_id` | Pseudonimizowany, unikalny identyfikator sprawy |
| `outcome` | Jedna z wartości: `conviction`, `acquittal`, `other`, `unknown` |
| `year` | Rok końcowego rozstrzygnięcia (opcjonalny) |

Wiersz odpowiada jednej sprawie. Przed analizą należy określić populację, okres, jurysdykcję, źródło i reguły kodowania. Sprawa może obejmować wielu funkcjonariuszy; wynik nie jest miarą częstości nadużyć wśród funkcjonariuszy. Nie umieszczaj danych osobowych ani identyfikatorów pozwalających na identyfikację.

## Metody i ograniczenia

- Udziały są liczone względem wszystkich spraw; `unknown` i `other` pozostają widoczne w mianowniku.
- Przedział Wilsona 95% podano dla odsetka skazań. Jest to niepewność próbkowania przy założeniu niezależnych obserwacji, a nie korekta błędów selekcji, zależności spraw ani błędów klasyfikacji.
- Brak modelu przewidującego winę lub wynik przyszłej sprawy. Wynik procesu nie jest etykietą prawdy o zachowaniu.
- Analiza opisowa nie identyfikuje przyczyn i nie uzasadnia porównań bez sprawdzenia porównywalności populacji.

## Struktura

```text
src/misconduct_mvp/  walidacja, statystyki, wykres i CLI
data/demo_cases.csv  mały, jawnie syntetyczny przykład
reports/             generowane wyniki (nie są wersjonowane)
```

## Następny krok po MVP

Zastąpić przykład legalnie pozyskanym, udokumentowanym zbiorem; opublikować kryteria włączenia spraw, słownik kodowania i analizę braków. Przed porównaniami grup sprawdzić nakładanie się okresów i jurysdykcji oraz strukturę zależności. Wyniki poddać przeglądowi prawnemu i metodologicznemu.
