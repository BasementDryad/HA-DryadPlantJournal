# 🌱 Dryad - Home Assistant Integration

Welcome to the official Home Assistant integration for **Dryad** — the ultimate plant and grow journaling app.

This custom integration enables **two-way, real-time sync** between your Android Dryad app and your Home Assistant smart home.

## ✨ Features

* **Dynamic Device Discovery**: Every plant in your Dryad app automatically becomes a native Device in Home Assistant.
* **Native Sensors**: Automatically tracks Temperature, Humidity, Canopy VPD, Leaf Temp, CO2, PAR, DLI, Water Volume, Feed Strength, and Vibe (Star Rating) as native Home Assistant sensors.
* **Two-Way Sync**: Log a watering event from a Lovelace dashboard or HA Automation, and it instantly syncs back down to your Android phone.
* **Live Media Storage**: Syncs your daily plant photos directly into Home Assistant's local `/media` folder.
* **Custom Lovelace Card**: Includes a beautiful `dryad-card` that perfectly mirrors the Android app UI (complete with light spectrum bars, expandable nutrients, and photo viewer).
* **On-Demand CSV Export**: Download your full 45-column log history straight from your Home Assistant dashboard at any time.

## 🚀 Installation (via HACS)

1. Open **HACS** in Home Assistant.
2. Click the three dots in the top right corner and select **Custom repositories**.
3. Add the URL of this repository and select the category **Integration**.
4. Search for "Dryad Plant Journal" in HACS and click **Download**.
5. Restart Home Assistant.
6. Go to **Settings > Devices & Services > Add Integration**, search for "Dryad", and install it!

### Adding the Lovelace Card
Once installed, you can add the beautiful UI card to any dashboard:
```yaml
type: custom:dryad-card
plant_id: <your-plant-id-here>
```

## 🛠 Manual Installation

1. Download the latest release.
2. Copy the `custom_components/dryad/` folder into your Home Assistant `/config/custom_components/` directory.
3. Copy the `www/dryad-card.js` file into your Home Assistant `/config/www/` directory.
4. Restart Home Assistant and add the integration via the UI.

## 📱 Get the App
Dryad is currently in development for Android. 
