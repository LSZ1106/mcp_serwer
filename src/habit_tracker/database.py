import os

from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

# 1. Konfiguracja połączenia (SQLite stworzy plik habits.db w tym samym folderze co ten moduł)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SQLALCHEMY_DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'habits.db')}"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = sqlalchemy.orm.declarative_base()

# 2. Model Nawyków (Tabela z nawykami)
class Habit(Base):
    __tablename__ = "habits"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    frequency = Column(String)  # np. "codziennie"
    goal = Column(String)       # np. "10 pompek"
    
    # Relacja do logów (jeden nawyk ma wiele wpisów)
    logs = relationship("HabitLog", back_populates="habit", cascade="all, delete-orphan")

# 3. Model Logów (Tabela z wykonaniem)
class HabitLog(Base):
    __tablename__ = "habit_logs"
    id = Column(Integer, primary_key=True, index=True)
    habit_id = Column(Integer, ForeignKey("habits.id"), nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    completed = Column(Boolean, default=False)
    
    habit = relationship("Habit", back_populates="logs")

# 4. Funkcja tworząca tabele
def init_db():
    Base.metadata.create_all(bind=engine)
    print("Baza danych i tabele zostały zainicjalizowane!")