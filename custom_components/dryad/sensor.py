import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import DeviceInfo
from .const import DOMAIN, SENSOR_TYPES, SIGNAL_DRYAD_UPDATE

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the Dryad sensors dynamically."""
    db = hass.data[DOMAIN]["db"]
    added_entities = set()

    async def async_update_sensors():
        plants = await hass.async_add_executor_job(db.get_all_plants_with_latest_log)
        new_entities = []

        for plant in plants:
            plant_id = plant['id']
            latest_log = plant.get('latest_log') or {}
            
            # Map database keys to sensor types
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

            for sensor_key, value in sensor_values.items():
                if value is not None:
                    entity_id = f"sensor.dryad_{plant_id}_{sensor_key}"
                    if entity_id not in added_entities:
                        sensor = DryadSensor(plant, sensor_key, value)
                        new_entities.append(sensor)
                        added_entities.add(entity_id)

        if new_entities:
            async_add_entities(new_entities)

    # Listen for sync updates to dynamically create/update sensors
    entry.async_on_unload(
        async_dispatcher_connect(hass, SIGNAL_DRYAD_UPDATE, async_update_sensors)
    )
    
    # Run once on startup
    await async_update_sensors()

class DryadSensor(SensorEntity):
    def __init__(self, plant, sensor_key, state):
        self.plant = plant
        self.sensor_key = sensor_key
        self._attr_native_value = state
        self._attr_unique_id = f"dryad_{plant['id']}_{sensor_key}"
        self._attr_name = f"{plant['name']} {SENSOR_TYPES[sensor_key]['name']}"
        self._attr_icon = SENSOR_TYPES[sensor_key]['icon']
        self._attr_native_unit_of_measurement = SENSOR_TYPES[sensor_key]['unit']
        self._attr_device_class = SENSOR_TYPES[sensor_key]['class']

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self.plant['id'])},
            name=self.plant['name'],
            manufacturer="Dryad Plant Journal",
            model=f"{self.plant['genetics']} ({self.plant['type']})",
        )

    async def async_added_to_hass(self):
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass, SIGNAL_DRYAD_UPDATE, self._update_callback
            )
        )

    async def _update_callback(self):
        db = self.hass.data[DOMAIN]["db"]
        plants = await self.hass.async_add_executor_job(db.get_all_plants_with_latest_log)
        for p in plants:
            if p['id'] == self.plant['id']:
                latest = p.get('latest_log') or {}
                if self.sensor_key == "stage":
                    self._attr_native_value = p.get('stage')
                else:
                    self._attr_native_value = latest.get(self.sensor_key)
                self.async_write_ha_state()
