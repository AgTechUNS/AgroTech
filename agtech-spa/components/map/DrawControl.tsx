"use client";

import { useEffect, useRef } from "react";
import { useMap } from "react-leaflet";
import L from "leaflet";
import "leaflet-draw";

interface DrawControlProps {
  onPolygonCreated: (geojson: string) => void;
}

export function DrawControl({ onPolygonCreated }: DrawControlProps) {
  const map = useMap();
  const drawnLayerRef = useRef<L.Layer | null>(null);
  const featureGroupRef = useRef<L.FeatureGroup>(new L.FeatureGroup());

  useEffect(() => {
    const fg = featureGroupRef.current;
    const drawControl = new L.Control.Draw({
      draw: {
        polygon: { allowIntersection: false, showArea: true },
        polyline: false,
        rectangle: false,
        circle: false,
        circlemarker: false,
        marker: false,
      },
      edit: { featureGroup: fg },
    });

    map.addControl(drawControl);

    const handleCreated = (e: any) => {
      const layer = e.layer;
      const geoJSON = (layer as any).toGeoJSON();
      fg.clearLayers();
      fg.addLayer(layer);
      drawnLayerRef.current = layer;
      onPolygonCreated(JSON.stringify(geoJSON));
    };

    const handleEdited = () => {
      const layers = fg.getLayers();
      if (layers.length > 0) {
        const geoJSON = (layers[0] as any).toGeoJSON();
        onPolygonCreated(JSON.stringify(geoJSON));
      }
    };

    const handleDeleted = () => {
      drawnLayerRef.current = null;
      onPolygonCreated("");
    };

    map.on(L.Draw.Event.CREATED as any, handleCreated as any);
    map.on(L.Draw.Event.EDITED as any, handleEdited as any);
    map.on(L.Draw.Event.DELETED as any, handleDeleted as any);

    return () => {
      map.off(L.Draw.Event.CREATED as any, handleCreated as any);
      map.off(L.Draw.Event.EDITED as any, handleEdited as any);
      map.off(L.Draw.Event.DELETED as any, handleDeleted as any);
      map.removeControl(drawControl);
    };
  }, [map, onPolygonCreated]);

  return null;
}
