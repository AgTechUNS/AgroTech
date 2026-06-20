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
        background: "var(--bg-glass)",
        backdropFilter: "var(--blur)",
        WebkitBackdropFilter: "var(--blur)",
        borderRadius: "var(--radius)",
        border: "1px solid var(--border)",
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
            background: sensor.activo ? "var(--success-bg)" : "var(--danger-bg)",
            color: sensor.activo ? "var(--success)" : "var(--danger)",
          }}
        >
          {sensor.activo ? "Activo" : "Inactivo"}
        </span>
      </div>
      <div style={{ fontSize: "0.85rem", color: "var(--text-secondary)", marginBottom: "0.75rem" }}>
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
              <span style={{ color: "var(--text-secondary)" }}>Temp </span>
              <span style={{ fontWeight: 600 }}>{ultimaTemp.toFixed(1)}°C</span>
            </div>
          )}
          {ultimaHum !== undefined && (
            <div>
              <span style={{ color: "var(--text-secondary)" }}>Hum </span>
              <span style={{ fontWeight: 600 }}>{ultimaHum.toFixed(1)}%</span>
            </div>
          )}
        </div>
      ) : (
        <div style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>Sin lecturas</div>
      )}
    </div>
  );
}
