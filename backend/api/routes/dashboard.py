from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional
from backend.db.connection import get_db
from backend.services import TransactionService, AccountService
from backend.db.repositories import TransactionRepository
from backend.core.dependencies import get_current_user
from backend.models import User

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/summary/")
def get_summary(
    month: str = Query(default=date.today().strftime("%Y-%m"), pattern=r"^\d{4}-\d{2}$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return {
        "month": month,
        "transactions_summary": TransactionService(db, current_user).get_dashboard_summary(month),
        "accounts": AccountService(db, current_user).get_all(),
        "expenses_by_category": TransactionService(db, current_user).get_expense_by_category(month),
    }

@router.get("/charts/monthly/")
def get_monthly_chart(
    months: int = Query(6, ge=1, le=24),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = TransactionRepository(db, current_user)
    from dateutil.relativedelta import relativedelta
    today = date.today()
    result = []
    for i in range(months - 1, -1, -1):
        d = today - relativedelta(months=i)
        ym = d.strftime("%Y-%m")
        s = repo.get_summary_by_month(ym)
        result.append({
            "month": ym,
            "income": s.get("income", {}).get("total", 0),
            "expense": s.get("expense", {}).get("total", 0) + s.get("expense_tc", {}).get("total", 0),
        })
    return result

@router.get("/expenses-by-category/")
def get_expenses_by_category(
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = TransactionRepository(db, current_user)
    return repo.get_expense_by_category_range(date_from, date_to)