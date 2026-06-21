"""
Smoke test MANUAL del Notification Component contra los SaaS reales.

A diferencia de tests/test_notification.py (que mockea todo y prueba la
lógica de notify() en CI), este script SÍ cruza la red hacia Twilio y
SendGrid — pero configurado para NO enviar mensajes reales ni generar
cargos. Sirve para responder una sola pregunta: "¿mis credenciales y mi
integración con el SDK funcionan de verdad?".

Las tres capas de testing del componente:

  1. Unit (CI)          -> tests/test_notification.py   (todo mockeado)
  2. Integración real   -> ESTE script                  (test creds + sandbox)
  3. End-to-end real    -> este script con --live        (envía de verdad)

Uso:
    # SMS contra Twilio con TEST CREDENTIALS (no envía, no cobra):
    python tools/smoke_notifications.py --sms

    # Email contra SendGrid en SANDBOX (valida, no envía):
    python tools/smoke_notifications.py --email

    # Ambos:
    python tools/smoke_notifications.py --sms --email

    # Envío REAL (cuenta trial + número/email verificados):
    python tools/smoke_notifications.py --sms --live
"""

import argparse
import os
import sys

from dotenv import load_dotenv

load_dotenv()


def smoke_sms(live: bool) -> bool:
    """
    Prueba el envío de SMS.

    Modo test (default): usa TWILIO_TEST_ACCOUNT_SID / TWILIO_TEST_AUTH_TOKEN
    y el número mágico +15005550006 como From. Twilio valida la request
    igual que en producción, devuelve un SID simulado, pero no envía SMS
    ni cobra. Cambiá el From por otro número mágico para forzar errores
    (ej: +15005550001 -> 21606 'From inválido').

    Modo --live: usa las credenciales reales y el From real. El 'to'
    (ALERT_PHONE) debe ser un número verificado en la cuenta trial.
    """
    from twilio.rest import Client
    from twilio.base.exceptions import TwilioRestException

    if live:
        sid = os.environ["TWILIO_ACCOUNT_SID"]
        token = os.environ["TWILIO_AUTH_TOKEN"]
        from_number = os.environ["TWILIO_FROM"]
        print("[SMS] Modo LIVE — esto envía un SMS REAL.")
    else:
        sid = os.environ["TWILIO_TEST_ACCOUNT_SID"]
        token = os.environ["TWILIO_TEST_AUTH_TOKEN"]
        from_number = "+15005550006"  # número mágico válido
        print("[SMS] Modo TEST — no se envía nada ni se cobra.")

    to = os.environ.get("ALERT_PHONE", "+15005550006")
    client = Client(sid, token)

    try:
        msg = client.messages.create(
            body="🌡️ AgTechUNS smoke test: alerta de calor extremo en lote-4.",
            from_=from_number,
            to=to,
        )
        print(f"[SMS] OK  sid={msg.sid}  status={msg.status}  to={to}")
        return True
    except TwilioRestException as e:
        # En modo test, un número mágico puede devolver un error ESPERADO.
        print(f"[SMS] Twilio respondió error  code={e.code}  msg={e.msg}")
        return False


def smoke_email(live: bool) -> bool:
    """
    Prueba el envío de email vía SendGrid.

    Modo sandbox (default): mail_settings.sandbox_mode = True. SendGrid
    valida la request completa (API key, From verificado, formato) y
    devuelve 200, pero NO entrega el email. Es el equivalente a las test
    credentials de Twilio.

    Modo --live: sandbox off. Envía de verdad; el From debe ser un Single
    Sender verificado en SendGrid.
    """
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail, MailSettings, SandBoxMode

    api_key = os.environ["SENDGRID_API_KEY"]
    from_email = os.environ.get("SENDGRID_FROM", "alertas@agtech.com")
    to_email = os.environ.get("ALERT_EMAIL", "admin@agtech.com")

    mail = Mail(
        from_email=from_email,
        to_emails=to_email,
        subject="⚠️ AgTechUNS — smoke test",
        plain_text_content="Alerta de prueba del Notification Component.",
    )
    if not live:
        mail.mail_settings = MailSettings(sandbox_mode=SandBoxMode(enable=True))
        print("[EMAIL] Modo SANDBOX — valida pero no entrega.")
    else:
        print("[EMAIL] Modo LIVE — esto envía un email REAL.")

    try:
        resp = SendGridAPIClient(api_key).send(mail)
        ok = resp.status_code in (200, 202)
        print(f"[EMAIL] {'OK' if ok else 'FALLO'}  status={resp.status_code}  to={to_email}")
        return ok
    except Exception as e:  # python_http_client.exceptions.HTTPError, etc.
        print(f"[EMAIL] Error: {type(e).__name__}: {e}")
        return False


def main() -> int:
    p = argparse.ArgumentParser(description="Smoke test del Notification Component.")
    p.add_argument("--sms", action="store_true", help="Probar SMS (Twilio)")
    p.add_argument("--email", action="store_true", help="Probar email (SendGrid)")
    p.add_argument("--live", action="store_true", help="Envío REAL (default: test/sandbox)")
    args = p.parse_args()

    if not (args.sms or args.email):
        p.error("Indicá al menos --sms o --email")

    results = []
    if args.sms:
        results.append(smoke_sms(args.live))
    if args.email:
        results.append(smoke_email(args.live))

    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
