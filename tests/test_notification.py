"""
Test de integración del Notification Component.

Ejecuta el punto de entrada público (notify desde __init__.py)
y verifica que los proveedores de email y SMS sean invocados.

Correr con:
    python tests/test_notification.py
"""

import os
import sys
import unittest
from unittest.mock import AsyncMock, patch
from unittest import IsolatedAsyncioTestCase

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


if __name__ == "__main__":
    unittest.main()
