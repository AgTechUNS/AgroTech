"use client";

import { Lectura } from "@/lib/types";

interface SensorChartProps {
  lecturas: Lectura[];
  sensorId?: string;
}

function minMax(values: number[]): [number, number] {
  const min = Math.min(...values);
  const max = Math.max(...values);
  const pad = (max - min) * 0.1 || 5;
  return [min - pad, max + pad];
}

export function SensorChart({ lecturas, sensorId }: SensorChartProps) {
  const filtradas = sensorId
    ? lecturas.filter((l) => l.sensorId === sensorId)
    : lecturas;

  if (filtradas.length === 0) {
    return <p style={{ color: "#94a3b8", textAlign: "center", padding: "1rem" }}>Sin lecturas</p>;
  }

  const sliced = filtradas.slice(-24);
  const labels = sliced.map((l) => {
    const d = new Date(l.timestamp);
    return `${d.getHours().toString().padStart(2, "0")}:${d.getMinutes().toString().padStart(2, "0")}`;
  });

  const temps = sliced.map((l) => l.temperatura).filter((t): t is number => t !== null);
  const hums = sliced.map((l) => l.humedad).filter((h): h is number => h !== null);

  const [tempMin, tempMax] = temps.length > 0 ? minMax(temps) : [0, 50];
  const [humMin, humMax] = hums.length > 0 ? minMax(hums) : [0, 100];

  const W = 600;
  const H = 180;
  const PAD = { top: 10, right: 10, bottom: 20, left: 40 };
  const iw = W - PAD.left - PAD.right;
  const ih = H - PAD.top - PAD.bottom;

  const tempPath = temps
    .map((t, i) => {
      const x = PAD.left + (i / Math.max(temps.length - 1, 1)) * iw;
      const y = PAD.top + ih - ((t - tempMin) / (tempMax - tempMin)) * ih;
      return `${i === 0 ? "M" : "L"}${x.toFixed(1)},${y.toFixed(1)}`;
    })
    .join(" ");

  const humPath = hums
    .map((h, i) => {
      const x = PAD.left + (i / Math.max(hums.length - 1, 1)) * iw;
      const y = PAD.top + ih - ((h - humMin) / (humMax - humMin)) * ih;
      return `${i === 0 ? "M" : "L"}${x.toFixed(1)},${y.toFixed(1)}`;
    })
    .join(" ");

  return (
    <div>
      <svg width="100%" viewBox={`0 0 ${W} ${H}`} style={{ display: "block" }}>
        <line x1={PAD.left} y1={0} x2={PAD.left} y2={H - PAD.bottom} stroke="#e2e8f0" />
        <line x1={PAD.left} y1={H - PAD.bottom} x2={W - PAD.right} y2={H - PAD.bottom} stroke="#e2e8f0" />
        {tempPath && <path d={tempPath} fill="none" stroke="#ef4444" strokeWidth="2" />}
        {humPath && <path d={humPath} fill="none" stroke="#3b82f6" strokeWidth="2" />}
        {temps.length > 0 && (() => {
          const step = Math.max(1, Math.floor(labels.length / 6));
          return labels.map((label, idx) => {
            if (idx % step !== 0) return null;
            const x = PAD.left + (idx / Math.max(temps.length - 1, 1)) * iw;
            return <text key={label + idx} x={x} y={H - 4} textAnchor="middle" fontSize="10" fill="#94a3b8">{label}</text>;
          });
        })()}
      </svg>
      <div style={{ display: "flex", gap: "1.5rem", fontSize: "0.8rem", color: "#64748b", marginTop: "0.3rem" }}>
        <span><span style={{ color: "#ef4444" }}>━</span> Temperatura</span>
        <span><span style={{ color: "#3b82f6" }}>━</span> Humedad</span>
      </div>
    </div>
  );
}
