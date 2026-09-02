import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from mcp.client.session import ClientSession
from mcp.client.sse import sse_client
import uvicorn
import httpx

load_dotenv()

app = FastAPI(title="MCP Habit Tracker Client")

# Adres serwera MCP uruchomionego przez fastmcp (domyślnie port 8000)
# Używamy ścieżki /sse zgodnie z protokołem streamable-http
# MCP_SERVER_URL = "http://localhost:8000/sse"
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:6277/sse")
# Token wczytywany ze zmiennej środowiskowej / pliku .env - nigdy nie commitować sekretów!
BEARER_TOKEN = os.getenv("MCP_BEARER_TOKEN", "")

@app.get("/")
async def root():
    return {"message": "Klient MCP Habit Tracker działa. Wejdź na /docs po interfejs testowy."}

@app.get("/list-habits")
async def list_habits_via_mcp():
    """Pobiera nawyki z bazy danych ZA POŚREDNICTWEM serwera MCP."""
    try:
        headers = {
        "Authorization": f"Bearer {BEARER_TOKEN}",
        "Content-Type": "application/json"
        }

        async with sse_client(url=MCP_SERVER_URL, headers=headers, timeout=10) as (read, write): 
            async with ClientSession(read, write) as session:
                await session.initialize()
                # Wywołujemy narzędzie zdefiniowane w mcp_server.py
                result = await session.call_tool("get_habits", arguments={})
                return {"source": "MCP Server", "content": result.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd połączenia z MCP: {str(e)}")

@app.post("/add-habit")
async def add_habit_via_mcp(name: str, frequency: str, goal: str):
    """Dodaje nowy nawyk wysyłając żądanie do serwera MCP."""
    try:
        headers = {
        "Authorization": f"Bearer {BEARER_TOKEN}",
        "Content-Type": "application/json"
        }
        async with sse_client(url=MCP_SERVER_URL, headers=headers, timeout=10) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(
                    "create_habit", 
                    arguments={"name": name, "frequency": frequency, "goal": goal}
                )
                return {"status": "success", "mcp_response": result.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd: {str(e)}")

def main():
    uvicorn.run(app, host="127.0.0.1", port=8080)

if __name__ == "__main__":
    main()