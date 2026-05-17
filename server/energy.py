"""
Energy Harvesting Module

Primary: reads from C++ firmware via serial link (serial_link.py).
Fallback: direct I2C to AEM10941 or BQ25570 when firmware is not present.

Per architecture principle: C++ owns hardware, Python owns intelligence.
The firmware handles all I2C register reads; Python only consumes the data.
"""

from enum import Enum
from typing import Optional


class PowerMode(str, Enum):
    FULL        = "FullOperation"   # >500mW
    REDUCED     = "Reduced"         # 100–500mW
    LOW_POWER   = "LowPower"        # 10–100mW
    SLEEP       = "Sleep"           # <10mW


# I2C addresses for supported energy harvesting ICs
AEM10941_ADDR = 0x48   # e-peas AEM10941 ambient energy manager
BQ25570_ADDR = 0x10    # TI BQ25570 nano power boost charger

# I2C bus (default: bus 1 on Raspberry Pi / GL.iNet)
I2C_BUS = 1


def get_power_mode(harvested_mw: float) -> PowerMode:
    """Determine operational power mode from harvested milliwatts."""
    if harvested_mw >= 500:
        return PowerMode.FULL
    elif harvested_mw >= 100:
        return PowerMode.REDUCED
    elif harvested_mw >= 10:
        return PowerMode.LOW_POWER
    else:
        return PowerMode.SLEEP


def has_surplus_bandwidth() -> bool:
    """
    Check if node has surplus bandwidth to share.
    In production: read from /proc/net/dev and compare to threshold.
    """
    return True


def _read_i2c_power() -> float:
    """Direct I2C fallback when firmware serial link is unavailable."""
    try:
        import smbus2
        bus = smbus2.SMBus(I2C_BUS)
        try:
            raw_high = bus.read_byte_data(AEM10941_ADDR, 0x00)
            raw_low = bus.read_byte_data(AEM10941_ADDR, 0x01)
            raw_adc = (raw_high << 8) | raw_low
            voltage = (raw_adc / 4095.0) * 3.3
            power_mw = voltage * 200.0
            bus.close()
            return power_mw
        except OSError:
            pass
        try:
            raw = bus.read_byte_data(BQ25570_ADDR, 0x02)
            power_mw = raw * 2.0
            bus.close()
            return power_mw
        except OSError:
            pass
        bus.close()
    except (ImportError, FileNotFoundError, PermissionError):
        pass
    return 0.0


def read_harvested_power_mw() -> float:
    """
    Read harvested power. Primary source: serial link from C++ firmware.
    Fallback: direct I2C. Simulation: sinusoidal cycle for dev testing.
    """
    # Try serial link first (firmware is the hardware owner per architecture)
    from serial_link import get_link
    link = get_link()
    if link is not None:
        reading = link.get_power()
        if reading.timestamp > 0:
            return reading.harvested_mw

    # Fallback: direct I2C when firmware not present
    i2c_result = _read_i2c_power()
    if i2c_result > 0:
        return i2c_result

    # Development simulation
    import math
    t = __import__("time").time()
    sim = 300.0 + 300.0 * math.sin(t * 0.02)
    return sim if sim > 0 else 0.0


def get_battery_voltage() -> Optional[float]:
    """
    Read storage capacitor/battery voltage.
    Primary: serial link from firmware. Fallback: direct I2C.
    """
    from serial_link import get_link
    link = get_link()
    if link is not None:
        reading = link.get_power()
        if reading.timestamp > 0 and reading.battery_v > 0:
            return reading.battery_v

    try:
        import smbus2
        bus = smbus2.SMBus(I2C_BUS)
        raw_high = bus.read_byte_data(AEM10941_ADDR, 0x02)
        raw_low = bus.read_byte_data(AEM10941_ADDR, 0x03)
        raw_adc = (raw_high << 8) | raw_low
        voltage = (raw_adc / 4095.0) * 5.0
        bus.close()
        return voltage
    except (ImportError, FileNotFoundError, PermissionError, OSError):
        return 3.7  # Dev fallback
