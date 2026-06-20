"use client";

import { Lectura } from "@/lib/types";

interface SensorChartProps {
  lecturas: Lectura[];
}

const BAR_HEIGHT = 120;
const BAR_MAX = 50;

export function SensorChart({ lecturas }: SensorChartProps) {
  const latest = lecturas.slice(-20);

  if (latest.length === 0) {
    return <p style={{ color: "#94a3b8", textAlign: "center", padding: "1rem" }}>Sin datos</p>;
  }

  const maxVal = Math.max(
    ...latest.map((l) => Math.max(l.temperatura ?? 0, l.humedad ?? 0)),
    BAR_MAX
  );

  return (
    <div>
      <div style={{ display: "flex", alignItems: "flex-end", gap: "2px", height: BAR_HEIGHT + 40, overflowX: "auto", paddingBottom: "1.5rem" }}>
        {latest.map((l, i) => {
          const tempH = ((l.temperatura ?? 0) / maxVal) * BAR_HEIGHT;
          const humH = ((l.humedad ?? 0) / maxVal) * BAR_HEIGHT;
          const label = new Date(l.timestamp).toLocaleDateString("es-AR", { day: "2-digit", month: "2-digit" });
          return (
            <div key={i} style={{ display: "flex", flexDirection: "column", alignItems: "center", minWidth: 30 }}>
              <div style={{ display: "flex", gap: "1px", alignItems: "flex-end", height: BAR_HEIGHT }}>
                {l.temperatura !== null && (
                  <div
                    style={{
                      width: 12,
                      height: tempH,
                      background: "#e74c3c",
                      borderRadius: "2px 2px 0 0",
                      transition: "height 0.2s",
                    }}
                    title={`Temp: ${l.temperatura}°C`}
                  />
                )}
                {l.humedad !== null && (
                  <div
                    style={{
                      width: 12,
                      height: humH,
                      background: "#2c7be5",
                      borderRadius: "2px 2px 0 0",
                      transition: "height 0.2s",
                    }}
                    title={`Hum: ${l.humedad}%`}
                  />
                )}
              </div>
              <span style={{ fontSize: "0.65rem", color: "#94a3b8", marginTop: "0.25rem", whiteSpace: "nowrap" }}>{label}</span>
            </div>
          );
        })}
      </div>
      <div style={{ display: "flex", gap: "1rem", justifyContent: "center", fontSize: "0.8rem", color: "#64748b" }}>
        <span><span style={{ display: "inline-block", width: 10, height: 10, background: "#e74c3c", borderRadius: 2, marginRight: 4 }} /> Temp</span>
        <span><span style={{ display: "inline-block", width: 10, height: 10, background: "#2c7be5", borderRadius: 2, marginRight: 4 }} /> Hum</span>
      </div>
    </div>
  );
}
