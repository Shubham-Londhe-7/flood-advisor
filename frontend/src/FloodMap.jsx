// Pune Flood Advisor - Map component
// Needs: npm install leaflet react-leaflet
import { useEffect, useState } from "react";
import { MapContainer, TileLayer, CircleMarker, Popup, useMapEvents } from "react-leaflet";
import "leaflet/dist/leaflet.css";

const API_BASE = "https://flood-advisor.onrender.com";

const riskColor = {
  high: "#e63946",
  medium: "#f4a261",
  low: "#2a9d8f",
};

function ReportClickHandler({ onMapClick }) {
  useMapEvents({
    click(e) {
      onMapClick(e.latlng);
    },
  });
  return null;
}

export default function FloodMap() {
  const [zones, setZones] = useState([]);
  const [reportMode, setReportMode] = useState(false);
  const [pendingReport, setPendingReport] = useState(null);

  useEffect(() => {
    fetchZones();
    const interval = setInterval(fetchZones, 60000); // refresh every 1 min
    return () => clearInterval(interval);
  }, []);

  async function fetchZones() {
    const res = await fetch(`${API_BASE}/zones`);
    const data = await res.json();
    setZones(data);
  }

  async function submitReport(latlng, severity) {
    await fetch(`${API_BASE}/report`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ lat: latlng.lat, lon: latlng.lng, severity }),
    });
    setPendingReport(null);
    setReportMode(false);
    fetchZones(); // refresh risk after report
  }

  return (
    <div style={{ height: "100vh", width: "100%" }}>
      <div style={{ padding: 8, background: "#fff", position: "absolute", zIndex: 1000, top: 10, left: 10, borderRadius: 8, boxShadow: "0 1px 4px rgba(0,0,0,0.2)" }}>
        <button onClick={() => setReportMode(!reportMode)}>
          {reportMode ? "Cancel report" : "Report waterlogging here"}
        </button>
      </div>

      <MapContainer center={[18.5204, 73.8567]} zoom={12} style={{ height: "100%", width: "100%" }}>
        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />

        {zones.map((z) => (
          <CircleMarker
            key={z.zone_id}
            center={[z.lat, z.lon]}
            radius={12}
            pathOptions={{ color: riskColor[z.risk_level], fillOpacity: 0.6 }}
          >
            <Popup>
              <b>{z.name}</b><br />
              Risk: {z.risk_level} ({z.risk_score.toFixed(1)}/10)
            </Popup>
          </CircleMarker>
        ))}

        {reportMode && <ReportClickHandler onMapClick={setPendingReport} />}

        {pendingReport && (
          <CircleMarker center={[pendingReport.lat, pendingReport.lng]} radius={8} pathOptions={{ color: "#000" }}>
            <Popup>
              Confirm report severity:
              <br />
              {[1, 2, 3, 4, 5].map((s) => (
                <button key={s} onClick={() => submitReport(pendingReport, s)} style={{ margin: 2 }}>
                  {s}
                </button>
              ))}
            </Popup>
          </CircleMarker>
        )}
      </MapContainer>
    </div>
  );
}
