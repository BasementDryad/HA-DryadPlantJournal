class DryadCard extends HTMLElement {
  set hass(hass) {
    if (!this.content) {
      this.innerHTML = `
        <ha-card>
          <style>
            .header {
              display: flex; justify-content: space-between; align-items: center;
              padding: 16px; background: rgba(0,0,0,0.2); border-radius: 12px 12px 0 0;
            }
            .title { font-size: 20px; font-weight: bold; display: flex; align-items: center; gap: 8px; }
            .color-dot { width: 12px; height: 12px; border-radius: 50%; }
            .photo-container {
              width: 100%; height: 250px; background-size: cover; background-position: center;
              position: relative;
            }
            .stage-badge {
              position: absolute; bottom: 8px; right: 8px;
              background: rgba(0,0,0,0.7); color: white; padding: 4px 8px; border-radius: 12px;
              font-size: 12px;
            }
            .metrics-grid {
              display: grid; grid-template-columns: 1fr 1fr; gap: 8px; padding: 16px;
            }
            .metric-pill {
              display: flex; align-items: center; gap: 8px;
              background: rgba(255,255,255,0.05); padding: 8px 12px; border-radius: 8px;
            }
            .spectrum-bar {
              height: 12px; border-radius: 6px; margin: 0 16px;
              background: linear-gradient(90deg, #8A2BE2, #0000FF, #00FF00, #FFFF00, #FFA500, #FF0000, #800000);
            }
            .actions { padding: 16px; display: flex; gap: 8px; }
            button {
              flex: 1; padding: 8px; border-radius: 8px; border: none; cursor: pointer;
              background: var(--primary-color); color: white; font-weight: bold;
            }
          </style>
          <div class="content"></div>
        </ha-card>
      `;
      this.content = this.querySelector('.content');
    }

    const plantId = this.config.plant_id;
    const name = hass.states[`sensor.dryad_${plantId}_stage`]?.attributes.friendly_name?.replace(' Stage', '') || 'Plant';
    const stage = hass.states[`sensor.dryad_${plantId}_stage`]?.state || 'Unknown';
    const days = hass.states[`sensor.dryad_${plantId}_cycle_days`]?.state || '0';
    const temp = hass.states[`sensor.dryad_${plantId}_temperature`]?.state || '--';
    const humidity = hass.states[`sensor.dryad_${plantId}_humidity`]?.state || '--';
    const vpd = hass.states[`sensor.dryad_${plantId}_vpd_canopy`]?.state || '--';
    const dli = hass.states[`sensor.dryad_${plantId}_dli`]?.state || '--';
    const water = hass.states[`sensor.dryad_${plantId}_water_amount`]?.state || '--';
    const notes = hass.states[`sensor.dryad_${plantId}_notes`]?.state || 'No notes today.';
    
    // Auto-bust cache for image updates
    const imageEntity = hass.states[`image.dryad_${plantId}_photo`];
    const imageToken = imageEntity?.attributes.access_token || '';
    const imageUrl = `/api/image_proxy/image.dryad_${plantId}_photo?token=${imageToken}`;

    this.content.innerHTML = `
      <div class="header">
        <div class="title">
          <div class="color-dot" style="background: #9C27B0;"></div>
          ${name}
        </div>
        <div>Cycle: ${days} Days</div>
      </div>
      
      <div class="photo-container" style="background-image: url('${imageUrl}');">
        <div class="stage-badge">${stage}</div>
      </div>

      <div class="metrics-grid">
        <div class="metric-pill">🌡️ ${temp}° / 💧 ${humidity}%</div>
        <div class="metric-pill">🌬️ VPD: ${vpd} kPa</div>
        <div class="metric-pill">☀️ DLI: ${dli}</div>
        <div class="metric-pill">🚿 Water: ${water} L</div>
      </div>

      <div style="padding: 0 16px 8px; font-size: 12px;">Light Spectrum</div>
      <div class="spectrum-bar"></div>

      <div style="padding: 16px;">
        <strong>Notes:</strong><br/>
        <span style="opacity: 0.8;">${notes}</span>
      </div>

      <div class="actions">
        <button onclick="window.location.href='/api/dryad/export/${plantId}.csv'">📥 Download CSV</button>
        <button id="addLogBtn">➕ Add Log</button>
      </div>
    `;

    // Simple service call attachment
    const btn = this.querySelector('#addLogBtn');
    if(btn) {
      btn.onclick = () => {
        hass.callService('dryad', 'add_log', {
          plant_id: plantId,
          notes: "Quick log from Lovelace"
        });
      };
    }
  }

  setConfig(config) {
    if (!config.plant_id) {
      throw new Error("You need to define a plant_id");
    }
    this.config = config;
  }
}
customElements.define('dryad-card', DryadCard);
