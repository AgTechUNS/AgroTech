"use client";

import { useEffect } from "react";
import { useMap } from "react-leaflet";
import L from "leaflet";
import "leaflet-draw";

interface DrawControlProps {
  onPolygonCreated: (geojson: string) => void;
}

export function DrawControl({ onPolygonCreated }: DrawControlProps) {
  const map = useMap();

  useEffect(() => {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const drawControl = new (L.Control as any).Draw({
      edit: { featureGroup: new L.FeatureGroup() },
      draw: {
        polygon: { allowIntersection: false, showArea: true },
        circle: false,
        circlemarker: false,
        marker: false,
        polyline: false,
        rectangle: true,
      },
    });
    map.addControl(drawControl);

    const drawnItems = new L.FeatureGroup();
    map.addLayer(drawnItems);

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    map.on(L.Draw.Event.CREATED, (e: any) => {
      drawnItems.clearLayers();
      drawnItems.addLayer(e.layer);
      const geo = e.layer.toGeoJSON();
      onPolygonCreated(JSON.stringify(geo));
    });

    return () => {
      map.removeControl(drawControl);
      map.removeLayer(drawnItems);
    };
  }, [map, onPolygonCreated]);

  return null;
}
