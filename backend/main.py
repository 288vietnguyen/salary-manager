from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import os
import math

from database import init_db, get_users, create_user, update_user, upsert_income, get_income_history, get_income_for_stats

app = FastAPI(title="Salary Manager")

# Serve frontend static files
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")


@app.on_event("startup")
def startup():
    init_db()


# ── Static files & root ───────────────────────────────────────────────────────

app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/")
def root():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))


# ── Schemas ───────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    name: str
    title: str
    base_salary: float


class UserUpdate(BaseModel):
    name: str
    title: str
    base_salary: float


class IncomeInput(BaseModel):
    user_id: int
    year: int
    month: int
    income: float
    note: Optional[str] = ""


# ── API Endpoints ─────────────────────────────────────────────────────────────

@app.get("/api/users")
def api_get_users():
    return get_users()


@app.post("/api/users", status_code=201)
def api_create_user(body: UserCreate):
    uid = create_user(body.name, body.title, body.base_salary)
    return {"id": uid, "name": body.name, "title": body.title, "base_salary": body.base_salary}


@app.put("/api/users/{user_id}")
def api_update_user(user_id: int, body: UserUpdate):
    update_user(user_id, body.name, body.title, body.base_salary)
    return {"ok": True}


@app.get("/api/income/{user_id}")
def api_get_income(user_id: int):
    return get_income_history(user_id)


@app.post("/api/income")
def api_add_income(body: IncomeInput):
    upsert_income(body.user_id, body.year, body.month, body.income, body.note or "")
    return {"ok": True}


@app.get("/api/stats/{user_id}")
def api_get_stats(user_id: int):
    rows = get_income_for_stats(user_id)
    if not rows:
        return {"monthly": [], "rolling3": [], "annual": [], "base_salary": 0}

    # Get base salary
    conn = __import__('database').get_conn()
    user_row = conn.execute("SELECT base_salary FROM users WHERE id=?", (user_id,)).fetchone()
    conn.close()
    base_salary = user_row["base_salary"] if user_row else 0

    # ── Monthly % diff vs base salary ─────────────────────────────────────────
    monthly = []
    for row in rows:
        curr = row["income"]
        diff_pct = round((curr - base_salary) / base_salary * 100, 2) if base_salary != 0 else None
        monthly.append({
            "year": row["year"],
            "month": row["month"],
            "income": curr,
            "base_salary": base_salary,
            "diff_pct": diff_pct,
        })

    # ── Fixed quarterly (Q1=Jan-Mar, Q2=Apr-Jun, Q3=Jul-Sep, Q4=Oct-Dec) ──────
    QUARTERS = [
        (1, [1, 2, 3]),
        (2, [4, 5, 6]),
        (3, [7, 8, 9]),
        (4, [10, 11, 12]),
    ]
    year_month_map: dict = {}
    for row in rows:
        year_month_map.setdefault(row["year"], {})[row["month"]] = row["income"]

    base_3m = base_salary * 3
    rolling3 = []
    for year in sorted(year_month_map.keys()):
        months_data = year_month_map[year]
        for q_num, q_months in QUARTERS:
            q_incomes = [months_data[m] for m in q_months if m in months_data]
            if not q_incomes:
                continue
            income_sum = sum(q_incomes)
            diff_pct = round((income_sum - base_3m) / base_3m * 100, 2) if base_3m != 0 else None
            actual_diff = round(income_sum - base_3m, 2)
            rolling3.append({
                "year": year,
                "quarter": q_num,
                "base_3m": round(base_3m, 2),
                "income_sum": round(income_sum, 2),
                "diff_pct": diff_pct,
                "actual_diff": actual_diff,
                "months_count": len(q_incomes),
            })

    # ── Annual totals vs base salary * 12 ────────────────────────────────────
    annual_map: dict = {}
    for row in rows:
        y = row["year"]
        annual_map.setdefault(y, []).append(row["income"])

    annual_base = base_salary * 12
    annual = []
    for y in sorted(annual_map.keys()):
        total = sum(annual_map[y])
        count = len(annual_map[y])
        diff_pct = round((total - annual_base) / annual_base * 100, 2) if annual_base != 0 else None
        actual_diff = round(total - annual_base, 2)
        annual.append({
            "year": y,
            "total": round(total, 2),
            "months_recorded": count,
            "annual_base": round(annual_base, 2),
            "diff_pct": diff_pct,
            "actual_diff": actual_diff,
        })

    return {"monthly": monthly, "rolling3": rolling3, "annual": annual, "base_salary": base_salary}
