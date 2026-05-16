from .accounts import router as accounts_router
from .categories import router as categories_router
from .transactions import router as transactions_router
from .dashboard import router as dashboard_router
from .auth import router as auth_router

__all__ = ["accounts_router", "categories_router", "transactions_router", "dashboard_router", "auth_router"]