from enum import Enum

class PowerMode(str, Enum):
    FULL        = "FullOperation"   # >500mW
    REDUCED     = "Reduced"         # 100–500mW
    LOW_POWER   = "LowPower"        # 10–100mW
    SLEEP       = "Sleep"           # <10mW

def get_power_mode(harvested_mw: float) -> PowerMode:
    if harvested_mw >= 500:
        return PowerMode.FULL
    elif harvested_mw >= 100:
        return PowerMode.REDUCED
    elif harvested_mw >= 10:
        return PowerMode.LOW_POWER
    else:
        return PowerMode.SLEEP

def has_surplus_bandwidth() -> bool:
    # In production: read from /proc/net/dev and compare to threshold
    return True

def read_harvested_power_mw() -> float:
    # In production: read ADC from AEM10941 or BQ25570 IC via smbus2 (I2C)
    # import smbus2; bus = smbus2.SMBus(1); return bus.read_byte_data(0x48, 0x00)
    return 0.0
