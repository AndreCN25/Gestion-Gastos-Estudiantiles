from collections import defaultdict
from datetime import date
from decimal import Decimal
import logging
from pathlib import Path
from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import func
from sqlalchemy.orm import Session
from .config import settings
from .database import Base, SessionLocal, engine, get_db
from .models import Expense, User
from .schemas import ExpenseIn, ExpenseOut, LoginIn, RegisterIn
from .security import create_token, get_current_user, hash_password, require_admin, verify_password
from .services import fetch_exchange, fetch_weather, spending_tips

logger = logging.getLogger(__name__)

if len(settings.secret_key) < 32 or settings.secret_key == "replace-with-a-long-random-secret":
    raise RuntimeError("Configura SECRET_KEY con al menos 32 caracteres aleatorios antes de iniciar la aplicación.")
Base.metadata.create_all(bind=engine)
if settings.admin_email and settings.admin_password:
    with SessionLocal() as seed_db:
        if not seed_db.query(User).filter(func.lower(User.email) == settings.admin_email.lower()).first():
            seed_db.add(User(email=settings.admin_email.lower(), password_hash=hash_password(settings.admin_password), role="admin"))
            seed_db.commit()

app = FastAPI(title="CuentaClara API", version="1.0.0")
origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=False, allow_methods=["GET", "POST", "DELETE"], allow_headers=["Authorization", "Content-Type"])


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/auth/register", status_code=201)
def register(data: RegisterIn, db: Session = Depends(get_db)):
    email = str(data.email).lower()
    if db.query(User).filter(func.lower(User.email) == email).first():
        raise HTTPException(409, "Ese correo ya está registrado")
    user = User(email=email, password_hash=hash_password(data.password), role="student")
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"access_token": create_token(user), "token_type": "bearer", "user": {"id": user.id, "email": user.email, "role": user.role}}


@app.post("/api/auth/login")
def login(data: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(func.lower(User.email) == str(data.email).lower()).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Correo o contraseña incorrectos")
    return {"access_token": create_token(user), "token_type": "bearer", "user": {"id": user.id, "email": user.email, "role": user.role}}


@app.get("/api/me")
def me(user: User = Depends(get_current_user)):
    return {"id": user.id, "email": user.email, "role": user.role}


@app.get("/api/expenses", response_model=list[ExpenseOut])
def list_expenses(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Expense).filter(Expense.user_id == user.id).order_by(Expense.spent_on.desc(), Expense.id.desc()).limit(500).all()


@app.post("/api/expenses", response_model=ExpenseOut, status_code=201)
def add_expense(data: ExpenseIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    values = data.model_dump(exclude={"currency"})
    expense = Expense(user_id=user.id, currency=data.currency.upper(), **values)
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


@app.delete("/api/expenses/{expense_id}", status_code=204)
def delete_expense(expense_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    expense = db.get(Expense, expense_id)
    if not expense or (expense.user_id != user.id and user.role != "admin"):
        raise HTTPException(404, "Gasto no encontrado")
    db.delete(expense)
    db.commit()


@app.get("/api/summary")
def summary(month: str = Query(default_factory=lambda: date.today().strftime("%Y-%m"), pattern=r"^\d{4}-\d{2}$"), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    try:
        year, month_number = map(int, month.split("-"))
        start = date(year, month_number, 1)
        end = date(year + (month_number == 12), month_number % 12 + 1, 1)
    except ValueError:
        raise HTTPException(422, "El mes debe ser una fecha válida con formato AAAA-MM")
    rows = db.query(Expense).filter(Expense.user_id == user.id, Expense.spent_on >= start, Expense.spent_on < end).all()
    totals = defaultdict(lambda: Decimal("0.00"))
    for row in rows:
        totals[row.currency] += row.amount
    by_category = defaultdict(lambda: Decimal("0.00"))
    for row in rows:
        by_category[f"{row.category} ({row.currency})"] += row.amount
    return {"month": month, "count": len(rows), "totals": dict(totals), "by_category": dict(by_category)}


@app.get("/api/external/weather")
async def weather(city: str | None = Query(default=None, min_length=2, max_length=80), latitude: float | None = Query(default=None, ge=-90, le=90), longitude: float | None = Query(default=None, ge=-180, le=180), user: User = Depends(get_current_user)):
    if (latitude is None) != (longitude is None) or (city is None and latitude is None):
        raise HTTPException(422, "Indica una ciudad o una ubicación completa")
    try:
        return await fetch_weather(city, latitude, longitude)
    except Exception:
        logger.exception("Falló la consulta del clima")
        raise HTTPException(502, "El servicio de clima no está disponible ahora")


@app.get("/api/external/exchange")
async def exchange(source: str = Query(default="MXN", pattern=r"^[A-Za-z]{3}$"), target: str = Query(default="USD", pattern=r"^[A-Za-z]{3}$"), user: User = Depends(get_current_user)):
    try:
        return await fetch_exchange(source.upper(), target.upper())
    except Exception:
        raise HTTPException(502, "El servicio de tipo de cambio no está disponible ahora")


@app.post("/api/ai/tips")
async def tips(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    expenses = db.query(Expense).filter(Expense.user_id == user.id).order_by(Expense.spent_on.desc()).limit(100).all()
    try:
        return await spending_tips(expenses)
    except Exception:
        raise HTTPException(502, "El asistente IA no está disponible ahora")


@app.get("/api/admin/summary")
def admin_summary(db: Session = Depends(get_db), _admin: User = Depends(require_admin)):
    return {"users": db.query(func.count(User.id)).scalar(), "expenses": db.query(func.count(Expense.id)).scalar()}


STATIC = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=STATIC), name="static")


@app.get("/", include_in_schema=False)
def home():
    return FileResponse(STATIC / "index.html")
