"""
Test the serial protocol message format that the C++ firmware produces.
These tests verify that our Python parser correctly handles messages
from the embedded firmware layer.
"""

import sys
import os
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from serial_link import SerialLink


def test_parse_power_message():
    raw = '{"type":"power","harvested_mw":150.5,"battery_v":3.7,"mode":"Reduced"}'
    msg = json.loads(raw)
    assert msg["type"] == "power"
    assert msg["harvested_mw"] == 150.5
    assert msg["battery_v"] == 3.7
    assert msg["mode"] == "Reduced"


def test_parse_radio_message():
    raw = '{"type":"radio","tvws_connected":true,"frequency_mhz":574.0,"bandwidth_mhz":6.0,"rssi_dbm":-65.0}'
    msg = json.loads(raw)
    assert msg["type"] == "radio"
    assert msg["tvws_connected"] is True
    assert msg["frequency_mhz"] == 574.0
    assert msg["rssi_dbm"] == -65.0


def test_parse_heartbeat_message():
    raw = '{"type":"heartbeat","uptime_sec":3600,"neighbors":3}'
    msg = json.loads(raw)
    assert msg["type"] == "heartbeat"
    assert msg["uptime_sec"] == 3600
    assert msg["neighbors"] == 3


def test_parse_alert_message():
    raw = '{"type":"alert","code":"LOW_POWER","message":"Entering sleep mode"}'
    msg = json.loads(raw)
    assert msg["type"] == "alert"
    assert msg["code"] == "LOW_POWER"
    assert msg["message"] == "Entering sleep mode"


def test_parse_ready_message():
    raw = '{"type":"ready","firmware_version":"0.1.0","hardware":"esp32s3","power_ic":"AEM10941","radio":"TVWS"}'
    msg = json.loads(raw)
    assert msg["type"] == "ready"
    assert msg["firmware_version"] == "0.1.0"
    assert msg["hardware"] == "esp32s3"


def test_parse_gateway_command():
    raw = '{"type":"cmd_gateway","enabled":true}'
    msg = json.loads(raw)
    assert msg["type"] == "cmd_gateway"
    assert msg["enabled"] is True


def test_parse_power_command():
    raw = '{"type":"cmd_power","mode":"FullOperation"}'
    msg = json.loads(raw)
    assert msg["type"] == "cmd_power"
    assert msg["mode"] == "FullOperation"


def test_link_handles_power_message():
    link = SerialLink(port=None)
    link._handle_message({
        "type": "power",
        "harvested_mw": 200.0,
        "battery_v": 3.8,
        "mode": "FullOperation",
    })
    reading = link.get_power()
    assert reading.harvested_mw == 200.0
    assert reading.battery_v == 3.8
    assert reading.mode == "FullOperation"


def test_link_handles_radio_message():
    link = SerialLink(port=None)
    link._handle_message({
        "type": "radio",
        "tvws_connected": True,
        "frequency_mhz": 574.0,
        "rssi_dbm": -65.0,
    })
    reading = link.get_radio()
    assert reading.connected is True
    assert reading.frequency_mhz == 574.0
    assert reading.rssi_dbm == -65.0


def test_link_handles_alert_message():
    link = SerialLink(port=None)
    link._handle_message({
        "type": "alert",
        "code": "LOW_POWER",
        "message": "Entering sleep",
    })
    alerts = link.get_alerts()
    assert len(alerts) == 1
    assert alerts[0]["code"] == "LOW_POWER"


def test_link_handles_ready_message():
    link = SerialLink(port=None)
    link._handle_message({
        "type": "ready",
        "firmware_version": "0.1.0",
    })
    assert link.firmware_ready is True
