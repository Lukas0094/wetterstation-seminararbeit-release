from zoneinfo import ZoneInfo

# Standort Konfiguration

"""Angaben für Anzeige- und Berechnungszwecke"""
LOCATION = {
    "country": "Deutschland",
    "sub-country": "Baden-Württemberg",
    "city": "Bohlsbach",
    "height": 158
}

"""Zeitzone auf der die App basiert"""
TIMEZONE = ZoneInfo("Europe/Berlin")

# App Konfiguration

"""Wird zum gemessenen Luftdruck dazuaddiert."""
PRESSURE_OFFSET = -2

"""Gibt an, ob die Daten von Tagen nach Sprüngen in der Datenbank angezeigt werden sollen"""
DISPLAY_NONE_CONSECUTIVE_WEEKLY_ENTRIES = False