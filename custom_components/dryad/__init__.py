import os
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN, PLATFORMS, STORAGE_DIR, DB_NAME
from .database import DryadDatabase
from .api import DryadSyncView, DryadPhotoView, DryadExportView

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Dryad from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    # Setup database
    db_path = hass.config.path(STORAGE_DIR, DB_NAME)
    db = await hass.async_add_executor_job(DryadDatabase, hass, db_path)
    hass.data[DOMAIN]["db"] = db

    # Setup media directory for photos
    media_dir = hass.config.path("media", DOMAIN)
    def make_media_dir():
        os.makedirs(media_dir, exist_ok=True)
    await hass.async_add_executor_job(make_media_dir)

    # Register API endpoints
    hass.http.register_view(DryadSyncView(db))
    hass.http.register_view(DryadPhotoView(media_dir))
    hass.http.register_view(DryadExportView(db))

    # Load platforms (Sensors, Image)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register HA Services
    async def handle_add_log(call):
        plant_id = call.data.get("plant_id")
        water_amount = call.data.get("water_amount")
        feed_type = call.data.get("feed_type")
        notes = call.data.get("notes")
        # Logic to insert log into DB goes here
        _LOGGER.info(f"Dryad service add_log called for {plant_id}")
    
    hass.services.async_register(DOMAIN, "add_log", handle_add_log)
    hass.services.async_register(DOMAIN, "quick_water", handle_add_log)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok
