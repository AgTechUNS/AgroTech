"use client";

import { Sensor } from "@/lib/types";

interface SensorCardProps {
  sensor: Sensor;
  ultimaTemp?: number;
  ultimaHum?: number;
}

export function SensorCard({ sensor, ultimaTemp, ultimaHum }: SensorCardProps) {
  return (
    <div
      style={{
        background: "#fff",
        borderRadius: "8px",
        border: "1px solid #e2e8f0",
        padding: "1rem",
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.5rem" }}>
        <span style={{ fontWeight: 600, fontSize: "0.9rem" }}>{sensor.deviceId}</span>
        <span
          style={{
            fontSize: "0.75rem",
            padding: "0.15rem 0.5rem",
            borderRadius: "999px",
            background: sensor.activo ? "#d4edda" : "#f8d7da",
            color: sensor.activo ? "#155724" : "#721c24",
          }}
        >
          {sensor.activo ? "Activo" : "Inactivo"}
        </span>
      </div>
      <div style={{ fontSize: "0.85rem", color: "#64748b", marginBottom: "0.75rem" }}>
        {sensor.tipo === "temperatura_humedad"
          ? "Temperatura / Humedad"
          : sensor.tipo === "ph"
            ? "pH"
            : "Lluvia"}
      </div>
      {ultimaTemp !== undefined || ultimaHum !== undefined ? (
        <div style={{ display: "flex", gap: "0.75rem", fontSize: "0.9rem" }}>
          {ultimaTemp !== undefined && (
            <div>
              <span style={{ color: "#64748b" }}>Temp </span>
              <span style={{ fontWeight: 600 }}>{ultimaTemp.toFixed(1)}°C</span>
            </div>
          )}
          {ultimaHum !== undefined && (
            <div>
              <span style={{ color: "#64748b" }}>Hum </span>
              <span style={{ fontWeight: 600 }}>{ultimaHum.toFixed(1)}%</span>
            </div>
          )}
        </div>
      ) : (
        <div style={{ fontSize: "0.8rem", color: "#94a3b8" }}>Sin lecturas</div>
      )}
    </div>
  );
}
