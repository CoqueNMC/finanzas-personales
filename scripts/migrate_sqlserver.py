"""
Migra los datos historicos desde SQL Server al nuevo esquema.
Ejecutar: python scripts/migrate_sqlserver.py --source "mssql+pyodbc://..." 

Mapeo de operaciones (esquema antiguo -> nuevo):
  OperacionID=1 (Ingreso)        -> type=income,      cuenta=Efectivo
  OperacionID=2 (Egreso efe.)    -> type=expense,      cuenta=Efectivo
  OperacionID=3 (Gasto TC)       -> type=expense_tc,   cuenta=TC
  OperacionID=4 (Pago TC)        -> type=transfer,     de=Efectivo, a=TC
  OperacionID=5 (Invertir)       -> type=invest,       de=Efectivo, a=Inversion
  OperacionID=6 (Retiro inv.)    -> type=withdraw,     de=Inversion, a=Efectivo
"""
import sys, os, argparse
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy import create_engine, text
from backend.db.connection import SessionLocal
from backend.models import Transaction
from backend.services.id_service import generate_id

# Mapeo de categorias por palabras clave (DRY: mismo que el frontend)
CAT_RULES = [
    (["NOMINA","CESANTIA","BONO","PRIMA","VENTA PC","INTERES INV"], "cat_10"),
    (["ALMUERZO","COMIDA","MECATO","MERCADO","RAPPI","RESTAURANTE"], "cat_1"),
    (["GASOLINA","DIDI","UBER","TAXI","BUS","PARQUEADERO","MOTILADA","MOTO ("], "cat_2"),
    (["VIAJE"], "cat_2"),
    (["REGALO"], "cat_3"),
    (["YOUTUBE","NETFLIX","SPOTIFY","WOM","CLARO","TIGO"], "cat_4"),
    (["SERVICIOS","ADMIN APTO","AGUA","LUZ","GAS","ARRIENDO"], "cat_5"),
    (["ROPA","ZAPATOS"], "cat_6"),
    (["SEGURO SALUD","SEGURO PENSION","MEDICO","CLINICA","FARMACIA"], "cat_7"),
    (["DISFRUTE","CINE","MOTEL","PISCINA","VIDEO JUEGO","TONTERIA"], "cat_8"),
    (["INVERSION","INVERTIR"], "cat_9"),
    (["IMPUESTO","CUOTA MANEJO","INTERESE","COMISION","AVANCE"], "cat_11"),
    (["GIMNASIO","PROTEINA","CREATINA"], "cat_12"),
    (["MASCOTA","VETERINARIO"], "cat_13"),
    (["PRESTAMO"], "cat_14"),
]

def auto_category(desc: str) -> str:
    d = (desc or "").upper()
    for keywords, cat_id in CAT_RULES:
        if any(k in d for k in keywords):
            return cat_id
    return "cat_15"

OP_MAP = {
    1: ("income",     "acc_cash", None),
    2: ("expense",    "acc_cash", None),
    3: ("expense_tc", "acc_tc",   None),
    4: ("transfer",   "acc_cash", "acc_tc"),
    5: ("invest",     "acc_cash", "acc_invest"),
    6: ("withdraw",   "acc_invest","acc_cash"),
}

def migrate(source_url: str, cash_id: str, tc_id: str, invest_id: str):
    acc_map = {"acc_cash": cash_id, "acc_tc": tc_id, "acc_invest": invest_id}
    src_engine = create_engine(source_url)

    print("Conectando a SQL Server origen...")
    with src_engine.connect() as conn:
        rows = conn.execute(text(
            "SELECT Descripcion, Valor, OperacionID, destinoID, Fecha FROM Finanzas"
        )).fetchall()
    print(f"{len(rows)} registros encontrados.")

    db = SessionLocal()
    try:
        batch = []
        for row in rows:
            desc, valor, op_id, dest_id, fecha = row
            type_str, from_key, to_key = OP_MAP.get(op_id, ("expense","acc_cash",None))
            batch.append(Transaction(
                id=generate_id("tx"),
                description=str(desc),
                amount=float(valor),
                date=fecha,
                type=type_str,
                account_id=acc_map.get(from_key),
                to_account_id=acc_map.get(to_key) if to_key else None,
                category_id=auto_category(str(desc)),
            ))
            if len(batch) >= 500:
                db.bulk_save_objects(batch)
                db.commit()
                print(f"  {len(batch)} registros guardados...")
                batch = []
        if batch:
            db.bulk_save_objects(batch)
            db.commit()
        print(f"Migracion completada: {len(rows)} transacciones.")
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Migrar datos de SQL Server")
    parser.add_argument("--source", required=True, help="DATABASE_URL de SQL Server origen")
    parser.add_argument("--cash-id",   default="acc_1", help="ID de cuenta Efectivo destino")
    parser.add_argument("--tc-id",     default="acc_2", help="ID de cuenta TC destino")
    parser.add_argument("--invest-id", default="acc_3", help="ID de cuenta Inversion destino")
    args = parser.parse_args()
    migrate(args.source, args.cash_id, args.tc_id, args.invest_id)
