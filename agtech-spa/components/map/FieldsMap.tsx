"use client";

import { useEffect } from "react";
import { MapContainer, TileLayer, GeoJSON, useMap } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { Campo, Parcela } from "@/lib/types";

interface FieldsMapProps {
  fields?: Campo[];
  parcels?: Parcela[];
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

const FIELD_COLORS = ["#2c7be5", "#27ae60", "#e67e22", "#8e44ad", "#c0392b", "#16a085"];
const PARCEL_COLORS = ["#e74c3c", "#f39c12", "#9b59b6", "#1abc9c", "#e67e22"];

export function FieldsMap({ fields, parcels, height = 400 }: FieldsMapProps) {
  const hasData = (fields && fields.length > 0) || (parcels && parcels.length > 0);
  if (!hasData) return null;

  const allItems: { geo: unknown; style: L.PathOptions }[] = [];
  const allCoords: { geoStr: string }[] = [];

  if (fields) {
    fields.forEach((f, i) => {
      try {
        const geo = JSON.parse(f.coordenadasCampo);
        allItems.push({
          geo,
          style: { color: FIELD_COLORS[i % FIELD_COLORS.length], weight: 2, fillOpacity: 0.1 },
        });
        allCoords.push({ geoStr: f.coordenadasCampo });
      } catch { /* skip */ }
    });
  }

  if (parcels) {
    parcels.forEach((p, i) => {
      try {
        const geo = JSON.parse(p.coordenadasParcela);
        allItems.push({
          geo,
          style: { color: PARCEL_COLORS[i % PARCEL_COLORS.length], weight: 3, fillOpacity: 0.25 },
        });
        allCoords.push({ geoStr: p.coordenadasParcela });
      } catch { /* skip */ }
    });
  }

  return (
    <div style={{ borderRadius: "8px", overflow: "hidden", border: "1px solid #e2e8f0" }}>
      <MapContainer
        center={[-38.0, -62.5]}
        zoom={6}
        style={{ height, width: "100%" }}
        scrollWheelZoom={true}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {allItems.map((item, i) => (
          <GeoJSON key={i} data={item.geo as GeoJSON.GeoJsonObject} style={item.style} />
        ))}
        <FitBounds items={allCoords} getCoords={(item) => (item as { geoStr: string }).geoStr} />
      </MapContainer>
    </div>
  );
}
