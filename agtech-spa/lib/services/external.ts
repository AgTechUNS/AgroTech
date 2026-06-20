import { SatelitalData, WeatherResponse } from "@/lib/types";
import { fetchWithAuth } from "@/lib/auth";

export async function obtenerSatelital(coordenadas: string): Promise<SatelitalData> {
  const res = await fetchWithAuth(`/api/external/satelital?coordenadas=${encodeURIComponent(coordenadas)}`);
  if (!res.ok) throw new Error("Error al obtener datos satelitales");
  return res.json();
}

export async function obtenerWeather(lat: number, lon: number): Promise<WeatherResponse> {
  const res = await fetchWithAuth(`/api/external/weather?lat=${lat}&lon=${lon}`);
  if (!res.ok) throw new Error("Error al obtener datos meteorológicos");
  return res.json();
}
