import sqlite3
from sensors import bme280
from datetime import datetime, timedelta
from warnings import warn
import config

# Daily measurements database
# Speichert alle Wetterdaten des aktuellen Tages

DAILY_DB_PATH = "/home/wetterstation/wetterstation/databases/daily_data.db"

ddcon = sqlite3.connect(DAILY_DB_PATH)
ddcur = ddcon.cursor()
ddcur.execute("CREATE TABLE IF NOT EXISTS measurements(timestamp INTEGER PRIMARY KEY, temperature, humidity, pressure)")
ddcon.close()

def updateDaily() -> None:
    """
    Aktualisiert die Datenbank. Daten werden automatisch von den Sensoren angefragt.\n
    Falls ein neuer Tag erkannt wird, werden die vorhandenen Daten in die Datenbank für wöchentliche Messungen übertragen\n
    und aus dieser Datenbank gelöscht.
    """
    con = sqlite3.connect(DAILY_DB_PATH)
    cur = con.cursor()

    bme280.filterIncorrect()
    latestDayData = getDailyLatest()
    timezone = config.TIMEZONE
    fullDate = datetime.now(tz=timezone)
    timestamp = int(fullDate.timestamp())

    if latestDayData:
        if datetime.fromtimestamp(latestDayData[0], tz=timezone).date() != fullDate.date():
            updateWeekly()

    cur.execute("DELETE FROM measurements WHERE timestamp < ? AND timestamp < ?",
                (int((fullDate - timedelta(hours=12)).replace(minute=0, second=0).timestamp()),
                 int(fullDate.replace(hour=0, minute=0, second=0, microsecond=0).timestamp())))
    con.commit()

    if cur.execute("SELECT 1 FROM measurements WHERE timestamp = ?", (timestamp,)).fetchone():
        warn("Entry with timestamp already exists. Overwriting...")
    
    cur.execute("INSERT OR REPLACE INTO measurements (timestamp, temperature, humidity, pressure) VALUES (?, ?, ?, ?)",
                   (timestamp, bme280.getTemperature(), bme280.getHumidity(), bme280.getPressure()))
    con.commit()

    con.close()

def getDailyFull(keepBuffer: bool = False) -> list[tuple[int, int, int, int]]:
    """
    Gibt alle Wetterdaten zurück.\n
    Mit 'keepBuffer' werden auch die letzten 12 Stunden zurückgegeben unabhängig davon, ob diese am vorherigen Tag gesammelt wurden.
    """
    con = sqlite3.connect(DAILY_DB_PATH)
    cur = con.cursor()

    timezone = config.TIMEZONE

    data = cur.execute("SELECT * FROM measurements").fetchall()
    con.close()
    return keepBuffer and data or [t for t in data if datetime.fromtimestamp(t[0], tz=timezone).date() == datetime.fromtimestamp(data[len(data) - 1][0], tz=timezone).date()]

def getDailyLatest() -> tuple[int, int, int, int] | None:
    """
    Gibt die aktuellsten Wetterdaten aus der Datenbank zurück.\n
    Sind keine Daten vorhanden, wird 'None' zurückgegeben.
    """
    fullData = getDailyFull()
    try:
        return fullData[len(fullData) - 1]
    except IndexError:
        return

def clearDaily(insertIntoWeekly: bool = False) -> None:
    """
    Leert die Datenbank für die heutigen Wetterdaten.\n
    Mit 'insertIntoWeekly' werden die 'Daily-Database'-Daten in die 'Weekly-Database' übertragen.\n
    VERALTET: Funktion wird nicht mehr im normalen Lebenszyklus der Wetterstation benutzt.\n
    Manuelles Aufrufen kann unerwartetes Verhalten verursachen.
    """
    con = sqlite3.connect(DAILY_DB_PATH)
    cur = con.cursor()

    if insertIntoWeekly:
        updateWeekly()
    cur.execute("DELETE FROM measurements")
    con.commit()

    con.close()

def evaluateDailyFull(data: list) -> tuple[int, int, int, int, int, int, int, int, int]:
    """
    Gibt die/den durchschnittliche, minimale und maximale Temperatur, Luftfeuchtigkeit und Luftdruck zurück.\n
    Sind keine Daten vorhanden, wird 'None' zurückgegeben.
    """
    measurements = len(data)
    if measurements < 1: return
    
    zipped = tuple(zip(*data))

    avg_temp = round(sum(zipped[1]) / measurements)
    avg_hum = round(sum(zipped[2]) / measurements)
    avg_pre = round(sum(zipped[3]) / measurements)

    min_temp = min(zipped[1])
    min_hum = min(zipped[2])
    min_pre = min(zipped[3])

    max_temp = max(zipped[1])
    max_hum = max(zipped[2])
    max_pre = max(zipped[3])
    
    return min_temp, max_temp, avg_temp, min_hum, max_hum, avg_hum, min_pre, max_pre, avg_pre

def packDaily() -> dict[str, tuple[int, int, int]]:
    """
    Gruppiert die Wetterdaten der letzten 12 Stunden stundenweise, indem von jeder Stunde der Durchschnitt berechnet wird.
    """
    timezone = config.TIMEZONE
    pastTwelveFull = [t for t in getDailyFull(True) if t[0] >= (datetime.now(tz=timezone) - timedelta(hours=11)).replace(minute=0, second=0).timestamp()]
    pastTwelve = {}
    for dataset in pastTwelveFull:
        hour = str(datetime.fromtimestamp(dataset[0]).time())[:2]
        weather = dataset[1:4]
        if not hour in pastTwelve:
            pastTwelve.update({hour: list(weather) + [1]})
        else:
            for i in range(3):
                cset = pastTwelve[hour]
                cset[3] += 1
                cset[i] = int(cset[i] + (weather[i] - cset[i]) / cset[3])
    return pastTwelve

# Weekly measurements database
# Speichert alle Wetterdaten der letzten sieben Tage.

WEEKLY_DB_PATH = "/home/wetterstation/wetterstation/databases/weekly_data.db"

wdcon = sqlite3.connect(WEEKLY_DB_PATH)
wdcur = wdcon.cursor()
wdcur.execute("""CREATE TABLE IF NOT EXISTS measurements(
                      date TEXT PRIMARY KEY,
                      min_temp, max_temp, avg_temp,
                      min_hum, max_hum, avg_hum,
                      min_pre, max_pre, avg_pre)
                      """)
wdcon.close()

def updateWeekly() -> None:
    """
    Aktualisiert die Datenbank, indem der Durchschnitt und das Minimum und Maximum von den Wetterdaten des Tages berechnet wird.\n
    Ist bereits ein Eintrag mit dem gleichen Datum vorhanden, wird dieser Eintrag überschrieben.
    """
    con = sqlite3.connect(WEEKLY_DB_PATH)
    cur = con.cursor()

    timezone = config.TIMEZONE
    dayData = getDailyFull()
    min_temp, max_temp, avg_temp, min_hum, max_hum, avg_hum, min_pre, max_pre, avg_pre = evaluateDailyFull(dayData)

    day = str(datetime.fromtimestamp(dayData[0][0], tz=timezone).date())

    if cur.execute("SELECT 1 FROM measurements WHERE date = ?", (day,)).fetchone():
        warn("Entry with date already exists. Overwriting...")

    cur.execute("""INSERT OR REPLACE INTO measurements (
                          date,
                          min_temp, max_temp, avg_temp,
                          min_hum, max_hum, avg_hum,
                          min_pre, max_pre, avg_pre
                          )
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                          """,
                          (day, min_temp, max_temp, avg_temp, min_hum, max_hum, avg_hum, min_pre, max_pre, avg_pre))
    con.commit()
    
    for t in getWeeklyFull():
        if (datetime.today() - datetime.strptime(t[0], "%Y-%m-%d")).days >= 8:
            cur.execute("DELETE FROM measurements WHERE date = ?", (t[0],))
            con.commit()
    
    con.close()

def getWeeklyFull() -> list[tuple[str, int, int, int, int, int, int, int, int, int]]:
    """
    Gibt alle Daten zurück.
    """
    con = sqlite3.connect(WEEKLY_DB_PATH)
    cur = con.cursor()

    fullData = cur.execute("SELECT * FROM measurements").fetchall()
    con.close()

    if not config.DISPLAY_NONE_CONSECUTIVE_WEEKLY_ENTRIES:
        for i in range(len(fullData) - 1, 0, -1):
            if (datetime.strptime(fullData[i][0], "%Y-%m-%d") - datetime.strptime(fullData[i - 1][0], "%Y-%m-%d")).days != 1:
                return fullData[i:]

    return fullData

def getWeeklyLatest() -> tuple[str, int, int, int, int, int, int, int, int, int] | None:
    """
    Gibt den neusten Eintrag in der 'Weekly-Database' zurück.\n
    Sind keine Daten vorhanden, wird 'None' zurückgegeben.
    """
    fullData = getWeeklyFull()
    try:
        return fullData[len(fullData) - 1]
    except IndexError:
        return

# Crontab Funktionalität

if __name__ == "__main__":
    updateDaily()
