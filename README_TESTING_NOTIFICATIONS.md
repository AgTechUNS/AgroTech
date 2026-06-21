# Testing del Notification Component

El componente cruza dos fronteras de red reales (Twilio para SMS, SendGrid
para email). Por eso el testing tiene **tres capas**, cada una responde una
pregunta distinta:

| Capa | Archivo | Qué prueba | Envía de verdad? |
|------|---------|------------|------------------|
| 1. Unit (CI) | `tests/test_notification.py` | La lógica de `notify()`: dedup, templating, dispatch a los 3 canales | No (todo mockeado) |
| 2. Integración | `tools/smoke_notifications.py` | Que las credenciales y el SDK funcionan contra el SaaS real | No (test creds + sandbox) |
| 3. End-to-end | `tools/smoke_notifications.py --live` | Que el mensaje llega al destino | Sí |

## Por qué no necesitás enviar SMS reales para testear Twilio

Twilio provee **Test Credentials** (un SID y token aparte, en Console >
Account > API keys & tokens). Cuando autenticás con ellas, Twilio **valida
la request exactamente igual que en producción**, pero no envía el SMS, no
toca tu cuenta y no cobra. Para el `From` se usa el **número mágico `+15005550006`**, que Twilio trata
como válido y devuelve una request exitosa (con un `sid` simulado). Hay
otros números mágicos que, usados como `From` o como `To`, fuerzan errores
específicos (número inválido, no SMS-capable, sin permiso de región, etc.)
para que puedas testear tus rutas de error. La tabla completa y vigente de
cada código está en la doc oficial:
<https://www.twilio.com/docs/iam/test-credentials> (sección *Test sending an
SMS*).

Limitación: las test credentials **no disparan status callbacks** y no
pueden usar números de tu cuenta real como `From`.

## Por qué no necesitás enviar emails reales para testear SendGrid

SendGrid tiene **Sandbox Mode** (`mail_settings.sandbox_mode = true`). Valida
toda la request (API key, From verificado, formato) y devuelve 200, pero no
entrega. El provider `_email.py` ya lo soporta vía `SENDGRID_SANDBOX_MODE`.

## Cómo correr cada capa

```bash
# Capa 1 — unit, no necesita credenciales:
python tests/test_notification.py

# Capa 2 — integración, con test creds + sandbox (no envía nada):
python tools/smoke_notifications.py --sms --email

# Capa 3 — envío real (cuenta trial, destino verificado, sandbox off):
python tools/smoke_notifications.py --sms --live
```

## Gotcha de cuenta trial (envío real)

En una cuenta Twilio gratis solo podés mandar SMS a **números verificados**
y el mensaje lleva el prefijo "Sent from a Twilio trial account". Mismo
criterio en SendGrid: el `From` tiene que ser un **Single Sender verificado**.
