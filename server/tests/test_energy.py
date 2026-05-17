import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from energy import get_power_mode, has_surplus_bandwidth, read_harvested_power_mw, PowerMode


def test_power_mode_full():
    assert get_power_mode(600.0) == PowerMode.FULL


def test_power_mode_reduced():
    assert get_power_mode(200.0) == PowerMode.REDUCED


def test_power_mode_low():
    assert get_power_mode(50.0) == PowerMode.LOW_POWER


def test_power_mode_sleep():
    assert get_power_mode(5.0) == PowerMode.SLEEP


def test_power_mode_boundary_full():
    assert get_power_mode(500.0) == PowerMode.FULL


def test_power_mode_boundary_reduced():
    assert get_power_mode(100.0) == PowerMode.REDUCED


def test_power_mode_boundary_low():
    assert get_power_mode(10.0) == PowerMode.LOW_POWER


def test_has_surplus_bandwidth():
    assert has_surplus_bandwidth() is True


def test_read_harvested_power_dev_mode():
    # In dev mode (no I2C hardware), should return 0.0
    power = read_harvested_power_mw()
    assert isinstance(power, float)
    assert power >= 0.0
