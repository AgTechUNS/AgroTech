"use client";

import { useEffect } from "react";
import { MapContainer, TileLayer, GeoJSON, useMap } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { Campo, Parcela, Sensor, Lectura } from "@/lib/types";
import { useTheme } from "@/contexts/ThemeContext";
import { TILE_LIGHT, TILE_DARK, TILE_ATTR } from "./tiles";

interface FieldsMapProps {
  fields?: Campo[];
  parcels?: Parcela[];
  sensores?: Sensor[];
  lecturas?: Lectura[];
  height?: number;
  ndviPorParcela?: Record<string, number>;
}

function FitBounds({ items, getCoords }: { items: unknown[]; getCoords: (item: unknown) => string }) {
  const map = useMap();
  useEffect(() => {
    if (items.length === 0) return;
    try {
      const coords: [number, number][] = [];
      for (const item of items) {
        const geo = toGeoJSON(getCoords(item));
        if (!geo) continue;
        const g = geo as GeoJSON.Polygon;
        if (g.type === "Polygon" && g.coordinates?.[0]) {
          (g.coordinates[0] as number[][]).forEach((c) => coords.push([c[1], c[0]]));
        }
      }
      if (coords.length > 0) {
        map.fitBounds(L.latLngBounds(coords).pad(0.2));
      }
    } catch {
      // ignore
    }
  }, [items, map, getCoords]);
  return null;
}

function toGeoJSON(raw: string): unknown | null {
  try {
    const parsed = JSON.parse(raw);
    if (parsed && typeof parsed === "object" && parsed.type) return parsed;
    if (Array.isArray(parsed) && parsed.length >= 3) {
      return { type: "Polygon", coordinates: [parsed] };
    }
    return null;
  } catch {
    return null;
  }
}

const FIELD_COLORS = ["#60a5fa", "#34d399", "#fbbf24", "#a78bfa", "#f87171", "#2dd4bf"];
const PARCEL_COLORS = ["#f87171", "#fb923c", "#c084fc", "#2dd4bf", "#fbbf24"];

function ndviColor(ndvi: number | undefined): string {
  if (ndvi === undefined) return "#94a3b8";
  if (ndvi >= 0.7) return "#22c55e";
  if (ndvi >= 0.5) return "#84cc16";
  if (ndvi >= 0.3) return "#eab308";
  return "#ef4444";
}

function ndviLabel(ndvi: number | undefined): string {
  if (ndvi === undefined) return "Sin datos";
  if (ndvi >= 0.7) return "Muy saludable";
  if (ndvi >= 0.5) return "Moderado";
  if (ndvi >= 0.3) return "Escaso";
  return "Estrés severo";
}

export function FieldsMap({ fields, parcels, sensores, lecturas, height = 400, ndviPorParcela }: FieldsMapProps) {
  const { theme } = useTheme();
  const hasData = (fields && fields.length > 0) || (parcels && parcels.length > 0);
  if (!hasData) return null;

  const sensoresByCampo: Record<string, number> = {};
  sensores?.forEach((s) => {
    sensoresByCampo[s.nombreCampo] = (sensoresByCampo[s.nombreCampo] || 0) + 1;
  });

  const sensoresByParcela: Record<string, Sensor[]> = {};
  sensores?.forEach((s) => {
    if (!sensoresByParcela[s.nombreParcela]) sensoresByParcela[s.nombreParcela] = [];
    sensoresByParcela[s.nombreParcela].push(s);
  });

  const lastLecturaBySensor: Record<string, Lectura> = {};
  if (lecturas) {
    for (const l of lecturas) {
      if (!lastLecturaBySensor[l.sensorId] || new Date(l.timestamp) > new Date(lastLecturaBySensor[l.sensorId].timestamp)) {
        lastLecturaBySensor[l.sensorId] = l;
      }
    }
  }

  const allItems: { geo: unknown; style: L.PathOptions; tooltip: string }[] = [];
  const allCoords: { geoStr: string }[] = [];

  if (fields) {
    fields.forEach((f, i) => {
      const geo = toGeoJSON(f.coordenadasCampo);
      if (!geo) return;
      const parcelCount = parcels?.filter((p) => p.nombreCampo === f.nombreCampo).length ?? 0;
      const sensorCount = sensoresByCampo[f.nombreCampo] ?? 0;
      let tooltip = `<b>${f.nombreCampo}</b>`;
      if (f.descripcionCampo) tooltip += `<br/>${f.descripcionCampo}`;
      tooltip += `<br/><span style="font-size:0.85rem;color:#94a3b8;">Parcelas: ${parcelCount} | Sensores: ${sensorCount}</span>`;
      allItems.push({
        geo,
        style: {
          color: FIELD_COLORS[i % FIELD_COLORS.length],
          weight: 2,
          fillOpacity: 0.12,
        },
        tooltip,
      });
      allCoords.push({ geoStr: f.coordenadasCampo });
    });
  }

  const lecturasByParcela: Record<string, string[]> = {};
  if (lecturas) {
    for (const l of lecturas) {
      const sensorParcela = l.parcelaId || "";
      if (!sensorParcela) continue;
      if (!lecturasByParcela[sensorParcela]) lecturasByParcela[sensorParcela] = [];
      if (!lecturasByParcela[sensorParcela].includes(l.sensorId)) {
        lecturasByParcela[sensorParcela].push(l.sensorId);
      }
    }
  }

  if (parcels) {
    parcels.forEach((p, i) => {
      const geo = toGeoJSON(p.coordenadasParcela);
      if (!geo) return;

      const parcelaSensores = sensoresByParcela[p.nombreParcela] ?? [];
      const activos = parcelaSensores.filter((s) => s.activo);
      const lecturasSensorIds = lecturasByParcela[p.nombreParcela] ?? [];
      const allSensorIds: string[] = [];
      activos.forEach(s => { if (!allSensorIds.includes(s.deviceId)) allSensorIds.push(s.deviceId); });
      lecturasSensorIds.forEach(sid => { if (!allSensorIds.includes(sid)) allSensorIds.push(sid); });

      const ndvi = ndviPorParcela?.[p.nombreParcela];
      const color = ndvi !== undefined ? ndviColor(ndvi) : PARCEL_COLORS[i % PARCEL_COLORS.length];

      let tooltip = `<b>${p.nombreParcela}</b>`;
      if (ndvi !== undefined) {
        tooltip += `<br/><span style="font-size:0.85rem;">🌿 NDVI: <b>${ndvi.toFixed(3)}</b> — ${ndviLabel(ndvi)}</span>`;
      }
      if (p.nombreCultivo) tooltip += `<br/>${p.nombreCultivo}${p.variedad ? ` — ${p.variedad}` : ""}`;
      if (p.descripcionParcela) tooltip += `<br/><span style="font-size:0.85rem;color:#94a3b8;">${p.descripcionParcela}</span>`;
      if (allSensorIds.length > 0) {
        tooltip += `<br/><hr style="border-color:rgba(255,255,255,0.1);margin:4px 0;"/>`;
        for (const sid of allSensorIds) {
          const ultima = lastLecturaBySensor[sid];
          tooltip += `<div style="font-size:0.85rem;margin:2px 0;">`;
          tooltip += `🛰️ <b>${sid}</b>`;
          if (ultima) {
            tooltip += ` — ${ultima.temperatura != null ? `${ultima.temperatura.toFixed(1)}°C` : "—"} / ${ultima.humedad != null ? `${ultima.humedad.toFixed(1)}%` : "—"}`;
          } else {
            tooltip += ` — <span style="color:#94a3b8;">sin datos</span>`;
          }
          tooltip += `</div>`;
        }
      }
      allItems.push({
        geo,
        style: {
          color,
          weight: 3,
          fillOpacity: ndvi !== undefined ? 0.35 : 0.2,
        },
        tooltip,
      });
      allCoords.push({ geoStr: p.coordenadasParcela });
    });
  }

  const hasNdvi = ndviPorParcela && Object.values(ndviPorParcela).some((v) => v !== undefined);

  return (
    <div style={{ borderRadius: "var(--radius)", overflow: "hidden", border: "1px solid var(--border)", position: "relative" }}>
      <MapContainer
        center={[-38.0, -62.5]}
        zoom={6}
        style={{ height, width: "100%" }}
        scrollWheelZoom={true}
      >
        <TileLayer
          attribution={TILE_ATTR}
          url={theme === "dark" ? TILE_DARK : TILE_LIGHT}
        />
        {allItems.map((item, i) => (
          <GeoJSON
            key={i}
            data={item.geo as GeoJSON.GeoJsonObject}
            style={item.style}
            eventHandlers={{
              mouseover: (e) => {
                e.layer.bindTooltip(item.tooltip, { sticky: true, direction: "right", offset: L.point(10, 10) }).openTooltip(e.latlng);
              },
              mouseout: (e) => {
                e.layer.closeTooltip();
                e.layer.unbindTooltip();
              },
            }}
          />
        ))}
        <FitBounds items={allCoords} getCoords={(item) => (item as { geoStr: string }).geoStr} />
      </MapContainer>
      {hasNdvi && (
        <div style={{
          position: "absolute", bottom: 12, right: 12, zIndex: 1000,
          background: "var(--card-bg, #1e293b)", borderRadius: 8, padding: "8px 12px",
          fontSize: "0.75rem", border: "1px solid var(--border, #334155)",
          boxShadow: "0 2px 8px rgba(0,0,0,0.3)",
        }}>
          <div style={{ fontWeight: 600, marginBottom: 4 }}>NDVI</div>
          {[
            { color: "#22c55e", label: "≥ 0.7 — Muy saludable" },
            { color: "#84cc16", label: "0.5 – 0.7 — Moderado" },
            { color: "#eab308", label: "0.3 – 0.5 — Escaso" },
            { color: "#ef4444", label: "< 0.3 — Estrés" },
            { color: "#94a3b8", label: "Sin datos" },
          ].map(({ color, label }) => (
            <div key={label} style={{ display: "flex", alignItems: "center", gap: 6, marginTop: 2 }}>
              <div style={{ width: 12, height: 12, borderRadius: 2, background: color }} />
              <span style={{ color: "var(--text-secondary, #94a3b8)" }}>{label}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
