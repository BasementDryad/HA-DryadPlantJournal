import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from .const import DOMAIN, SIGNAL_DRYAD_UPDATE

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the Dryad sensors."""
    db = hass.data[DOMAIN]["db"]

    async def async_update_sensors():
        plants = await hass.async_add_executor_job(db.get_all_plants_with_latest_log)
        entities = []
        for plant in plants:
            latest_log = plant.get('latest_log') or {}
            
            # The keys here must match what is stored in the SQLite database columns!
            sensor_values = {
                "temperature": latest_log.get('temperature'),
                "humidity": latest_log.get('humidity'),
                "vpd_leaf": latest_log.get('vpd_leaf'),
                "vpd_ambient": latest_log.get('vpd_ambient'),
                "co2": latest_log.get('co2'),
                "par": latest_log.get('par'),
                "dli": latest_log.get('dli'),
                "water_amount": latest_log.get('waterAmount'),
                "feed_strength": latest_log.get('feedStrengthPercentage'),
                "vibe": latest_log.get('vibe'),
                "stage": plant.get('stage'),
                "notes": latest_log.get('notes')
            }

            for metric, name, icon, unit in [
                ("temperature", "Temperature", "mdi:thermometer", "°F"),
                ("humidity", "Humidity", "mdi:water-percent", "%"),
                ("vpd_leaf", "VPD Leaf", "mdi:leaf", "kPa"),
                ("vpd_ambient", "VPD Ambient", "mdi:air-filter", "kPa"),
                ("co2", "CO2", "mdi:molecule-co2", "ppm"),
                ("par", "PAR", "mdi:white-balance-sunny", "µmol/m²/s"),
                ("dli", "DLI", "mdi:theme-light-dark", "mol/m²/d"),
                # Removed unit for water_amount because Android sends it as a String (e.g. "6 L")
                ("water_amount", "Water Amount", "mdi:water-pump", None),
                ("feed_strength", "Feed Strength", "mdi:flask", "%"),
                ("vibe", "Vibe Rating", "mdi:star", "Stars"),
                ("stage", "Stage", "mdi:sprout", None),
                ("notes", "Latest Notes", "mdi:notebook", None)
            ]:
                entities.append(DryadSensor(plant, metric, name, sensor_values[metric], icon, unit))

        async_add_entities(entities, True)

    # Initial load
    await async_update_sensors()

    # Listen for updates
    async_dispatcher_connect(hass, SIGNAL_DRYAD_UPDATE, async_update_sensors)

class DryadSensor(SensorEntity):
    def __init__(self, plant, metric, name, state, icon, unit):
        self.plant = plant
        self.metric = metric
        self._attr_name = f"{plant['name']} {name}"
        self._attr_unique_id = f"dryad_{plant['id']}_{metric}"
        self._state = state
        self._attr_icon = icon
        self._attr_native_unit_of_measurement = unit

    @property
    def native_value(self):
        return self._state

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.plant["id"])},
            "name": self.plant["name"],
            "manufacturer": "Dryad Plant Journal",
            "model": self.plant.get("genetics", "Unknown Genetics")
        }
