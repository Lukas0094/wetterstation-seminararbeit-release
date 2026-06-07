from flask import Flask, render_template, jsonify
from datetime import datetime, timedelta
import database
from sensors import raspberry_pi as pi
import config

app = Flask(__name__)

@app.route("/")
def index():
    """
    Gibt das Template zurück, was für die Website benutzt werden soll.
    """
    return render_template("index.html")

@app.route("/api/full_data")
def sendFullData():
    """
    Sendet alle Daten an das Frontend.
    """
    response = {
        "location": config.LOCATION,
        "latest": None,
        "past_hours": [],
        "past_days": [],
        "pi_info": None
    }

    latestDailyData = database.getDailyLatest()
    if latestDailyData:
        analysed = database.evaluateDailyFull(database.getDailyFull())
        response["latest"] = {
            "timestamp": datetime.fromtimestamp(latestDailyData[0], tz=config.TIMEZONE).strftime("%d.%m.%Y - %H:%M"),
            "temp": latestDailyData[1],
            "min_temp": analysed[0],
            "max_temp": analysed[1],
            "hum": latestDailyData[2],
            "min_hum": analysed[3],
            "max_hum": analysed[4],
            "pre": latestDailyData[3],
            "min_pre": analysed[6],
            "max_pre": analysed[7]
        }

    hourlyData = database.packDaily()
    if hourlyData:
        response["past_hours"] = [{
            "hour": hour,
            "temp": values[0],
            "hum": values[1],
            "pre": values[2]
        } for hour, values in hourlyData.items()]
            
    weeklyData = database.getWeeklyFull()
    if weeklyData:
        response["past_days"] = [{
            "date": (datetime.today().date() - datetime.strptime(day[0], "%Y-%m-%d").date()).days == 1 and "GESTERN" or ["MO", "DI", "MI", "DO", "FR", "SA", "SO"][datetime.strptime(day[0], "%Y-%m-%d").weekday()] + ".",
            "min_temp": day[1],
            "max_temp": day[2],
            "avg_temp": day[3],
            "min_hum": day[4],
            "max_hum": day[5],
            "avg_hum": day[6],
            "min_pre": day[7],
            "max_pre": day[8],
            "avg_pre": day[9]
        } for day in weeklyData]
            
    try:
        response["pi_info"] = {
            "cpu_temp": round(pi.getCPUTemp(), 1),
            "cpu_load": pi.getCPULoad(),
            "cpu_freq": pi.getCPUFreq(),
            "ram_used": pi.getRAMUsageMB(),
            "ram_total": pi.getRAMMaxMB(),
            "disk_used": pi.getDiskUsageMB(),
            "disk_total": pi.getDiskMaxMB(),
            "uptime": str(timedelta(seconds=pi.getUptime())).replace("days", "Tage").replace("day", "Tag")
        }
    except Exception:
        pass
        
    return jsonify(response)

if __name__ == "__main__":
    app.run(host="0.0.0.0")
