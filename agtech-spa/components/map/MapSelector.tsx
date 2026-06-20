"use client";

import { useCallback, useEffect } from "react";
import { MapContainer, TileLayer, useMap } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import "leaflet-draw/dist/leaflet.draw.css";
import { DrawControl } from "./DrawControl";

export interface ExistingPolygon {
  geojson: string;
  label: string;
  color?: string;
  weight?: number;
  fillOpacity?: number;
}

interface MapSelectorProps {
  onPolygonChange: (geojson: string | null) => void;
  height?: number;
  existingPolygons?: ExistingPolygon[];
}

function ExistingPolygonsLayer({ polygons }: { polygons: ExistingPolygon[] }) {
  const map = useMap();

  useEffect(() => {
    if (polygons.length === 0) return;

    const layer = L.featureGroup();
    const allCoords: [number, number][] = [];

    polygons.forEach((p) => {
      try {
        const geo = JSON.parse(p.geojson);
        const leafletPoly = L.geoJSON(geo, {
          style: {
            color: p.color ?? "#3388ff",
            weight: p.weight ?? 2,
            fillOpacity: p.fillOpacity ?? 0.1,
          },
        });
        leafletPoly.bindTooltip(p.label, { permanent: false, direction: "center", sticky: true });
        layer.addLayer(leafletPoly);

        if (geo.type === "Polygon") {
          geo.coordinates[0].forEach((c: number[]) => allCoords.push([c[1], c[0]]));
        }
      } catch { /* skip */ }
    });

    map.addLayer(layer);
    if (allCoords.length > 0) {
      map.fitBounds(L.latLngBounds(allCoords).pad(0.1));
    }

    return () => {
      map.removeLayer(layer);
    };
  }, [map, polygons]);

  return null;
}

export function MapSelector({ onPolygonChange, height = 400, existingPolygons = [] }: MapSelectorProps) {
  const handlePolygonCreated = useCallback(
    (geojson: string) => onPolygonChange(geojson),
    [onPolygonChange]
  );

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
        <ExistingPolygonsLayer polygons={existingPolygons} />
        <DrawControl onPolygonCreated={handlePolygonCreated} />
      </MapContainer>
    </div>
  );
}
