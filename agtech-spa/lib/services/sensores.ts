import { Sensor, Lectura } from "@/lib/types";
import { fetchWithAuth } from "@/lib/auth";
import { hash } from "@/lib/utils/hash";

function mockLecturas(nombreCampo: string, nombreParcela: string): Lectura[] {
  const seed = hash(`${nombreCampo}/${nombreParcela}`);
  const ahora = Date.now();
  const baseTemp = 24 + (seed % 10);
  const baseHum = 40 + (seed % 30);
  const lecturas: Lectura[] = [];
  for (let i = 0; i < 20; i++) {
    const offset = (20 - i) * 90 * 1000;
    const tempVariation = ((i * 7 + seed) % 9) - 4;
    const humVariation = ((i * 13 + seed) % 15) - 7;
    lecturas.push({
      sensorId: `sensor-mock-${(i % 3) + 1}`,
      timestamp: new Date(ahora - offset).toISOString(),
      temperatura: Math.round((baseTemp + tempVariation) * 10) / 10,
      humedad: Math.round(Math.min(95, Math.max(15, baseHum + humVariation)) * 10) / 10,
      campoId: nombreCampo,
      parcelaId: nombreParcela,
    });
  }
  return lecturas;
}

export async function listarSensores(): Promise<Sensor[]> {
  const res = await fetchWithAuth("/api/sensores");
  if (!res.ok) throw new Error("Error al obtener sensores");
  const json = await res.json();
  if (Array.isArray(json)) return json as Sensor[];
  return json.data as Sensor[];
}

export async function listarLecturas(
  nombreCampo: string,
  nombreParcela: string
): Promise<Lectura[]> {
  const res = await fetchWithAuth(
    `/api/campos/${encodeURIComponent(nombreCampo)}/parcelas/${encodeURIComponent(nombreParcela)}/lecturas`
  );
  if (!res.ok) return mockLecturas(nombreCampo, nombreParcela);
  const json = await res.json();
  const data = json.data as Lectura[] | undefined;
  if (!data || data.length === 0) return mockLecturas(nombreCampo, nombreParcela);
  return data;
}
