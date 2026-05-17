import sys
import os
import asyncio
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tvws import TVWSRadio, TVWSConfig, TVWSChannel, init_tvws, get_backhaul_status, connect_backhaul


def test_tvws_radio_init():
    radio = TVWSRadio()
    assert radio.is_connected is False
    assert radio.active_channel is None


def test_tvws_radio_initialize():
    radio = TVWSRadio()
    result = asyncio.run(radio.initialize())
    assert result is True
    assert radio.is_connected is True


def test_tvws_scan_channels():
    radio = TVWSRadio()
    asyncio.run(radio.initialize())
    channels = asyncio.run(radio.scan_channels())
    assert isinstance(channels, list)
    assert len(channels) > 0
    for ch in channels:
        assert isinstance(ch, TVWSChannel)
        assert ch.frequency_mhz >= 470.0
        assert ch.frequency_mhz <= 698.0


def test_tvws_select_best_channel():
    radio = TVWSRadio()
    asyncio.run(radio.initialize())
    channel = asyncio.run(radio.select_best_channel())
    assert channel is not None
    assert channel.occupied is False
    assert channel.snr_db > 10.0


def test_tvws_connect():
    radio = TVWSRadio()
    asyncio.run(radio.initialize())
    result = asyncio.run(radio.connect())
    assert result is True
    assert radio.active_channel is not None


def test_tvws_disconnect():
    radio = TVWSRadio()
    asyncio.run(radio.initialize())
    asyncio.run(radio.connect())
    asyncio.run(radio.disconnect())
    assert radio.is_connected is False
    assert radio.active_channel is None


def test_tvws_link_quality_disconnected():
    radio = TVWSRadio()
    quality = asyncio.run(radio.get_link_quality())
    assert quality["connected"] is False


def test_tvws_link_quality_connected():
    radio = TVWSRadio()
    asyncio.run(radio.initialize())
    asyncio.run(radio.connect())
    quality = asyncio.run(radio.get_link_quality())
    assert quality["connected"] is True
    assert quality["throughput_mbps"] > 0


def test_module_level_init():
    result = asyncio.run(init_tvws())
    assert result is True


def test_module_backhaul_status():
    status = asyncio.run(get_backhaul_status())
    assert "connected" in status


def test_module_connect_backhaul():
    result = asyncio.run(connect_backhaul())
    assert result is True
