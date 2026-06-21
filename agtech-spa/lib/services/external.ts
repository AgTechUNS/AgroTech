import { SatelitalData, WeatherResponse, SatelitalHistorialItem, CampoNdviItem } from "@/lib/types";
import { fetchWithAuth } from "@/lib/auth";

export async function obtenerSatelital(coordenadas: string, nombreParcela?: string, nombreCampo?: string): Promise<SatelitalData> {
  let url = `/api/external/satelital?coordenadas=${encodeURIComponent(coordenadas)}`;
  if (nombreParcela) url += `&nombre_parcela=${encodeURIComponent(nombreParcela)}`;
  if (nombreCampo) url += `&nombre_campo=${encodeURIComponent(nombreCampo)}`;
  const res = await fetchWithAuth(url);
  if (!res.ok) throw new Error("Error al obtener datos satelitales");
  return res.json();
}

export async function obtenerHistorialSatelital(nombreParcela: string, nombreCampo: string): Promise<SatelitalHistorialItem[]> {
  const res = await fetchWithAuth(`/api/external/satelital/historial?nombre_parcela=${encodeURIComponent(nombreParcela)}&nombre_campo=${encodeURIComponent(nombreCampo)}`);
  if (!res.ok) return [];
  return res.json();
}

export async function obtenerNdviCampo(nombreCampo: string): Promise<CampoNdviItem[]> {
  const res = await fetchWithAuth(`/api/external/satelital/campo/${encodeURIComponent(nombreCampo)}`);
  if (!res.ok) return [];
  return res.json();
}

export async function obtenerWeather(lat: number, lon: number): Promise<WeatherResponse> {
  const res = await fetchWithAuth(`/api/external/weather?lat=${lat}&lon=${lon}`);
  if (!res.ok) throw new Error("Error al obtener datos meteorológicos");
  return res.json();
}
