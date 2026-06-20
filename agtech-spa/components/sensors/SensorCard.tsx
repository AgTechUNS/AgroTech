"use client";

import { Sensor } from "@/lib/types";

const TIPO_ICON: Record<string, string> = {
  temperatura_humedad: "🌡️",
  ph: "🧪",
  lluvia: "🌧️",
};

const TIPO_LABEL: Record<string, string> = {
  temperatura_humedad: "Temp. / Humedad",
  ph: "pH de suelo",
  lluvia: "Precipitación",
};

interface SensorCardProps {
  sensor: Sensor;
  ultimaTemp?: number;
  ultimaHum?: number;
  onClick?: () => void;
}

export function SensorCard({ sensor, ultimaTemp, ultimaHum, onClick }: SensorCardProps) {
  return (
    <div
      onClick={onClick}
      style={{
        background: "#fff",
        border: "1px solid #e2e8f0",
        borderRadius: "8px",
        padding: "1rem",
        cursor: onClick ? "pointer" : undefined,
        opacity: sensor.activo ? 1 : 0.5,
        transition: "box-shadow 0.15s",
      }}
      onMouseEnter={(e) => { e.currentTarget.style.boxShadow = "0 2px 8px rgba(0,0,0,0.1)"; }}
      onMouseLeave={(e) => { e.currentTarget.style.boxShadow = "none"; }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.5rem" }}>
        <span style={{ fontSize: "1.2rem" }}>{TIPO_ICON[sensor.tipo] ?? "📡"}</span>
        <span style={{ fontFamily: "monospace", fontWeight: 600, fontSize: "0.9rem" }}>
          {sensor.deviceId}
        </span>
        <span style={{
          fontSize: "0.75rem",
          padding: "0.15rem 0.5rem",
          borderRadius: "999px",
          background: sensor.activo ? "#dcfce7" : "#f1f5f9",
          color: sensor.activo ? "#16a34a" : "#94a3b8",
          marginLeft: "auto",
        }}>
          {sensor.activo ? "Activo" : "Inactivo"}
        </span>
      </div>
      <div style={{ fontSize: "0.8rem", color: "#64748b", marginBottom: "0.3rem" }}>
        {TIPO_LABEL[sensor.tipo] ?? sensor.tipo}
      </div>
      {ultimaTemp !== undefined && (
        <div style={{ fontSize: "0.85rem", color: "#334155" }}>
          Temp: <strong>{ultimaTemp}°C</strong>
        </div>
      )}
      {ultimaHum !== undefined && (
        <div style={{ fontSize: "0.85rem", color: "#334155" }}>
          Hum: <strong>{ultimaHum}%</strong>
        </div>
      )}
    </div>
  );
}
