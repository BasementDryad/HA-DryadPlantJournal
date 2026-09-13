import logging
import os
import time
from aiohttp import web
from homeassistant.components.http import HomeAssistantView
from homeassistant.helpers.dispatcher import async_dispatcher_send
from .const import DOMAIN, API_SYNC_ENDPOINT, API_PHOTO_ENDPOINT, API_EXPORT_ENDPOINT, SIGNAL_DRYAD_UPDATE, SIGNAL_NEW_PLANT

_LOGGER = logging.getLogger(__name__)

class DryadSyncView(HomeAssistantView):
    url = API_SYNC_ENDPOINT
    name = "api:dryad:sync"
    requires_auth = True

    def __init__(self, db):
        self.db = db

    async def post(self, request):
        hass = request.app["hass"]
        data = await request.json()

        # Update SQLite DB via executor job
        def _update_db():
            plants = data.get("plants", [])
            logs = data.get("logs", [])
            for plant in plants:
                self.db.upsert_plant(plant)
            for log in logs:
                self.db.upsert_log(log)
            return len(plants), len(logs)

        num_plants, num_logs = await hass.async_add_executor_job(_update_db)
        
        # Fire signal to update sensors/images dynamically
        async_dispatcher_send(hass, SIGNAL_DRYAD_UPDATE)
        
        _LOGGER.info(f"Dryad sync successful: {num_plants} plants, {num_logs} logs updated")
        return self.json({"status": "success", "server_time": int(time.time() * 1000)})


class DryadPhotoView(HomeAssistantView):
    url = API_PHOTO_ENDPOINT
    name = "api:dryad:photo"
    requires_auth = True

    def __init__(self, media_dir):
        self.media_dir = media_dir

    async def post(self, request):
        hass = request.app["hass"]
        reader = await request.multipart()
        
        plant_id = None
        created_at = None
        image_data = None
        
        while True:
            part = await reader.next()
            if part is None:
                break
            if part.name == "plant_id":
                plant_id = await part.text()
            elif part.name == "created_at":
                created_at = await part.text()
            elif part.name == "photo":
                image_data = await part.read()

        if not plant_id or not created_at or not image_data:
            return self.json({"status": "error", "message": "Missing form data"}, status_code=400)

        # Save image to media folder
        def _save_image():
            plant_dir = os.path.join(self.media_dir, plant_id)
            os.makedirs(plant_dir, exist_ok=True)
            file_path = os.path.join(plant_dir, f"{created_at}.jpg")
            with open(file_path, "wb") as f:
                f.write(image_data)
        
        await hass.async_add_executor_job(_save_image)
        
        # Notify image entity that a new photo is available
        async_dispatcher_send(hass, SIGNAL_DRYAD_UPDATE)
        return self.json({"status": "success"})


class DryadExportView(HomeAssistantView):
    url = API_EXPORT_ENDPOINT
    name = "api:dryad:export"
    requires_auth = True

    def __init__(self, db):
        self.db = db

    async def get(self, request, plant_id):
        hass = request.app["hass"]
        csv_data = await hass.async_add_executor_job(self.db.generate_csv, plant_id)
        
        return web.Response(
            body=csv_data,
            content_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="{plant_id}_logs.csv"'}
        )
