"""
Energy Harvesting Module
Interfaces with power management ICs (AEM10941 or BQ25570) via I2C
to monitor harvested ambient energy (RF, solar, thermal).
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


def read_harvested_power_mw() -> float:
    """
    Read harvested power from energy management IC via I2C.
    
    Supports:
    - e-peas AEM10941: Multi-source ambient energy manager
    - TI BQ25570: Ultra-low power harvester with boost charger
    
    Returns harvested power in milliwatts.
    In development mode: returns simulated value.
    """
    try:
        import smbus2
        bus = smbus2.SMBus(I2C_BUS)
        # Try AEM10941 first
        try:
            raw_high = bus.read_byte_data(AEM10941_ADDR, 0x00)
            raw_low = bus.read_byte_data(AEM10941_ADDR, 0x01)
            raw_adc = (raw_high << 8) | raw_low
            # Convert 12-bit ADC reading to milliwatts
            # AEM10941 outputs 0-3.3V proportional to harvested power
            voltage = (raw_adc / 4095.0) * 3.3
            power_mw = voltage * 200.0  # Scale factor for power measurement
            bus.close()
            return power_mw
        except OSError:
            pass

        # Fallback to BQ25570
        try:
            raw = bus.read_byte_data(BQ25570_ADDR, 0x02)
            power_mw = raw * 2.0  # BQ25570 resolution ~2mW per LSB
            bus.close()
            return power_mw
        except OSError:
            pass

        bus.close()
    except (ImportError, FileNotFoundError, PermissionError):
        # smbus2 not available or I2C bus not present (dev environment)
        pass

    # Development fallback: simulate solar panel output
    return 0.0


def get_battery_voltage() -> Optional[float]:
    """
    Read storage capacitor/battery voltage.
    Returns voltage in V, or None if hardware not available.
    """
    try:
        import smbus2
        bus = smbus2.SMBus(I2C_BUS)
        raw_high = bus.read_byte_data(AEM10941_ADDR, 0x02)
        raw_low = bus.read_byte_data(AEM10941_ADDR, 0x03)
        raw_adc = (raw_high << 8) | raw_low
        voltage = (raw_adc / 4095.0) * 5.0  # 0-5V range
        bus.close()
        return voltage
    except (ImportError, FileNotFoundError, PermissionError, OSError):
        return None
