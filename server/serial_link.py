"""
Serial Link — Python bridge to C++ firmware over UART.
Reads JSON messages, exposes sensor data to Python stack.
"""

import json
import logging
import threading
import time
from typing import Optional
from dataclasses import dataclass, field
from collections import deque

logger = logging.getLogger(__name__)


@dataclass
class PowerReading:
    harvested_mw: float = 0.0
    battery_v: float = 0.0
    mode: str = "FullOperation"
    timestamp: float = field(default_factory=time.time)


@dataclass
class RadioReading:
    connected: bool = False
    frequency_mhz: float = 0.0
    rssi_dbm: float = -100.0
    timestamp: float = field(default_factory=time.time)


class SerialLink:
    """Thread-safe serial link to C++ firmware."""

    def __init__(self, port: Optional[str] = None, baud: int = 115200):
        self._port = port
        self._baud = baud
        self._serial = None
        self._thread: Optional[threading.Thread] = None
        self._running = False
        self._lock = threading.Lock()
        self._power = PowerReading()
        self._radio = RadioReading()
        self._alerts: deque[dict] = deque(maxlen=10)
        self._simulation_mode = port is None
        self.firmware_ready = False

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        if self._simulation_mode:
            logger.info("Starting serial link in simulation mode")
            self._thread = threading.Thread(target=self._simulate_loop, daemon=True)
        else:
            try:
                import serial
                self._serial = serial.Serial(self._port, self._baud, timeout=0.1)
                logger.info(f"Starting serial link on {self._port} at {self._baud} baud")
                self._thread = threading.Thread(target=self._read_loop, daemon=True)
            except Exception as e:
                logger.warning(f"Could not open {self._port}: {e}, falling back to simulation")
                self._simulation_mode = True
                self._thread = threading.Thread(target=self._simulate_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        logger.info("Stopping serial link")
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)
        if self._serial:
            self._serial.close()

    def get_power(self) -> PowerReading:
        with self._lock:
            return PowerReading(self._power.harvested_mw, self._power.battery_v,
                                self._power.mode, self._power.timestamp)

    def get_radio(self) -> RadioReading:
        with self._lock:
            return RadioReading(self._radio.connected, self._radio.frequency_mhz,
                                self._radio.rssi_dbm, self._radio.timestamp)

    def get_alerts(self) -> list[dict]:
        with self._lock:
            return list(self._alerts)

    def send_command(self, cmd: dict) -> None:
        line = json.dumps(cmd) + "\n"
        if self._serial:
            self._serial.write(line.encode())
            logger.debug(f"TX to firmware: {cmd}")
        else:
            logger.debug(f"Sim TX to firmware: {cmd}")

    def _handle_message(self, msg: dict) -> None:
        mtype = msg.get("type", "")
        with self._lock:
            if mtype == "power":
                self._power = PowerReading(
                    msg.get("harvested_mw", 0.0),
                    msg.get("battery_v", 0.0),
                    msg.get("mode", "FullOperation"),
                )
                logger.debug(f"RX power: {msg}")
            elif mtype == "radio":
                self._radio = RadioReading(
                    msg.get("tvws_connected", False),
                    msg.get("frequency_mhz", 0.0),
                    msg.get("rssi_dbm", -100.0),
                )
                logger.debug(f"RX radio: {msg}")
            elif mtype == "alert":
                self._alerts.append(msg)
                logger.warning(f"RX alert: {msg}")
            elif mtype == "ready":
                self.firmware_ready = True
                logger.info(f"RX ready: {msg.get('firmware_version', 'unknown')}")
            else:
                logger.warning(f"Unknown message type: {mtype}")

    def _read_loop(self) -> None:
        buf = b""
        while self._running:
            try:
                if self._serial and self._serial.in_waiting:
                    buf += self._serial.read(self._serial.in_waiting)
                    while b"\n" in buf:
                        line, buf = buf.split(b"\n", 1)
                        try:
                            msg = json.loads(line.decode().strip())
                            self._handle_message(msg)
                        except json.JSONDecodeError:
                            logger.warning(f"Failed to parse JSON: {line[:50]}")
                time.sleep(0.01)
            except Exception as e:
                logger.error(f"Serial read error: {e}", exc_info=True)
                time.sleep(1)

    def _simulate_loop(self) -> None:
        """Simulate firmware messages for development."""
        t0 = time.time()
        logger.info("Starting simulation loop")
        while self._running:
            t = time.time() - t0
            # Simulated power: cycles 0-600mW over ~5min
            power = max(0.0, 300.0 + 300.0 * __import__("math").sin(t * 0.02))
            mode = "FullOperation" if power >= 500 else "Reduced" if power >= 100 else "LowPower" if power >= 10 else "Sleep"
            self._handle_message({
                "type": "power",
                "harvested_mw": round(power, 2),
                "battery_v": 3.7,
                "mode": mode,
            })
            if int(t) % 10 == 0:
                self._handle_message({
                    "type": "radio",
                    "tvws_connected": True,
                    "frequency_mhz": 574.0,
                    "rssi_dbm": -65.0,
                })
            time.sleep(5.0)


# Global instance — imported by energy.py, api.py, main.py
_link: Optional[SerialLink] = None


def init_serial_link(port: Optional[str] = None) -> SerialLink:
    """Initialize and start the serial link. Call once at boot."""
    global _link
    _link = SerialLink(port=port)
    _link.start()
    return _link


def get_link() -> Optional[SerialLink]:
    return _link
