from __future__ import annotations

import os
import time
from contextlib import asynccontextmanager
from decimal import Decimal
from pathlib import Path
from typing import Any

import psycopg
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from psycopg.rows import dict_row
from starlette.templating import Jinja2Templates

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "calculator")
DB_USER = os.getenv("DB_USER", "calculator")
DB_PASSWORD = os.getenv("DB_PASSWORD", "calculator123")
DB_CONNECT_TIMEOUT = int(os.getenv("DB_CONNECT_TIMEOUT", "5"))
DB_MAX_RETRIES = int(os.getenv("DB_MAX_RETRIES", "20"))
DB_RETRY_DELAY_SECONDS = float(os.getenv("DB_RETRY_DELAY_SECONDS", "2"))


templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


class CalculationRequest(BaseModel):
    left: float = Field(..., description="Left operand")
    operator: str = Field(..., description="Arithmetic operator")
    right: float = Field(..., description="Right operand")


class CalculationResponse(BaseModel):
    left: float
    operator: str
    right: float
    result: float


class HistoryItem(BaseModel):
    id: int
    left_value: float
    operator: str
    right_value: float
    result_value: float
    created_at: str


app = FastAPI(title="Calculator App")
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


def get_connection() -> psycopg.Connection[Any]:
    return psycopg.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        connect_timeout=DB_CONNECT_TIMEOUT,
        row_factory=dict_row,
    )


def initialize_database() -> None:
    last_error: Exception | None = None
    for attempt in range(1, DB_MAX_RETRIES + 1):
        try:
            with get_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        CREATE TABLE IF NOT EXISTS calculations (
                            id SERIAL PRIMARY KEY,
                            left_value DOUBLE PRECISION NOT NULL,
                            operator TEXT NOT NULL,
                            right_value DOUBLE PRECISION NOT NULL,
                            result_value DOUBLE PRECISION NOT NULL,
                            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                        )
                        """
                    )
                connection.commit()
            return
        except Exception as exc:  # pragma: no cover - startup retry
            last_error = exc
            if attempt < DB_MAX_RETRIES:
                time.sleep(DB_RETRY_DELAY_SECONDS)

    raise RuntimeError("Unable to initialize the database") from last_error


def calculate(left: float, operator: str, right: float) -> float:
    if operator == "+":
        return left + right
    if operator == "-":
        return left - right
    if operator == "*":
        return left * right
    if operator == "/":
        if right == 0:
            raise ValueError("Division by zero is not allowed")
        return left / right
    raise ValueError(f"Unsupported operator: {operator}")


@app.on_event("startup")
def on_startup() -> None:
    initialize_database()


@app.get("/", response_class=HTMLResponse)
def home(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/calculate", response_model=CalculationResponse)
def create_calculation(payload: CalculationRequest) -> CalculationResponse:
    try:
        result = calculate(payload.left, payload.operator, payload.right)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO calculations (left_value, operator, right_value, result_value)
                VALUES (%s, %s, %s, %s)
                RETURNING id
                """,
                (payload.left, payload.operator, payload.right, result),
            )
        connection.commit()

    return CalculationResponse(
        left=payload.left,
        operator=payload.operator,
        right=payload.right,
        result=result,
    )


@app.get("/api/history", response_model=list[HistoryItem])
def get_history(limit: int = 20) -> list[HistoryItem]:
    safe_limit = max(1, min(limit, 100))

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, left_value, operator, right_value, result_value, created_at
                FROM calculations
                ORDER BY created_at DESC, id DESC
                LIMIT %s
                """,
                (safe_limit,),
            )
            rows = cursor.fetchall()

    history: list[HistoryItem] = []
    for row in rows:
        created_at = row["created_at"]
        history.append(
            HistoryItem(
                id=row["id"],
                left_value=float(row["left_value"]),
                operator=row["operator"],
                right_value=float(row["right_value"]),
                result_value=float(row["result_value"]),
                created_at=created_at.isoformat() if hasattr(created_at, "isoformat") else str(created_at),
            )
        )
    return history


@app.get("/healthz")
def healthcheck() -> JSONResponse:
    return JSONResponse({"status": "ok"})
