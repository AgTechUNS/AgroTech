"use client";

import { useCallback } from "react";
import { MapContainer, TileLayer } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import "leaflet-draw/dist/leaflet.draw.css";
import { DrawControl } from "./DrawControl";

interface MapSelectorProps {
  onPolygonChange: (geojson: string | null) => void;
  height?: number;
}

export function MapSelector({ onPolygonChange, height = 400 }: MapSelectorProps) {
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
        <DrawControl onPolygonCreated={handlePolygonCreated} />
      </MapContainer>
    </div>
  );
}
