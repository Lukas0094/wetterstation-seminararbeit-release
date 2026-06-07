import config
import smbus2
from bme280 import BME280
from time import sleep

bus = smbus2.SMBus(1)
sensor = BME280(i2c_dev=bus)

incorrectValue = None

def filterIncorrect() -> None:
    """
    Diese Funktion muss ausgeführt werden, bevor eigentliche Messungen durchgeführt werden können, weil\n
    die Bibliothek des BME280 fehlerhaft ist.\n
    INFO: Funktion löschen, wenn der Fehler behoben wurde.\n
    Terminiert sich selbst, falls die der Sensor schon korrigiert wurde.
    """
    if globals()["incorrectValue"] is not None: return
    incorrect = sensor.get_temperature()
    globals()["incorrectValue"] = incorrect
    while sensor.get_temperature() == incorrect:
        sleep(0.1)

def getTemperature() -> int:
    """
    Gibt die aktuelle Temperatur zurück, die vom BME280 gemessen wird.\n
    'filterIncorrect' muss vorher mindesten einmal ausgeführt werden.
    """
    return round(sensor.get_temperature())

def getHumidity() -> int:
    """
    Gibt die aktuelle Luftfeuchtigkeit zurück, die vom BME280 gemessen wird.\n
    'filterIncorrect' muss vorher mindesten einmal ausgeführt werden.
    """
    return round(sensor.get_humidity())

def getPressure() -> int:
    """
    Gibt den auf Meereshöhe umgerechneten, aktuellen Luftdruck zurück, der vom BME280 gemssen wird.\n
    Verwendet zur Umrechnung die Standardatmosphäre-Formel (basiert auf der internationalen Standardatmosphäre)\n
    Dabei gilt die Annahme, dass die Atmosphäre einem fest definierten Temperaturverlauf folgt.\n
    Zur richtigen Kalibrierung wird 'PRESSURE_OFFSET' dazuaddiert.\n
    'filterIncorrect' muss vorher mindesten einmal ausgeführt werden.
    """
    measuredPressure = sensor.get_pressure()
    seaLevelPressure = measuredPressure * pow((1 - config.LOCATION.get("height") / 44330), -5.255)

    return round(seaLevelPressure + config.PRESSURE_OFFSET)