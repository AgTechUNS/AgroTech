"""
Test de integración del Notification Component.

Ejecuta el punto de entrada público (notify desde __init__.py)
y verifica que los proveedores de email y SMS sean invocados.

Correr con:
    python tests/test_notification.py
"""

import contextlib
import io
import os
import sys
import unittest
from unittest.mock import AsyncMock, patch
from unittest import IsolatedAsyncioTestCase

from dotenv import load_dotenv

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
load_dotenv(os.path.join(ROOT_DIR, ".env"))

_SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from modules.notification_component import EventType, NotificationJob, notify


class TestNotifyDispatchesEmailAndSms(IsolatedAsyncioTestCase):
    def setUp(self):
        self.job = NotificationJob(
            event_type=EventType.HEAT_STRESS,
            field_id="lote-4",
            value=38.5,
            threshold=35.0,
        )

    @patch("modules.notification_component._handler.send_email", new_callable=AsyncMock)
    @patch("modules.notification_component._handler.send_sms", new_callable=AsyncMock)
    @patch("modules.notification_component._handler.send_in_app", new_callable=AsyncMock)
    @patch("modules.notification_component._handler.is_duplicate", new_callable=AsyncMock)
    async def test_notify_calls_email_and_sms(
        self,
        mock_is_duplicate,
        mock_send_in_app,
        mock_send_sms,
        mock_send_email,
    ):
        mock_is_duplicate.return_value = False

        await notify(self.job)

        expected_message = (
            f"🌡️ Alerta de Calor Extremo: temperatura máxima de {self.job.value}°C "
            f"detectada en {self.job.field_id} (umbral: {self.job.threshold}°C)."
        )
        mock_send_email.assert_awaited_once_with(expected_message, "Calor Extremo")
        mock_send_sms.assert_awaited_once_with(expected_message)

    @patch("modules.notification_component._handler.send_email", new_callable=AsyncMock)
    @patch("modules.notification_component._handler.send_sms", new_callable=AsyncMock)
    @patch("modules.notification_component._handler.send_in_app", new_callable=AsyncMock)
    @patch("modules.notification_component._handler.is_duplicate", new_callable=AsyncMock)
    async def test_duplicate_skips_all_channels(
        self,
        mock_is_duplicate,
        mock_send_in_app,
        mock_send_sms,
        mock_send_email,
    ):
        mock_is_duplicate.return_value = True

        await notify(self.job)

        mock_send_email.assert_not_awaited()
        mock_send_sms.assert_not_awaited()
        mock_send_in_app.assert_not_awaited()

    @patch("modules.notification_component._handler.send_email", new_callable=AsyncMock)
    @patch("modules.notification_component._handler.send_sms", new_callable=AsyncMock)
    @patch("modules.notification_component._handler.send_in_app", new_callable=AsyncMock)
    @patch("modules.notification_component._handler.is_duplicate", new_callable=AsyncMock)
    async def test_hydric_stress_uses_correct_template(
        self,
        mock_is_duplicate,
        mock_send_in_app,
        mock_send_sms,
        mock_send_email,
    ):
        mock_is_duplicate.return_value = False
        job = NotificationJob(
            event_type=EventType.HYDRIC_STRESS,
            field_id="lote-7",
            value=22.0,
            threshold=30.0,
        )

        await notify(job)

        expected_message = (
            f"💧 Alerta de Estrés Hídrico: humedad promedio de {job.value}% "
            f"en {job.field_id} por debajo del umbral ({job.threshold}%)."
        )
        mock_send_email.assert_awaited_once_with(expected_message, "Estrés Hídrico")
        mock_send_sms.assert_awaited_once_with(expected_message)

    async def test_provider_logging_prints_destinations(self):
        from modules.notification_component._providers import _email, _sms

        class DummySendGridClient:
            def __init__(self, api_key):
                self.api_key = api_key

            def send(self, mail):
                return None

        class DummyMail:
            def __init__(self, *, from_email, to_emails, subject, plain_text_content):
                self.from_email = from_email
                self.to_emails = to_emails
                self.subject = subject
                self.plain_text_content = plain_text_content

        class DummyMailSettings:
            def __init__(self, sandbox_mode=None):
                self.sandbox_mode = sandbox_mode

        class DummySandBoxMode:
            def __init__(self, enable):
                self.enable = enable

        class DummyTwilioMessages:
            def create(self, *, body, from_, to):
                return None

        class DummyTwilioClient:
            def __init__(self, account_sid, auth_token):
                self.messages = DummyTwilioMessages()

        dummy_sendgrid = type("sendgrid", (), {"SendGridAPIClient": DummySendGridClient})
        dummy_mail_helpers = type(
            "helpers", (), {"Mail": DummyMail, "MailSettings": DummyMailSettings, "SandBoxMode": DummySandBoxMode}
        )
        dummy_sendgrid_helpers = type("sendgrid_helpers", (), {"helpers": dummy_mail_helpers})

        class DummyTwilioRest:
            Client = DummyTwilioClient

        with patch.dict(
            sys.modules,
            {
                "sendgrid": dummy_sendgrid,
                "sendgrid.helpers.mail": type(
                    "module",
                    (),
                    {"Mail": DummyMail, "MailSettings": DummyMailSettings, "SandBoxMode": DummySandBoxMode},
                ),
                "twilio.rest": type("module", (), {"Client": DummyTwilioClient}),
            },
        ):
            with patch.object(_email, "_SENDGRID_API_KEY", "dummy-key"), patch.object(
                _email, "_ALERT_EMAIL", "dest@example.com"
            ), patch.object(_email, "_FROM_EMAIL", "from@example.com"), patch.object(
                _email, "_SANDBOX_MODE", False
            ), patch.object(_sms, "_ALERT_PHONE", "+5491112345678"), patch.object(
                _sms, "_get_client", lambda: DummyTwilioClient("sid", "token")
            ):
                captured = io.StringIO()
                with contextlib.redirect_stdout(captured):
                    await _email.send_email("mensaje", "Aviso")
                    await _sms.send_sms("mensaje")

        output = captured.getvalue()
        self.assertIn("Email enviado a dest@example.com desde from@example.com con asunto 'Aviso'", output)
        self.assertIn("SMS enviado a +5491112345678 desde "+"", output)


if __name__ == "__main__":
    unittest.main()
