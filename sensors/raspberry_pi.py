import psutil
from time import time

# CPU info

def getCPUTemp() -> int | None:
    """
    Gibt die aktuelle CPU-Temperatur zurück in Grad Celsius.\n
    Schlägt die Anfrage fehl, wird 'None' zurückgegeben.
    """
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as file:
            return round(int(file.read()) / 1000)
    except FileNotFoundError:
        return None

def getCPULoad() -> float:
    """Gibt die aktuelle CPU-Auslastung in Prozenz zurück."""
    return psutil.cpu_percent(interval=1)

def getCPUFreq() -> int:
    """Gibt die aktuelle CPU-Frequenz in Mhz zurück."""
    return int(psutil.cpu_freq().current)

# Memory info

def getRAMUsagePercent() -> float:
    """Gibt die aktuelle RAM-Nutzung in Prozent zurück."""
    return psutil.virtual_memory().percent

def getRAMUsageMB() -> int:
    """Gibt die aktuelle RAM-Nutzung in GB zurück."""
    return round(psutil.virtual_memory().used / (1024 ** 3), 1)

def getRAMMaxMB() -> int:
    """Gibt den maximal verfügbaren RAM des Micro-Controllers in GB zurück."""
    return round(psutil.virtual_memory().total / (1024 ** 3), 1)

# Disk info

def getDiskUsageMB() -> int:
    """Gibt zurück, wie viel Festplattenspeicher genutzt wird in GB."""
    return round(psutil.disk_usage(path="/").used / (1024 ** 3), 1)

def getDiskMaxMB() -> int:
    """Gibt den maximal verfügbaren Festplattenspeicher des Micro-Controllers zurück in GB."""
    return round(psutil.disk_usage(path="/").total / (1024 ** 3), 1)

# Other

def getUptime() -> int:
    """Gibt die vergangene Zeit seit dem Start des Micro-Controllers zurück in Sekunden."""
    return round(time() - psutil.boot_time())