import os
import glob
from homeassistant.components.image import ImageEntity
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import DeviceInfo
from .const import DOMAIN, SIGNAL_DRYAD_UPDATE
import homeassistant.util.dt as dt_util

async def async_setup_entry(hass, entry, async_add_entities):
    db = hass.data[DOMAIN]["db"]
    media_dir = hass.config.path("media", DOMAIN)
    added_entities = set()

    async def async_update_images():
        plants = await hass.async_add_executor_job(db.get_all_plants_with_latest_log)
        new_entities = []
        for plant in plants:
            plant_id = plant['id']
            entity_id = f"image.dryad_{plant_id}_photo"
            if entity_id not in added_entities:
                img = DryadImage(hass, plant, media_dir)
                new_entities.append(img)
                added_entities.add(entity_id)

        if new_entities:
            async_add_entities(new_entities)

    entry.async_on_unload(
        async_dispatcher_connect(hass, SIGNAL_DRYAD_UPDATE, async_update_images)
    )
    await async_update_images()

class DryadImage(ImageEntity):
    def __init__(self, hass, plant, media_dir):
        super().__init__(hass)
        self.plant = plant
        self.media_dir = media_dir
        self._attr_unique_id = f"dryad_{plant['id']}_photo"
        self._attr_name = f"{plant['name']} Photo"
        self._last_image_path = None

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self.plant['id'])},
            name=self.plant['name']
        )

    async def async_image(self):
        """Return bytes of image."""
        plant_dir = os.path.join(self.media_dir, self.plant['id'])
        if os.path.exists(plant_dir):
            # Find the most recent photo
            files = glob.glob(f"{plant_dir}/*.jpg")
            if files:
                latest_file = max(files, key=os.path.getctime)
                if self._last_image_path != latest_file:
                    self._last_image_path = latest_file
                    self._attr_image_last_updated = dt_util.utcnow()
                
                def _read_img():
                    with open(latest_file, "rb") as f:
                        return f.read()
                return await self.hass.async_add_executor_job(_read_img)
        return None

    async def async_added_to_hass(self):
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass, SIGNAL_DRYAD_UPDATE, self.async_write_ha_state
            )
        )
