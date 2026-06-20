"use client";

import { useState } from "react";
import { obtenerSatelital, obtenerWeather } from "@/lib/services/external";
import { SatelitalData, WeatherResponse } from "@/lib/types";
import { Card, Button, Spinner } from "@/components/ui";

export default function ExternalDataPage() {
  const [satelital, setSatelital] = useState<SatelitalData | null>(null);
  const [weather, setWeather] = useState<WeatherResponse | null>(null);
  const [coordenadas, setCoordenadas] = useState("");
  const [lat, setLat] = useState("");
  const [lon, setLon] = useState("");
  const [loadingSat, setLoadingSat] = useState(false);
  const [loadingWx, setLoadingWx] = useState(false);
  const [error, setError] = useState("");

  async function buscarSatelital() {
    if (!coordenadas) return;
    setLoadingSat(true);
    setError("");
    try {
      const data = await obtenerSatelital(coordenadas);
      setSatelital(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error");
    } finally {
      setLoadingSat(false);
    }
  }

  async function buscarWeather() {
    const latN = parseFloat(lat);
    const lonN = parseFloat(lon);
    if (isNaN(latN) || isNaN(lonN)) return;
    setLoadingWx(true);
    setError("");
    try {
      const data = await obtenerWeather(latN, lonN);
      setWeather(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error");
    } finally {
      setLoadingWx(false);
    }
  }

  return (
    <div>
      <h1 style={{ fontSize: "1.5rem", fontWeight: 700, marginBottom: "0.5rem" }}>Datos externos</h1>
      <p style={{ color: "var(--text-secondary)", marginBottom: "1.5rem", fontSize: "0.9rem" }}>
        Consulta de datos satelitales y meteorológicos
      </p>

      {error && (
        <div style={{ color: "var(--danger)", background: "var(--danger-bg)", padding: "0.5rem 0.75rem", borderRadius: "var(--radius)", marginBottom: "1rem", fontSize: "0.85rem" }}>
          {error}
        </div>
      )}

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", gap: "1.5rem" }}>
        <Card title="Satelital (Google Earth Engine)">
          <div style={{ display: "flex", flexDirection: "column", gap: "0.8rem" }}>
            <div>
              <label style={{ display: "block", fontSize: "0.85rem", fontWeight: 600, marginBottom: "0.3rem" }}>Coordenadas (GeoJSON)</label>
              <textarea value={coordenadas} onChange={(e) => setCoordenadas(e.target.value)}
                placeholder='{"type":"Point","coordinates":[-62.5,-38.0]}'
                rows={3}
                style={{ width: "100%", padding: "0.4rem", border: "1px solid var(--border)", borderRadius: "var(--radius)", fontSize: "0.85rem", fontFamily: "monospace", background: "var(--bg-input)", color: "var(--text-primary)" }} />
            </div>
            <Button onClick={buscarSatelital} loading={loadingSat}>Consultar NDVI</Button>
            {satelital && (
              <div style={{ background: "var(--success-bg)", padding: "0.8rem", borderRadius: "var(--radius)" }}>
                <p style={{ margin: "0 0 0.4rem" }}><strong>NDVI:</strong> {satelital.ndvi}</p>
                <p style={{ margin: 0 }}><strong>Humedad suelo estimada:</strong> {satelital.humedad_suelo_estimada}%</p>
              </div>
            )}
          </div>
        </Card>

        <Card title="Meteorológico (Open-Meteo)">
          <div style={{ display: "flex", flexDirection: "column", gap: "0.8rem" }}>
            <div style={{ display: "flex", gap: "0.5rem" }}>
              <div style={{ flex: 1 }}>
                <label style={{ display: "block", fontSize: "0.85rem", fontWeight: 600, marginBottom: "0.3rem" }}>Latitud</label>
                <input type="number" value={lat} onChange={(e) => setLat(e.target.value)} step="0.1"
                  style={{ width: "100%", padding: "0.4rem", border: "1px solid var(--border)", borderRadius: "var(--radius)", fontSize: "0.9rem", background: "var(--bg-input)", color: "var(--text-primary)" }} />
              </div>
              <div style={{ flex: 1 }}>
                <label style={{ display: "block", fontSize: "0.85rem", fontWeight: 600, marginBottom: "0.3rem" }}>Longitud</label>
                <input type="number" value={lon} onChange={(e) => setLon(e.target.value)} step="0.1"
                  style={{ width: "100%", padding: "0.4rem", border: "1px solid var(--border)", borderRadius: "var(--radius)", fontSize: "0.9rem", background: "var(--bg-input)", color: "var(--text-primary)" }} />
              </div>
            </div>
            <Button onClick={buscarWeather} loading={loadingWx}>Consultar clima</Button>
            {weather && (
              <div style={{ background: "var(--accent-bg)", padding: "0.8rem", borderRadius: "var(--radius)" }}>
                <p style={{ margin: "0 0 0.3rem" }}><strong>Temperatura:</strong> {weather.temperature_celsius}°C</p>
                <p style={{ margin: "0 0 0.3rem" }}><strong>Humedad:</strong> {weather.humidity_percent}%</p>
                <p style={{ margin: "0 0 0.3rem" }}><strong>Coordenadas:</strong> {weather.latitude}, {weather.longitude}</p>
                <p style={{ margin: 0, fontSize: "0.85rem", color: "var(--text-muted)" }}>{new Date(weather.timestamp).toLocaleString()}</p>
              </div>
            )}
          </div>
        </Card>
      </div>
    </div>
  );
}
