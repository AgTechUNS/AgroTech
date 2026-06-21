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
}

function FitBounds({ items, getCoords }: { items: unknown[]; getCoords: (item: unknown) => string }) {
  const map = useMap();
  useEffect(() => {
    if (items.length === 0) return;
    try {
      const coords: [number, number][] = [];
      for (const item of items) {
        const geo = JSON.parse(getCoords(item));
        if (geo.type === "Polygon") {
          geo.coordinates[0].forEach((c: number[]) => coords.push([c[1], c[0]]));
        } else if (geo.type === "Point") {
          coords.push([geo.coordinates[1], geo.coordinates[0]]);
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

const FIELD_COLORS = ["#60a5fa", "#34d399", "#fbbf24", "#a78bfa", "#f87171", "#2dd4bf"];
const PARCEL_COLORS = ["#f87171", "#fb923c", "#c084fc", "#2dd4bf", "#fbbf24"];

export function FieldsMap({ fields, parcels, sensores, lecturas, height = 400 }: FieldsMapProps) {
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
      try {
        const geo = JSON.parse(f.coordenadasCampo);
        const parcelCount = parcels?.filter((p) => p.nombreCampo === f.nombreCampo).length ?? 0;
        const sensorCount = sensoresByCampo[f.nombreCampo] ?? 0;
        let tooltip = `<b>${f.nombreCampo}</b>`;
        if (f.descripcionCampo) tooltip += `<br/>${f.descripcionCampo}`;
        tooltip += `<br/><span style="font-size:0.85rem;color:#94a3b8;">Parcelas: ${parcelCount} | Sensores: ${sensorCount}</span>`;
        allItems.push({
          geo,
          style: { color: FIELD_COLORS[i % FIELD_COLORS.length], weight: 2, fillOpacity: 0.12 },
          tooltip,
        });
        allCoords.push({ geoStr: f.coordenadasCampo });
      } catch { /* skip */ }
    });
  }

  if (parcels) {
    parcels.forEach((p, i) => {
      try {
        const geo = JSON.parse(p.coordenadasParcela);
        const parcelaSensores = sensoresByParcela[p.nombreParcela] ?? [];
        const activos = parcelaSensores.filter((s) => s.activo);
        let tooltip = `<b>${p.nombreParcela}</b>`;
        if (p.nombreCultivo) tooltip += `<br/>${p.nombreCultivo}${p.variedad ? ` — ${p.variedad}` : ""}`;
        if (p.descripcionParcela) tooltip += `<br/><span style="font-size:0.85rem;color:#94a3b8;">${p.descripcionParcela}</span>`;
        if (activos.length > 0) {
          tooltip += `<br/><hr style="border-color:rgba(255,255,255,0.1);margin:4px 0;"/>`;
          for (const s of activos) {
            const ultima = lastLecturaBySensor[s.deviceId];
            tooltip += `<div style="font-size:0.85rem;margin:2px 0;">`;
            tooltip += `🛰️ <b>${s.deviceId}</b>`;
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
          style: { color: PARCEL_COLORS[i % PARCEL_COLORS.length], weight: 3, fillOpacity: 0.2 },
          tooltip,
        });
        allCoords.push({ geoStr: p.coordenadasParcela });
      } catch { /* skip */ }
    });
  }

  return (
    <div style={{ borderRadius: "var(--radius)", overflow: "hidden", border: "1px solid var(--border)" }}>
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
    </div>
  );
}
