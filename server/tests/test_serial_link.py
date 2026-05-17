import sys
import os
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from serial_link import SerialLink, init_serial_link


def test_serial_link_simulation_mode():
    link = SerialLink(port=None)
    assert link._simulation_mode is True


def test_serial_link_start_stop():
    link = SerialLink(port=None)
    link.start()
    assert link._running is True
    assert link._thread is not None
    link.stop()
    assert link._running is False


def test_serial_link_power_reading():
    link = SerialLink(port=None)
    link.start()
    time.sleep(0.5)  # let simulation thread produce a reading
    power = link.get_power()
    assert power.harvested_mw >= 0.0
    link.stop()


def test_serial_link_radio_reading():
    link = SerialLink(port=None)
    link.start()
    time.sleep(0.5)
    radio = link.get_radio()
    assert radio.connected is False or radio.frequency_mhz > 0
    link.stop()


def test_serial_link_alerts_empty():
    link = SerialLink(port=None)
    link.start()
    alerts = link.get_alerts()
    assert isinstance(alerts, list)
    link.stop()


def test_serial_link_send_command_simulation():
    link = SerialLink(port=None)
    link.start()
    # In simulation mode, send_command just prints — should not raise
    link.send_command({"type": "cmd_gateway", "enabled": True})
    link.stop()


def test_init_serial_link_global():
    link = init_serial_link(port=None)
    assert link is not None
    from serial_link import get_link
    assert get_link() is link
    link.stop()
