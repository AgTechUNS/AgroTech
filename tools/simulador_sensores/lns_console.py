import curses
import queue
import time
import threading
import json
import os
import base64
import random
import pathlib
from collections import deque
from dataclasses import dataclass, asdict
from datetime import datetime

try:
    import paho.mqtt.client as mqtt
except ImportError:
    mqtt = None


# ---------------------------------------------------------------------------
# Modelos
# ---------------------------------------------------------------------------

@dataclass
class Gateway:
    gateway_id: str
    campo_id: str


@dataclass
class Sensor:
    device_id: str
    campo_id: str
    parcela_id: str


@dataclass
class ReceptionLog:
    timestamp: str
    device_id: str
    campo_id: str
    parcela_id: str
    payload: dict
    temperatura: float
    humedad: float
    gateways: list
    best_gateway: str


# ---------------------------------------------------------------------------
# Estado del simulador
# ---------------------------------------------------------------------------

TOOLS_DIR = pathlib.Path(__file__).parent.resolve()
SPA_DATA_DIR = TOOLS_DIR.parents[1] / ".data"

REGISTRO_FILE = SPA_DATA_DIR / "sensores.json"
CAMPOS_FILE = SPA_DATA_DIR / "campos.json"
PARCELAS_FILE = SPA_DATA_DIR / "parcelas.json"
REGISTRO_LEGACY = TOOLS_DIR / "registro_lns.json"

BROKER = os.getenv("BROKER", "localhost")
PORT = int(os.getenv("PORT", "1883"))


class LNSState:
    def __init__(self):
        self.campos: list[str] = []
        self.gateways: list[Gateway] = []
        self.sensors: list[Sensor] = []
        self.campo_activo: str | None = None
        self.transmitiendo = False
        self.historial: deque[ReceptionLog] = deque(maxlen=20)
        self.thread: threading.Thread | None = None
        self.mqtt_client = mqtt.Client() if mqtt else None

        self.packet_count = 0
        self.last_packet_info = ""

    def _load_spa_campos(self):
        try:
            if os.path.exists(CAMPOS_FILE):
                with open(CAMPOS_FILE) as f:
                    data = json.load(f)
                if isinstance(data, list):
                    self.campos = [c["nombreCampo"] for c in data if "nombreCampo" in c]
        except Exception:
            pass

    def _load_spa_parcelas(self, campo_id):
        try:
            if os.path.exists(PARCELAS_FILE):
                with open(PARCELAS_FILE) as f:
                    data = json.load(f)
                if isinstance(data, list):
                    return [p["nombreParcela"] for p in data if p.get("nombreCampo") == campo_id]
        except Exception:
            pass
        return []

    def _read_sensor_file(self):
        """Read .data/sensores.json (camelCase format)"""
        try:
            if os.path.exists(REGISTRO_FILE):
                with open(REGISTRO_FILE) as f:
                    data = json.load(f)
                self.gateways = [Gateway(gw["gatewayId"], gw["nombreCampo"]) for gw in data.get("gateways", [])]
                raw_sensors = data.get("sensors", [])
                self.sensors = []
                for s in raw_sensors:
                    if s.get("activo", True):
                        self.sensors.append(Sensor(s["deviceId"], s["nombreCampo"], s["nombreParcela"]))
            elif os.path.exists(REGISTRO_LEGACY):
                with open(REGISTRO_LEGACY) as f:
                    data = json.load(f)
                self.gateways = [Gateway(g["gateway_id"], g["campo_id"]) for g in data.get("gateways", [])]
                self.sensors = [Sensor(s["device_id"], s["campo_id"], s["parcela_id"]) for s in data.get("sensors", [])]
        except Exception:
            pass

    def _write_sensor_file(self):
        """Write .data/sensores.json (camelCase format)"""
        SPA_DATA_DIR.mkdir(parents=True, exist_ok=True)
        data = {
            "gateways": [{"gatewayId": g.gateway_id, "nombreCampo": g.campo_id} for g in self.gateways],
            "sensors": [{"deviceId": s.device_id, "nombreCampo": s.campo_id, "nombreParcela": s.parcela_id, "tipo": "temperatura_humedad", "activo": True} for s in self.sensors],
        }
        with open(REGISTRO_FILE, "w") as f:
            json.dump(data, f, indent=2)

    def load(self):
        self._load_spa_campos()
        self._read_sensor_file()

    def save(self):
        self._write_sensor_file()

    def sensores_sin_cobertura(self) -> list[Sensor]:
        campos_con_gw = {g.campo_id for g in self.gateways}
        return [s for s in self.sensors if s.campo_id not in campos_con_gw]

    def gateways_del_campo(self, campo_id: str) -> list[Gateway]:
        return [g for g in self.gateways if g.campo_id == campo_id]

    def sensors_del_campo(self, campo_id: str) -> list[Sensor]:
        return [s for s in self.sensors if s.campo_id == campo_id]


# ---------------------------------------------------------------------------
# Hilo de transmisión MQTT
# ---------------------------------------------------------------------------

def _loop_transmision(state: LNSState, log_queue: queue.Queue):
    if not mqtt:
        log_queue.put("ERROR: paho-mqtt no está instalado (pip install paho-mqtt)")
        state.transmitiendo = False
        return

    try:
        state.mqtt_client.connect(BROKER, PORT, 60)
    except Exception as e:
        log_queue.put(f"ERROR: No se pudo conectar al broker MQTT: {e}")
        state.transmitiendo = False
        return

    log_queue.put("Transmisión LNS iniciada.")

    try:
        while state.transmitiendo:
            for sensor in list(state.sensors):
                gateways = state.gateways_del_campo(sensor.campo_id)
                if not gateways:
                    log_queue.put(f"⚠ {sensor.device_id} en '{sensor.campo_id}' sin gateway — perdido")
                    continue

                temp = round(random.uniform(10.0, 35.0), 2)
                hum = round(random.uniform(30.0, 80.0), 2)

                payload_bytes = json.dumps({"t": temp, "h": hum}).encode("utf-8")
                payload_b64 = base64.b64encode(payload_bytes).decode("utf-8")

                rx_list = []
                for gw in gateways:
                    rssi = random.randint(-110, -40)
                    rx_list.append({"gateway_ids": {"gateway_id": gw.gateway_id}, "rssi": rssi})

                best_gw = max(rx_list, key=lambda x: x["rssi"])
                ts = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())

                msg = {
                    "end_device_ids": {"device_id": sensor.device_id},
                    "campo_id": sensor.campo_id,
                    "parcela_id": sensor.parcela_id,
                    "received_at": ts,
                    "uplink_message": {
                        "f_port": 1,
                        "frm_payload": payload_b64,
                        "rx_metadata": [best_gw],
                    }
                }

                topic = f"v3/agtechuns-app/devices/{sensor.device_id}/up"
                state.mqtt_client.publish(topic, json.dumps(msg), qos=1)

                gws_str = ", ".join(f"{g['gateway_ids']['gateway_id']}({g['rssi']})" for g in rx_list)
                log_line = (f"{sensor.device_id} | {sensor.campo_id}/{sensor.parcela_id} | "
                           f"T:{temp}C H:{hum}% | receptoras: {gws_str} | mejor: {best_gw['gateway_ids']['gateway_id']}")
                log_queue.put(log_line)

                state.last_packet_info = (f"{sensor.device_id} → {best_gw['gateway_ids']['gateway_id']} "
                                          f"(RSSI {best_gw['rssi']})  T:{temp}C H:{hum}%")
                state.packet_count += 1

                log = ReceptionLog(
                    timestamp=ts,
                    device_id=sensor.device_id,
                    campo_id=sensor.campo_id,
                    parcela_id=sensor.parcela_id,
                    payload={"t": temp, "h": hum},
                    temperatura=temp,
                    humedad=hum,
                    gateways=rx_list,
                    best_gateway=best_gw["gateway_ids"]["gateway_id"],
                )
                state.historial.append(log)

            time.sleep(10)
    except Exception as e:
        log_queue.put(f"ERROR en transmisión: {e}")
    finally:
        if state.mqtt_client:
            try:
                state.mqtt_client.disconnect()
            except Exception:
                pass
        log_queue.put("Transmisión LNS detenida.")


# ---------------------------------------------------------------------------
# Aplicación TUI con curses
# ---------------------------------------------------------------------------

class App:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.state = LNSState()
        self.state.load()
        self.log_queue: queue.Queue[str] = queue.Queue()

        curses.use_default_colors()
        curses.curs_set(0)
        if curses.has_colors():
            curses.init_pair(1, curses.COLOR_CYAN, -1)
            curses.init_pair(2, curses.COLOR_GREEN, -1)
            curses.init_pair(3, curses.COLOR_YELLOW, -1)
            curses.init_pair(4, curses.COLOR_RED, -1)
            curses.init_pair(5, curses.COLOR_MAGENTA, -1)
            curses.init_pair(6, curses.COLOR_BLUE, -1)

        self.running = True
        self.view = "main"
        self.view_data = {}
        self.msg_text = ""
        self.msg_time = 0

        self.log_display = deque(maxlen=500)

        # Input state
        self.in_input = False
        self.input_prompt = ""
        self.input_val = ""
        self.input_cb = None

    # ---------------------------------------------------------------
    # Utilidades de dibujo
    # ---------------------------------------------------------------

    def color(self, pair):
        return curses.color_pair(pair) if curses.has_colors() else 0

    def write(self, y, x, text, pair=0, bold=False):
        attr = self.color(pair)
        if bold:
            attr |= curses.A_BOLD
        try:
            self.stdscr.addstr(y, x, text[:self.stdscr.getmaxyx()[1] - x - 1], attr)
        except curses.error:
            pass

    def write_center(self, y, text, pair=0, bold=False):
        w = self.stdscr.getmaxyx()[1]
        x = max(0, (w - len(text)) // 2)
        self.write(y, x, text, pair, bold)

    def separator(self, y, char="─"):
        w = self.stdscr.getmaxyx()[1]
        self.write(y, 0, char * w, 6)

    def show_msg(self, text):
        self.msg_text = text
        self.msg_time = time.time()

    # ---------------------------------------------------------------
    # Dibujado completo
    # ---------------------------------------------------------------

    def draw(self):
        self.stdscr.erase()
        h, w = self.stdscr.getmaxyx()

        self._draw_header(h, w)
        self._draw_status(h, w)
        content_top = 4

        content_end = content_top

        if self.in_input:
            content_end = self._draw_input_view(content_top, h, w)
        elif self.view == "main":
            content_end = self._draw_main_menu(content_top, h, w)
        elif self.view == "campo_select":
            content_end = self._draw_campo_select(content_top, h, w)
        elif self.view == "campo_menu":
            content_end = self._draw_campo_menu(content_top, h, w)
        elif self.view == "list_gw_sensors":
            content_end = self._draw_list_gw_sensors(content_top, h, w)
        elif self.view == "historial":
            content_end = self._draw_historial(content_top, h, w)
        elif self.view == "list_selection":
            content_end = self._draw_list_selection(content_top, h, w)
        elif self.view == "parcela_select":
            content_end = self._draw_parcela_select(content_top, h, w)

        self._draw_log_panel(content_end + 1, h - 1, h, w)

        if self.msg_text and time.time() - self.msg_time < 3:
            self.write(h - 1, 0, self.msg_text, 2)

        self.stdscr.refresh()

    def _draw_header(self, h, w):
        self.write_center(0, "LNS Console Simulator", 1, bold=True)
        self.separator(1)

    def _draw_status(self, h, w):
        estado = "▶ TRANSMITIENDO" if self.state.transmitiendo else "⏹ DETENIDO"
        campo = self.state.campo_activo or "ninguno"
        status_color = 2 if self.state.transmitiendo else 3

        self.write(2, 0, f"  CAMPO ACTIVO: {campo}", 6)
        self.write(2, max(0, w - len(estado) - 3), f"  {estado}", status_color, bold=True)
        self.write(3, 0, f"  PAQUETES: {self.state.packet_count}", 0)
        if self.state.last_packet_info:
           self.write(3, max(0, w - len(self.state.last_packet_info) - 3), f"  {self.state.last_packet_info}", 5)
        self.separator(3)

    def _draw_main_menu(self, y, h, w):
        items = [
            ("1", "Gestionar campo"),
            ("2", "Iniciar / Detener transmision LNS"),
            ("3", "Mostrar ultimas recepciones"),
            ("4", "Salir"),
        ]
        for i, (key, label) in enumerate(items):
            self.write(y + i, 4, f"[{key}]  {label}")
        return y + len(items)

    def _draw_campo_select(self, y, h, w):
        if not self.state.campos:
            self.write(y, 4, "No hay campos en la aplicacion web.", 3)
            self.write(y + 1, 4, "Crealos desde la SPA (app web) primero.")
            y += 2
        else:
            self.write(y, 4, "Campos sincronizados de la aplicacion web:", 6)
            y += 1
            for i, campo in enumerate(self.state.campos):
                gw = len(self.state.gateways_del_campo(campo))
                sn = len(self.state.sensors_del_campo(campo))
                active = " ◀ ACTIVO" if campo == self.state.campo_activo else ""
                self.write(y + i, 4, f"[{i+1}]  {campo}  (GW: {gw}  Sens: {sn}){active}")

            y += len(self.state.campos)

        self.write(y, 4, "[N]  Crear nuevo campo (solo local)")
        self.write(y + 1, 4, "[0]  Volver")
        return y + 2

    def _draw_campo_menu(self, y, h, w):
        campo_id = self.view_data.get("campo_id", "")
        self.write(y, 4, f"Gestion: {campo_id}", 1, bold=True)

        sin_cob = self.state.sensores_sin_cobertura()
        sin_cob_campo = [s for s in sin_cob if s.campo_id == campo_id]
        if sin_cob_campo:
            self.write(y + 1, 4, f"⚠  {len(sin_cob_campo)} sensor(es) sin cobertura", 3)

        offset = 2 if sin_cob_campo else 1
        items = [
            ("1", "Listar gateways y sensores"),
            ("2", "Registrar nueva gateway"),
            ("3", "Registrar nuevo sensor"),
            ("4", "Eliminar gateway"),
            ("5", "Eliminar sensor"),
            ("6", "Volver"),
        ]
        for i, (key, label) in enumerate(items):
            self.write(y + offset + i, 4, f"[{key}]  {label}")
        return y + offset + len(items)

    def _draw_list_gw_sensors(self, y, h, w):
        campo_id = self.view_data.get("campo_id", "")
        gws = self.state.gateways_del_campo(campo_id)
        sens = self.state.sensors_del_campo(campo_id)

        self.write(y, 4, f"Gateways en '{campo_id}':", 1)
        y += 1
        if not gws:
            self.write(y, 6, "(ninguna)", 3)
            y += 1
        else:
            for gw in gws:
                self.write(y, 6, f"• {gw.gateway_id}")
                y += 1

        y += 1
        self.write(y, 4, f"Sensores en '{campo_id}':", 1)
        y += 1
        if not sens:
            self.write(y, 6, "(ninguno)", 3)
            y += 1
        else:
            for s in sens:
                self.write(y, 6, f"• {s.device_id}  →  parcela: {s.parcela_id}")
                y += 1

        sin_cob = self.state.sensores_sin_cobertura()
        sin_cob_campo = [s for s in sin_cob if s.campo_id == campo_id]
        if sin_cob_campo:
            y += 1
            self.write(y, 4, "⚠  Sensores SIN COBERTURA:", 3)
            y += 1
            for s in sin_cob_campo:
                self.write(y, 6, f"• {s.device_id}")
                y += 1

        y += 1
        self.write(y, 4, "[0]  Volver")
        return y + 1

    def _draw_historial(self, y, h, w):
        if not self.state.historial:
            self.write(y, 4, "No hay recepciones registradas aun.", 3)
            y += 1
        else:
            for log in reversed(self.state.historial):
                if y >= h - 2:
                    break
                self.write(y, 4, f"{log.timestamp}  {log.device_id}", 5)
                y += 1
                self.write(y, 6, f"Campo: {log.campo_id}  Parcela: {log.parcela_id}  T:{log.payload['t']}C  H:{log.payload['h']}%")
                y += 1
                self.write(y, 6, f"Mejor GW: {log.best_gateway}")
                y += 1
                for gw in log.gateways:
                    marca = "  ◀" if gw["gateway_ids"]["gateway_id"] == log.best_gateway else ""
                    self.write(y, 8, f"• {gw['gateway_ids']['gateway_id']}  RSSI: {gw['rssi']}{marca}")
                    y += 1
                y += 1
                if y >= h - 2:
                    break

        self.write(max(y, h - 2), 4, "[0]  Volver")

    def _draw_log_panel(self, y_start, y_end, h, w):
        if y_start >= y_end:
            return
        if y_start < h:
            self.separator(y_start - 1)
            self.write(y_start - 1, 2, " Log de transmisiones ", 6, bold=True)

        while len(self.log_display) < self.state.packet_count:
            try:
                line = self.log_queue.get_nowait()
                ts = datetime.now().strftime("%H:%M:%S")
                self.log_display.append(f"{ts}  {line}")
            except queue.Empty:
                break

        lines_to_show = y_end - y_start
        log_start = max(0, len(self.log_display) - lines_to_show)
        for i in range(min(lines_to_show, len(self.log_display) - log_start)):
            idx = log_start + i
            self.write(y_start + i, 2, self.log_display[idx], 5)

    def _draw_input_view(self, y, h, w):
        self.write(y, 4, self.input_prompt, 1, bold=True)
        self.write(y + 1, 4, "> " + self.input_val + ("█" if int(time.time() * 2) % 2 else " "))
        self.write(y + 2, 4, "[Enter] confirmar  [Esc] cancelar")
        return y + 3

    def _draw_list_selection(self, y, h, w):
        title = self.view_data.get("title", "")
        items = self.view_data.get("items", [])
        prompt = self.view_data.get("prompt", "")

        self.write(y, 4, title, 3, bold=True)
        y += 1
        for i, item in enumerate(items):
            label = item.gateway_id if hasattr(item, "gateway_id") else item.device_id
            self.write(y + i, 4, f"[{i+1}]  {label}")
        y += len(items)
        self.write(y, 4, prompt)
        return y + 1

    def _draw_parcela_select(self, y, h, w):
        campo_id = self.view_data.get("campo_id", "")
        parcelas = self.view_data.get("parcelas", [])
        dev_id = self.view_data.get("dev_id", "")

        self.write(y, 4, f"Seleccione parcela para sensor '{dev_id}' en '{campo_id}':", 1, bold=True)
        y += 1
        if not parcelas:
            self.write(y, 4, "(No hay parcelas disponibles en este campo)", 3)
            y += 1
        else:
            for i, p in enumerate(parcelas):
                self.write(y + i, 4, f"[{i+1}]  {p}")
            y += len(parcelas)
        self.write(y, 4, "[0]  Cancelar")
        return y + 1

    # ---------------------------------------------------------------
    # Manejo de entrada
    # ---------------------------------------------------------------

    def run(self):
        self.stdscr.timeout(200)
        while self.running:
            self.draw()
            key = self.stdscr.getch()
            if key == -1:
                continue
            self.handle_key(key)

        self.state.save()

    def handle_key(self, key):
        if self.in_input:
            self._handle_input_key(key)
            return

        if self.view == "main":
            self._handle_main_key(key)
        elif self.view == "campo_select":
            self._handle_campo_select_key(key)
        elif self.view == "campo_menu":
            self._handle_campo_menu_key(key)
        elif self.view == "list_gw_sensors":
            self._handle_list_key(key)
        elif self.view == "historial":
            self._handle_list_key(key)
        elif self.view == "list_selection":
            self._handle_list_selection_key(key)
        elif self.view == "parcela_select":
            self._handle_parcela_select_key(key)

    def _handle_input_key(self, key):
        if key == 10 or key == curses.KEY_ENTER:
            cb = self.input_cb
            val = self.input_val
            self.in_input = False
            self.input_val = ""
            self.input_cb = None
            curses.curs_set(0)
            if cb:
                cb(val)
        elif key == 27:
            self.in_input = False
            self.input_val = ""
            self.input_cb = None
            curses.curs_set(0)
        elif key == 127 or key == curses.KEY_BACKSPACE:
            self.input_val = self.input_val[:-1]
        elif 32 <= key <= 126:
            if len(self.input_val) < 60:
                self.input_val += chr(key)

    def start_input(self, prompt, callback):
        self.in_input = True
        self.input_prompt = prompt
        self.input_val = ""
        self.input_cb = callback
        curses.curs_set(1)

    def _handle_main_key(self, key):
        ch = chr(key) if 48 <= key <= 57 else ""
        if ch == "1":
            self.view = "campo_select"
        elif ch == "2":
            self._toggle_transmision()
        elif ch == "3":
            self.view = "historial"
        elif ch == "4":
            self.running = False

    def _handle_campo_select_key(self, key):
        ch = chr(key) if 48 <= key <= 57 else ""
        if ch == "0":
            self.view = "main"
        elif ch.isdigit():
            idx = int(ch) - 1
            if 0 <= idx < len(self.state.campos):
                self.state.campo_activo = self.state.campos[idx]
                self.state.save()
                self.view = "campo_menu"
                self.view_data = {"campo_id": self.state.campo_activo}
        elif key == ord('n') or key == ord('N'):
            self.start_input("Nombre del nuevo campo:", self._create_campo)

    def _create_campo(self, name):
        name = name.strip()
        if not name:
            self.show_msg("Nombre invalido")
            return
        if name in self.state.campos:
            self.show_msg(f"El campo '{name}' ya existe")
            return
        self.state.campos.append(name)
        self.state.campo_activo = name
        self.state.save()
        self.view = "campo_menu"
        self.view_data = {"campo_id": name}

    def _handle_campo_menu_key(self, key):
        ch = chr(key) if 48 <= key <= 57 else ""
        campo_id = self.view_data.get("campo_id", "")

        if ch == "1":
            self.view = "list_gw_sensors"
            self.view_data = {"campo_id": campo_id}
        elif ch == "2":
            self.start_input("ID de la nueva gateway:", lambda v: self._register_gw(campo_id, v))
        elif ch == "3":
            self.start_input("ID del nuevo sensor (DevEUI):", lambda v: self._register_sensor_step2(campo_id, v))
        elif ch == "4":
            self._delete_gw(campo_id)
        elif ch == "5":
            self._delete_sensor(campo_id)
        elif ch == "6":
            self.view = "campo_select"

    def _register_gw(self, campo_id, gw_id):
        gw_id = gw_id.strip()
        if not gw_id:
            self.show_msg("ID invalido")
            return
        if any(g.gateway_id == gw_id for g in self.state.gateways):
            self.show_msg(f"La gateway '{gw_id}' ya existe")
            return
        self.state.gateways.append(Gateway(gateway_id=gw_id, campo_id=campo_id))
        self.state.save()
        self.show_msg(f"Gateway '{gw_id}' registrada en '{campo_id}'")

    def _register_sensor_step2(self, campo_id, dev_id):
        dev_id = dev_id.strip()
        if not dev_id:
            self.show_msg("ID invalido")
            return
        if any(s.device_id == dev_id for s in self.state.sensors):
            self.show_msg(f"El sensor '{dev_id}' ya existe")
            return
        parcelas = self.state._load_spa_parcelas(campo_id)
        if not parcelas:
            self.start_input("ID de la parcela (no hay parcelas en SPA):", lambda p: self._register_sensor_final(campo_id, dev_id, p))
        else:
            self.view = "parcela_select"
            self.view_data = {
                "campo_id": campo_id,
                "parcelas": parcelas,
                "dev_id": dev_id,
            }

    def _register_sensor_final(self, campo_id, dev_id, parcela):
        parcela = parcela.strip()
        if not parcela:
            self.show_msg("Parcela invalida")
            return
        self.state.sensors.append(Sensor(device_id=dev_id, campo_id=campo_id, parcela_id=parcela))
        gws = self.state.gateways_del_campo(campo_id)
        if not gws:
            self.show_msg(f"⚠ Sensor '{dev_id}' registrado, pero '{campo_id}' no tiene gateways")
        else:
            self.show_msg(f"Sensor '{dev_id}' registrado en '{campo_id}', parcela '{parcela}'")
        self.state.save()

    def _delete_gw(self, campo_id):
        gws = self.state.gateways_del_campo(campo_id)
        if not gws:
            self.show_msg("No hay gateways en este campo")
            return
        self.view = "list_selection"
        self.view_data = {
            "type": "gateway",
            "campo_id": campo_id,
            "items": gws,
            "title": "Seleccione gateway a eliminar:",
            "prompt": "[0]  Cancelar",
        }

    def _delete_sensor(self, campo_id):
        sens = self.state.sensors_del_campo(campo_id)
        if not sens:
            self.show_msg("No hay sensores en este campo")
            return
        self.view = "list_selection"
        self.view_data = {
            "type": "sensor",
            "campo_id": campo_id,
            "items": sens,
            "title": "Seleccione sensor a eliminar:",
            "prompt": "[0]  Cancelar",
        }

    def _handle_list_key(self, key):
        if key == ord("0"):
            campo_id = self.state.campo_activo
            if campo_id:
                self.view = "campo_menu"
                self.view_data = {"campo_id": campo_id}
            else:
                self.view = "campo_select"
                self.view_data = {}

    def _handle_list_selection_key(self, key):
        ch = chr(key) if 48 <= key <= 57 else ""
        items = self.view_data.get("items", [])
        tipo = self.view_data.get("type", "")
        campo_id = self.view_data.get("campo_id", "")

        if ch == "0":
            self.view = "campo_menu"
            self.view_data = {"campo_id": campo_id}
        elif ch.isdigit():
            idx = int(ch) - 1
            if 0 <= idx < len(items):
                item = items[idx]
                if tipo == "gateway":
                    self.state.gateways.remove(item)
                    sin_cob = self.state.sensores_sin_cobertura()
                    sin_cob_campo = [s for s in sin_cob if s.campo_id == campo_id]
                    if sin_cob_campo:
                        self.show_msg(f"⚠ {len(sin_cob_campo)} sensor(es) perdieron cobertura")
                    else:
                        self.show_msg(f"Gateway '{item.gateway_id}' eliminada")
                elif tipo == "sensor":
                    self.state.sensors.remove(item)
                    self.show_msg(f"Sensor '{item.device_id}' eliminado")
                self.state.save()
                self.view = "campo_menu"
                self.view_data = {"campo_id": campo_id}

    def _handle_parcela_select_key(self, key):
        ch = chr(key) if 48 <= key <= 57 else ""
        campo_id = self.view_data.get("campo_id", "")
        parcelas = self.view_data.get("parcelas", [])
        dev_id = self.view_data.get("dev_id", "")

        if ch == "0":
            self.view = "campo_menu"
            self.view_data = {"campo_id": campo_id}
        elif ch.isdigit():
            idx = int(ch) - 1
            if 0 <= idx < len(parcelas):
                self._register_sensor_final(campo_id, dev_id, parcelas[idx])

    def _toggle_transmision(self):
        if self.state.transmitiendo:
            self.state.transmitiendo = False
            self.show_msg("Deteniendo transmision...")
        else:
            if not self.state.sensors:
                self.show_msg("No hay sensores registrados")
                return
            if not self.state.gateways:
                self.show_msg("No hay gateways registradas")
                return
            self.state.transmitiendo = True
            self.state.thread = threading.Thread(
                target=_loop_transmision, args=(self.state, self.log_queue), daemon=True
            )
            self.state.thread.start()
            self.show_msg("Transmision iniciada")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main(stdscr):
    app = App(stdscr)
    app.run()


if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass
