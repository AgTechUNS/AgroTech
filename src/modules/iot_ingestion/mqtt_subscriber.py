import paho.mqtt.client as mqtt
import json
import base64
import asyncio
import time
import os
from collections import OrderedDict
from datetime import datetime
from modules.iot_ingestion.schemas import LecturaNormalizada
from modules.iot_ingestion.ports import TimeSeriesRepositoryInterface


class TTLCache:
    """Caché TTL simple sin dependencias externas.
    Clave: f"{sensor_id}_{timestamp}" → expira tras ttl segundos.
    """
    def __init__(self, maxsize: int = 10000, ttl: int = 3600):
        self._cache: OrderedDict[str, float] = OrderedDict()
        self._maxsize = maxsize
        self._ttl = ttl

    def __contains__(self, key: str) -> bool:
        if key not in self._cache:
            return False
        if time.time() > self._cache[key]:
            del self._cache[key]
            return False
        return True

    def add(self, key: str) -> None:
        self._cache[key] = time.time() + self._ttl
        if len(self._cache) > self._maxsize:
            self._cache.popitem(last=False)


class IotIngestionService:
    def __init__(self, broker_url: str, port: int, repository: TimeSeriesRepositoryInterface, num_workers: int = 3):
        self.broker = broker_url
        self.port = port
        self.repository = repository
        self.num_workers = num_workers
        self.client = mqtt.Client()
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect
        self.client.reconnect_delay_set(min_delay=1, max_delay=120)

        self._main_loop: asyncio.AbstractEventLoop | None = None

        # Deduplicación
        self.dedup_cache = TTLCache(maxsize=10000, ttl=3600)

        # Cola de escritura asíncrona + DLQ
        self.write_queue: asyncio.Queue[LecturaNormalizada] = asyncio.Queue(maxsize=5000)
        self.dlq_path = os.path.join(os.path.dirname(__file__) or ".", "dlq_fallos.json")

        self._worker_tasks: list[asyncio.Task] = []

        print(f"[IotIngestionService] Inicializado")
        print(f"   Broker: {self.broker}:{self.port}")
        print(f"   Workers: {self.num_workers}")

    def start_workers(self, loop: asyncio.AbstractEventLoop):
        """Crea las tareas workers en el event loop indicado (debe ser el mismo donde se creó el repo)."""
        self._main_loop = loop
        for i in range(self.num_workers):
            task = asyncio.ensure_future(self._worker_loop(i), loop=loop)
            self._worker_tasks.append(task)
        print(f"[IotIngestionService] {self.num_workers} workers creados en event loop principal")

    async def _worker_loop(self, worker_id: int = 0):
        """Consume LecturaNormalizada de la cola y las persiste con retry."""
        while True:
            lectura = await self.write_queue.get()
            await self._process_with_retry(lectura, worker_id)
            self.write_queue.task_done()

    async def _process_with_retry(self, lectura: LecturaNormalizada, worker_id: int = 0, max_retries: int = 5):
        """Intenta guardar con backoff exponencial. Falla → DLQ."""
        tag = f"[W{worker_id}]"
        backoff = 1
        for attempt in range(max_retries):
            try:
                await self.repository.guardar_telemetria(lectura)
                print(f"{tag} Lectura persistida: {lectura.sensor_id}")
                return
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"{tag} Reintento {attempt + 1}/{max_retries} para {lectura.sensor_id}: {e}")
                    await asyncio.sleep(backoff)
                    backoff = min(backoff * 2, 60)
                else:
                    print(f"{tag} Fallo definitivo para {lectura.sensor_id}: {e}")
                    await self._enviar_a_dlq(lectura, str(e))

    async def _enviar_a_dlq(self, lectura: LecturaNormalizada, error: str):
        """Escribe la lectura fallida al archivo DLQ (JSON Lines)."""
        entry = {
            "timestamp_fallo": datetime.utcnow().isoformat() + "Z",
            "sensor_id": lectura.sensor_id,
            "campo_id": lectura.campo_id,
            "parcela_id": lectura.parcela_id,
            "temperatura": lectura.temperatura,
            "humedad": lectura.humedad,
            "timestamp_lectura": lectura.timestamp.isoformat(),
            "error": error,
        }
        try:
            with open(self.dlq_path, "a") as f:
                f.write(json.dumps(entry) + "\n")
            print(f"[DLQ]  Escrito a DLQ: {lectura.sensor_id}")
        except Exception as e:
            print(f"[DLQ] Error escribiendo DLQ: {e}")

    def start(self):
        print(f"[IotIngestionService] Conectando a broker MQTT...")
        self.client.connect(self.broker, self.port, 60)
        self.client.loop_start()
        print("[IotIngestionService] Componente iniciado y escuchando (loop_start)")

    def stop(self):
        """Detiene el loop MQTT y las tareas workers gracefulmente."""
        print("[IotIngestionService] Deteniendo componente...")
        self.client.loop_stop()
        self.client.disconnect()
        for task in self._worker_tasks:
            task.cancel()
        print("[IotIngestionService] Componente detenido.")

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print(f"[OK]  [MQTT] Conectado al broker")
            client.subscribe("v3/agtechuns-app/devices/+/up", qos=1)
            print(f"[Topic]  [MQTT] Suscrito a: v3/agtechuns-app/devices/+/up")
        else:
            print(f"[Error]  [MQTT] Error de conexión: código {rc}")
    
    def _on_disconnect(self, client, userdata, rc):
        if rc != 0:
            print(f"[Warn]  [MQTT] Desconexión inesperada: código {rc} — el cliente reintentará automáticamente")

    def _on_message(self, client, userdata, msg):
        try:
            print(f"[Msg]  [MQTT] Mensaje recibido en: {msg.topic}")
            lora_packet = json.loads(msg.payload.decode())
            device_id = lora_packet['end_device_ids']['device_id']
            timestamp_str = lora_packet['received_at']

            # --- DEDUPLICACIÓN ---
            dedup_key = f"{device_id}_{timestamp_str}"
            if dedup_key in self.dedup_cache:
                print(f"[Skip]  [Dedup] Duplicado descartado: {dedup_key}")
                return
            self.dedup_cache.add(dedup_key)

            payload_b64 = lora_packet['uplink_message']['frm_payload']
            payload_str = base64.b64decode(payload_b64).decode('utf-8')
            telemetria = json.loads(payload_str)

            temp = float(telemetria['t'])
            hum = float(telemetria['h'])
            campo_id = lora_packet.get('campo_id')
            parcela_id = lora_packet.get('parcela_id')
            print(f"[Data]  [MQTT] Datos parseados - Sensor: {device_id}, Campo: {campo_id}, Parcela: {parcela_id}, T: {temp}°C, H: {hum}%")


            lectura_limpia = LecturaNormalizada(
                sensor_id=device_id,
                campo_id=campo_id,
                parcela_id=parcela_id,
                temperatura=temp,
                humedad=hum,
                timestamp=datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
            )

            # Encolar escritura en el event loop principal
            if self._main_loop:
                asyncio.run_coroutine_threadsafe(
                    self.write_queue.put(lectura_limpia),
                    self._main_loop
                )
                print(f"[Encolado] Lectura encolada para persistir: {device_id}")

        except Exception as e:
            print(f"[Error]  Error interno procesando paquete: {e}")
            import traceback
            traceback.print_exc()
