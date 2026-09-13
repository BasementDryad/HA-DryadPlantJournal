DOMAIN = "dryad"
PLATFORMS = ["sensor", "image"]

API_SYNC_ENDPOINT = "/api/dryad/sync"
API_PHOTO_ENDPOINT = "/api/dryad/photo"
API_EXPORT_ENDPOINT = "/api/dryad/export"

SIGNAL_DRYAD_UPDATE = "dryad_update_signal"
SIGNAL_NEW_PLANT = "dryad_new_plant_signal"

STORAGE_DIR = "dryad"
DB_NAME = "dryad.sqlite"

# Sensor definitions mapping internal keys to display names and units
SENSOR_TYPES = {
    "temperature": {"name": "Temperature", "unit": "°F", "icon": "mdi:thermometer", "class": "temperature"},
    "humidity": {"name": "Humidity", "unit": "%", "icon": "mdi:water-percent", "class": "humidity"},
    "vpd_leaf": {"name": "VPD Leaf", "unit": "kPa", "icon": "mdi:leaf", "class": "pressure"},
    "vpd_ambient": {"name": "VPD Ambient", "unit": "kPa", "icon": "mdi:weather-windy", "class": "pressure"},
    "co2": {"name": "CO2", "unit": "ppm", "icon": "mdi:molecule-co2", "class": "carbon_dioxide"},
    "par": {"name": "PAR", "unit": "µmol/m²/s", "icon": "mdi:white-balance-sunny", "class": "illuminance"},
    "dli": {"name": "DLI", "unit": "mol/m²/d", "icon": "mdi:sun-clock", "class": "illuminance"},
    "water_amount": {"name": "Water Amount", "unit": "L", "icon": "mdi:watering-can", "class": "volume"},
    "feed_strength": {"name": "Feed Strength", "unit": "%", "icon": "mdi:flask", "class": None},
    "vibe": {"name": "Vibe Rating", "unit": "Stars", "icon": "mdi:star", "class": None},
    "stage": {"name": "Stage", "unit": None, "icon": "mdi:sprout", "class": None},
    "cycle_days": {"name": "Cycle Days", "unit": "days", "icon": "mdi:calendar-clock", "class": None},
    "notes": {"name": "Latest Notes", "unit": None, "icon": "mdi:notebook", "class": None}
}
