// Pune Flood Advisor - Map component
// Needs: npm install leaflet react-leaflet
import { useEffect, useState, useRef } from "react";
import { MapContainer, TileLayer, CircleMarker, Popup, Polyline, useMapEvents } from "react-leaflet";
import "leaflet/dist/leaflet.css";

const API_BASE = "https://flood-advisor.onrender.com"; // live backend

const riskColor = {
  high: "#e63946",
  medium: "#f4a261",
  low: "#2a9d8f",
};

function ClickHandler({ onMapClick }) {
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

  // route-check state
  const [routeMode, setRouteMode] = useState(false);
  const [routeStart, setRouteStart] = useState(null);
  const [routeEnd, setRouteEnd] = useState(null);
  const [routeResult, setRouteResult] = useState(null);
  const [routeLoading, setRouteLoading] = useState(false);

  // alerts state
  const [alertsOn, setAlertsOn] = useState(false);
  const notifiedZones = useRef(new Set()); // avoid repeat-notifying same zone

  useEffect(() => {
    fetchZones();
    const interval = setInterval(fetchZones, 60000); // refresh every 1 min
    return () => clearInterval(interval);
  }, []);

  // check for newly-high-risk zones whenever zones refresh, fire browser notification
  useEffect(() => {
    if (!alertsOn) return;
    zones.forEach((z) => {
      if (z.risk_level === "high" && !notifiedZones.current.has(z.zone_id)) {
        notifiedZones.current.add(z.zone_id);
        if (Notification.permission === "granted") {
          new Notification("⚠️ High flood risk nearby", {
            body: `${z.name} is now HIGH risk (${z.risk_score.toFixed(1)}/10). Avoid this route.`,
          });
        }
      }
      if (z.risk_level !== "high") {
        notifiedZones.current.delete(z.zone_id);
      }
    });
  }, [zones, alertsOn]);

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
    fetchZones();
  }

  async function runRouteCheck() {
    if (!routeStart || !routeEnd) return;
    setRouteLoading(true);
    try {
      const res = await fetch(`${API_BASE}/route-check`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          start_lat: routeStart.lat,
          start_lon: routeStart.lng,
          end_lat: routeEnd.lat,
          end_lon: routeEnd.lng,
        }),
      });
      const data = await res.json();
      setRouteResult(data);
    } finally {
      setRouteLoading(false);
    }
  }

  function handleRouteClick(latlng) {
    if (!routeStart) {
      setRouteStart(latlng);
    } else if (!routeEnd) {
      setRouteEnd(latlng);
    } else {
      // reset and start new selection
      setRouteStart(latlng);
      setRouteEnd(null);
      setRouteResult(null);
    }
  }

  function resetRoute() {
    setRouteStart(null);
    setRouteEnd(null);
    setRouteResult(null);
    setRouteMode(false);
  }

  async function enableAlerts() {
    if (!("Notification" in window)) {
      alert("This browser doesn't support notifications.");
      return;
    }
    const permission = await Notification.requestPermission();
    if (permission === "granted") {
      setAlertsOn(true);
    } else {
      alert("Notification permission denied — enable it in browser settings to get alerts.");
    }
  }

  return (
    <div style={{ height: "100vh", width: "100%" }}>
      <div
        style={{
          position: "absolute", zIndex: 1000, top: 10, left: 10,
          display: "flex", flexDirection: "column", gap: 6,
        }}
      >
        <div style={{ padding: 8, background: "#fff", borderRadius: 8, boxShadow: "0 1px 4px rgba(0,0,0,0.2)" }}>
          <button onClick={() => { setReportMode(!reportMode); setRouteMode(false); }}>
            {reportMode ? "Cancel report" : "Report waterlogging here"}
          </button>
        </div>

        <div style={{ padding: 8, background: "#fff", borderRadius: 8, boxShadow: "0 1px 4px rgba(0,0,0,0.2)" }}>
          <button onClick={() => { setRouteMode(!routeMode); setReportMode(false); if (routeMode) resetRoute(); }}>
            {routeMode ? "Cancel route check" : "Check my route"}
          </button>
          {routeMode && (
            <div style={{ marginTop: 6, fontSize: 13, maxWidth: 220 }}>
              {!routeStart && "Click map to set START point."}
              {routeStart && !routeEnd && "Now click map to set END point."}
              {routeStart && routeEnd && (
                <>
                  <button onClick={runRouteCheck} disabled={routeLoading} style={{ marginRight: 6 }}>
                    {routeLoading ? "Checking..." : "Check now"}
                  </button>
                  <button onClick={resetRoute}>Reset</button>
                </>
              )}
              {routeResult && (
                <div style={{ marginTop: 8 }}>
                  {routeResult.safe ? (
                    <div style={{ color: "#2a9d8f" }}>✅ No flood-risk zones on this route.</div>
                  ) : (
                    <div>
                      <div style={{ color: "#e63946", fontWeight: "bold" }}>⚠️ Route crosses risk zones:</div>
                      {routeResult.warnings.map((w, i) => (
                        <div key={i} style={{ marginTop: 4 }}>
                          {w.zone_name} — {w.risk_level} ({w.distance_km}km from route)
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>

        <div style={{ padding: 8, background: "#fff", borderRadius: 8, boxShadow: "0 1px 4px rgba(0,0,0,0.2)" }}>
          <button onClick={enableAlerts} disabled={alertsOn}>
            {alertsOn ? "🔔 Alerts ON" : "Enable high-risk alerts"}
          </button>
        </div>
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
              Risk: {z.risk_level} ({z.risk_score.toFixed(1)}/10)<br />
              Rainfall (last hr): {z.rainfall_mm?.toFixed(1) ?? 0}mm
            </Popup>
          </CircleMarker>
        ))}

        {reportMode && <ClickHandler onMapClick={setPendingReport} />}
        {routeMode && !routeResult && <ClickHandler onMapClick={handleRouteClick} />}

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

        {routeStart && (
          <CircleMarker center={[routeStart.lat, routeStart.lng]} radius={8} pathOptions={{ color: "#000" }}>
            <Popup>Start</Popup>
          </CircleMarker>
        )}
        {routeEnd && (
          <CircleMarker center={[routeEnd.lat, routeEnd.lng]} radius={8} pathOptions={{ color: "#333" }}>
            <Popup>End</Popup>
          </CircleMarker>
        )}
        {routeStart && routeEnd && (
          <Polyline positions={[[routeStart.lat, routeStart.lng], [routeEnd.lat, routeEnd.lng]]} pathOptions={{ color: "#457b9d", dashArray: "6,6" }} />
        )}
      </MapContainer>
    </div>
  );
}
