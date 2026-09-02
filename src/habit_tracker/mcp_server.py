from typing import List, Optional
from datetime import datetime
from fastmcp import FastMCP
from sqlalchemy.orm import Session
from database import SessionLocal, Habit, HabitLog

# Inicjalizacja serwera MCP
mcp = FastMCP("Habit Tracker")

@mcp.tool()
def create_habit(name: str, frequency: str, goal: str) -> str:
    """
    Definiuje nowy nawyk w bazie danych.
    :param name: Nazwa nawyku (np. 'Skłony').
    :param frequency: Jak często (np. 'codziennie').
    :param goal: Cel (np. '20 powtórzeń').
    """
    session: Session = SessionLocal()
    try:
        new_habit = Habit(name=name, frequency=frequency, goal=goal)
        session.add(new_habit)
        session.commit()
        return f"Sukces: Utworzono nawyk '{name}' z ID: {new_habit.id}"
    except Exception as e:
        session.rollback()
        return f"Błąd podczas tworzenia nawyku: {str(e)}"
    finally:
        session.close()

@mcp.tool()
def get_habits() -> List[dict]:
    """Pobiera listę wszystkich zdefiniowanych nawyków."""
    session: Session = SessionLocal()
    habits = session.query(Habit).all()
    result = [{"id": h.id, "name": h.name, "frequency": h.frequency, "goal": h.goal} for h in habits]
    session.close()
    return result

@mcp.tool()
def log_habit(habit_id: int, completed: bool, date_str: Optional[str] = None) -> str:
    """
    Rejestruje wykonanie nawyku.
    :param habit_id: ID nawyku.
    :param completed: Czy wykonano (True/False).
    :param date_str: Data w formacie YYYY-MM-DD (opcjonalnie).
    """
    session: Session = SessionLocal()
    try:
        log_date = datetime.strptime(date_str, "%Y-%m-%d") if date_str else datetime.now()
        new_log = HabitLog(habit_id=habit_id, completed=completed, date=log_date)
        session.add(new_log)
        session.commit()
        return f"Zalogowano status dla nawyku ID {habit_id} na dzień {log_date.date()}"
    except Exception as e:
        session.rollback()
        return f"Błąd logowania: {str(e)}"
    finally:
        session.close()
@mcp.tool()
def get_habit_log(habit_id: int, start_time: str, end_time: str) -> dict:
    """
    Pobiera historię wykonania nawyku i statystyki w podanym zakresie dat.
    :param habit_id: ID nawyku z bazy danych.
    :param start_time: Data początkowa (format YYYY-MM-DD).
    :param end_time: Data końcowa (format YYYY-MM-DD).
    """
    session: Session = SessionLocal()
    try:
        # Konwersja tekstowych dat na obiekty datetime
        start_dt = datetime.strptime(start_time, "%Y-%m-%d")
        # Ustawiamy koniec dnia na 23:59:59, żeby objąć cały dzień końcowy
        end_dt = datetime.strptime(end_time, "%Y-%m-%d").replace(hour=23, minute=59, second=59)

        # Pobranie logów z bazy za pomocą SQLAlchemy
        logs = session.query(HabitLog).filter(
            HabitLog.habit_id == habit_id,
            HabitLog.date >= start_dt,
            HabitLog.date <= end_dt
        ).order_by(HabitLog.date.asc()).all()

        # Obliczanie prostych statystyk dla Agenta LLM
        total_entries = len(logs)
        completed_count = sum(1 for log in logs if log.completed)
        success_rate = (completed_count / total_entries * 100) if total_entries > 0 else 0

        # Przygotowanie czytelnej listy historii
        history = [
            {"date": log.date.strftime("%Y-%m-%d %H:%M"), "completed": log.completed}
            for log in logs
        ]

        return {
            "habit_id": habit_id,
            "period": f"{start_time} - {end_time}",
            "stats": {
                "total_logs": total_entries,
                "completed": completed_count,
                "success_rate_percent": round(success_rate, 2)
            },
            "history": history
        }
    except Exception as e:
        return {"error": f"Nie udało się pobrać logów: {str(e)}"}
    finally:
        session.close()