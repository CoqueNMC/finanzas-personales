def create_user(email: str, name: str, password: str, admin: bool = False):
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            print(f"❌ Ya existe un usuario con el email {email}")
            return
        user = User(
            id=generate_id("usr"),
            email=email,
            name=name,
            password_hash=pwd_context.hash(password),
            is_active=True,
            is_admin=admin,
        )
        db.add(user)
        db.flush()
        _seed_categories(db, user.id)
        db.commit()
        print(f"✓ Usuario creado exitosamente")
        print(f"  ID:    {user.id}")
        print(f"  Email: {user.email}")
        print(f"  Nombre: {user.name}")
        print(f"  Admin: {user.is_admin}")
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
    finally:
        db.close()


def _seed_categories(db, user_id: str):
    from backend.models import Category
    defaults = [
        ("Alimentación",        "🍽️", "#22d48f"),
        ("Transporte",          "🏍️", "#3b9eff"),
        ("Regalos",             "🎁", "#f472b6"),
        ("Suscripciones",       "📱", "#7c6aff"),
        ("Servicios del hogar", "🏠", "#ffad3b"),
        ("Ropa y accesorios",   "👗", "#c084fc"),
        ("Salud y seguros",     "🏥", "#ff7b54"),
        ("Entretenimiento",     "🎬", "#ff5e7a"),
        ("Inversión",           "📈", "#22d48f"),
        ("Nómina e ingresos",   "💼", "#3b9eff"),
        ("Finanzas e impuestos","🏦", "#888888"),
        ("Gimnasio",            "💪", "#ff7b54"),
        ("Mascotas",            "🐾", "#ffad3b"),
        ("Préstamos",           "🤝", "#ff5e7a"),
        ("Créditos e hipoteca", "🏡", "#3b9eff"),
        ("Varios",              "📦", "#555555"),
    ]
    for name, emoji, color in defaults:
        cat = Category(
            id=generate_id("cat"),
            name=name,
            emoji=emoji,
            color=color,
            user_id=user_id,
        )
        db.add(cat)
    db.flush()