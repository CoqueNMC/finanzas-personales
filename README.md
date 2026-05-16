# Finanzas Personales

App web de gestión financiera personal. Backend Python/FastAPI + Frontend modular vanilla JS.

## Estructura del proyecto

```
finanzas/
│
├── backend/                          # Servidor Python / FastAPI
│   ├── main.py                       # Entry point: registra routers, CORS, health
│   ├── core/
│   │   └── config.py                 # Variables de entorno (singleton vía lru_cache)
│   ├── db/
│   │   ├── connection.py             # ★ ÚNICO archivo a editar para cambiar de BD
│   │   └── repositories/
│   │       ├── base_repository.py    # CRUD genérico (DRY): get, create, delete, exists
│   │       ├── account_repository.py # Saldo calculado desde transacciones
│   │       ├── category_repository.py
│   │       └── transaction_repository.py  # Filtros dinámicos + bulk_insert
│   ├── models/                       # SQLAlchemy ORM (tablas)
│   │   ├── account.py
│   │   ├── category.py
│   │   └── transaction.py
│   ├── schemas/                      # Pydantic: validación entrada/salida
│   │   ├── account.py
│   │   ├── category.py
│   │   └── transaction.py
│   ├── services/                     # Lógica de negocio (sin SQL, sin HTTP)
│   │   ├── account_service.py
│   │   ├── category_service.py
│   │   ├── transaction_service.py
│   │   └── id_service.py             # Generación de IDs (centralizado)
│   └── api/
│       └── routes/                   # Un archivo por recurso
│           ├── accounts.py
│           ├── categories.py
│           ├── transactions.py
│           └── dashboard.py
│
├── frontend/
│   ├── index.html                    # Entry point único del SPA
│   └── src/
│       ├── app.js                    # Orquestador: navegación + inicialización
│       ├── services/
│       │   └── api.js                # ★ Todas las llamadas HTTP aquí (un solo lugar)
│       ├── pages/                    # Una clase por pantalla
│       │   ├── dashboard.js
│       │   ├── accounts.js
│       │   ├── transactions.js
│       │   ├── charts.js
│       │   └── categories.js
│       ├── components/               # Reutilizables: no tienen estado de negocio
│       │   ├── sidebar.js
│       │   ├── modal.js
│       │   ├── toast.js
│       │   └── colorPicker.js
│       ├── utils/                    # Helpers puros (sin side effects)
│       │   ├── formatters.js         # fmt(), fmtDate(), currentYearMonth()
│       │   ├── badges.js             # txBadge(), txAmount()
│       │   └── dom.js                # $(), $$(), el(), setHtml()
│       └── styles/                   # CSS modular
│           ├── variables.css         # Tokens de diseño (colores, radios, fuentes)
│           ├── base.css              # Reset + tipografía global
│           ├── components.css        # Buttons, cards, badges, table, forms
│           ├── sidebar.css
│           ├── modal.css
│           └── toast.css
│
├── scripts/
│   ├── init_db.py                    # Crea tablas en la BD configurada
│   ├── seed_categories.py            # Inserta las 15 categorías por defecto
│   └── migrate_sqlserver.py          # Migra datos históricos desde SQL Server
│
├── .env.example                      # Plantilla de variables de entorno
├── .gitignore
├── requirements.txt
└── README.md
```

## Cambiar de base de datos

Edita **solo** `backend/db/connection.py` y la variable `DATABASE_URL` en `.env`:

| Motor           | DATABASE_URL                                                                 |
|-----------------|------------------------------------------------------------------------------|
| SQL Server      | `mssql+pyodbc://user:pass@host/db?driver=ODBC+Driver+17+for+SQL+Server`     |
| PostgreSQL      | `postgresql+asyncpg://user:pass@host:5432/db`                                |
| Supabase        | `postgresql+asyncpg://user:pass@db.xxx.supabase.co:5432/postgres`            |
| SQLite (dev)    | `sqlite+aiosqlite:///./finanzas.db`                                          |
| MySQL           | `mysql+aiomysql://user:pass@host:3306/finanzas`                              |

## Inicio rápido

```bash
# 1. Configurar entorno
cp .env.example .env
# Editar .env con tus credenciales

# 2. Instalar dependencias Python
pip install -r requirements.txt

# 3. Crear tablas
python scripts/init_db.py

# 4. Poblar categorías por defecto
python scripts/seed_categories.py

# 5. (Opcional) Migrar datos históricos de SQL Server
python scripts/migrate_sqlserver.py \
  --source "mssql+pyodbc://sa:pass@localhost/Finanzas?driver=ODBC+Driver+17+for+SQL+Server" \
  --cash-id acc_1 --tc-id acc_2 --invest-id acc_3

# 6. Iniciar backend
uvicorn backend.main:app --reload --port 8000

# 7. Abrir frontend
# Opción A: directamente en el navegador (si usas Live Server en VSCode)
# Opción B: servidor simple
python -m http.server 3000 --directory frontend
# Abrir http://localhost:3000
```

## Principios aplicados

| Principio | Implementación |
|-----------|---------------|
| **DRY** | `BaseRepository` centraliza CRUD; `formatters.js` y `badges.js` compartidos en todo el frontend; `id_service.py` único generador de IDs; `api.js` única capa HTTP |
| **Single Responsibility** | Cada clase/archivo tiene una sola razón para cambiar |
| **Repository Pattern** | Las rutas no tocan SQL; todo pasa por repositorios |
| **Dependency Injection** | FastAPI inyecta `Session` via `Depends(get_db)` |
| **Environment-based config** | Sin credenciales en código; todo en `.env` |
| **Schema validation** | Pydantic valida 100% de entrada y salida |
| **Escalabilidad** | Agregar un recurso = nuevo model + schema + repository + service + router |
