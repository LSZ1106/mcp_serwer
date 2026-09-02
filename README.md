# Habit Tracker (MCP)

Prosta aplikacja do śledzenia nawyków (habit tracking), zbudowana wokół protokołu **MCP (Model Context Protocol)**. Serwer MCP udostępnia narzędzia do zarządzania nawykami i ich historią, które mogą być wywoływane przez agentów LLM lub przez dołączonego klienta REST opartego o FastAPI.

## Funkcjonalności

- Definiowanie nawyków (nazwa, częstotliwość, cel) - `create_habit`
- Pobieranie listy zdefiniowanych nawyków - `get_habits`
- Rejestrowanie wykonania nawyku w danym dniu - `log_habit`
- Pobieranie historii i statystyk (współczynnik sukcesu) dla nawyku w zadanym okresie - `get_habit_log`
- Prosty klient REST (FastAPI), który komunikuje się z serwerem MCP przez SSE i udostępnia endpointy HTTP (`/list-habits`, `/add-habit`)

## Struktura projektu

```
projektpython/
├── src/
│   └── habit_tracker/
│       ├── __init__.py
│       ├── database.py     # modele SQLAlchemy (Habit, HabitLog) i inicjalizacja bazy SQLite
│       ├── main.py         # skrypt inicjalizujący bazę danych
│       ├── mcp_server.py   # serwer MCP (FastMCP) z narzędziami do zarządzania nawykami
│       └── web_client.py   # klient FastAPI łączący się z serwerem MCP przez SSE
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Wymagania

- Python 3.11+ (projekt tworzony i testowany na Pythonie 3.13)
- pip

## Instalacja

```powershell
git clone <adres-repozytorium>
cd projektpython

python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt
```

Skopiuj plik z przykładową konfiguracją i uzupełnij własnymi wartościami:

```powershell
copy .env.example .env
```

W pliku `.env` ustaw:
- `MCP_SERVER_URL` - adres serwera MCP (domyślnie `http://localhost:6277/sse`)
- `MCP_BEARER_TOKEN` - token autoryzacyjny wygenerowany przy starcie serwera MCP (patrz niżej)

## Inicjalizacja bazy danych

Baza SQLite (`habits.db`) tworzona jest automatycznie w folderze `src/habit_tracker/`:

```powershell
cd src\habit_tracker
python main.py
```

## Uruchomienie serwera MCP

Serwer MCP (`mcp_server.py`) uruchamiamy z poziomu folderu `src/habit_tracker` za pomocą narzędzia `mcp dev`, które startuje MCP Inspector (domyślnie na porcie `6277`) i wypisuje w konsoli token autoryzacyjny:

```powershell
cd src\habit_tracker
mcp dev mcp_server.py
```

Skopiuj wypisany token do zmiennej `MCP_BEARER_TOKEN` w pliku `.env`.

## Uruchomienie klienta REST

Klient FastAPI (`web_client.py`) łączy się z serwerem MCP i wystawia proste endpointy HTTP:

```powershell
cd src\habit_tracker
python web_client.py
```

Aplikacja wystartuje pod adresem `http://127.0.0.1:8080`, dokumentacja API dostępna pod `/docs`:

- `GET /` - sprawdzenie statusu klienta
- `GET /list-habits` - pobiera listę nawyków za pośrednictwem serwera MCP
- `POST /add-habit?name=...&frequency=...&goal=...` - dodaje nowy nawyk za pośrednictwem serwera MCP

## Technologie

- [FastMCP](https://github.com/jlowin/fastmcp) / [MCP SDK](https://modelcontextprotocol.io/) - serwer i klient MCP
- [FastAPI](https://fastapi.tiangolo.com/) + [Uvicorn](https://www.uvicorn.org/) - warstwa REST
- [SQLAlchemy](https://www.sqlalchemy.org/) + SQLite - przechowywanie danych
- [python-dotenv](https://pypi.org/project/python-dotenv/) - konfiguracja przez zmienne środowiskowe
