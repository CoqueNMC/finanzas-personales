from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from backend.core.config import get_settings

settings = get_settings()

conf = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_FROM=settings.mail_from,
    MAIL_PORT=settings.mail_port,
    MAIL_SERVER=settings.mail_server,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
)


async def send_reset_email(email: str, name: str, reset_token: str, base_url: str):
    reset_url = f"{base_url}/reset-password?token={reset_token}"
    html = f"""
    <div style="font-family:sans-serif;max-width:480px;margin:auto;padding:32px;">
        <h2 style="color:#7c6aff;">Finanzas Personales</h2>
        <p>Hola <strong>{name}</strong>,</p>
        <p>Recibiste este correo porque solicitaste restablecer tu contraseña.</p>
        <a href="{reset_url}" style="display:inline-block;margin:24px 0;padding:12px 24px;background:#7c6aff;color:white;border-radius:8px;text-decoration:none;font-weight:500;">
            Restablecer contraseña
        </a>
        <p style="color:#888;font-size:13px;">Este enlace expira en 1 hora. Si no solicitaste esto, ignora este correo.</p>
    </div>
    """
    message = MessageSchema(
        subject="Restablecer contraseña — Finanzas Personales",
        recipients=[email],
        body=html,
        subtype=MessageType.html,
    )
    fm = FastMail(conf)
    await fm.send_message(message)