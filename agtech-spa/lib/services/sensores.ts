import { Sensor, Lectura } from "@/lib/types";

export async function listarSensores(): Promise<Sensor[]> {
  const res = await fetch("/api/sensores");
  if (!res.ok) throw new Error("Error al obtener sensores");
  const json = await res.json();
  return json.data as Sensor[];
}

export async function listarLecturas(
  nombreCampo: string,
  nombreParcela: string
): Promise<Lectura[]> {
  const res = await fetch(
    `/api/campos/${encodeURIComponent(nombreCampo)}/parcelas/${encodeURIComponent(nombreParcela)}/lecturas`
  );
  if (!res.ok) throw new Error("Error al obtener lecturas");
  const json = await res.json();
  return json.data as Lectura[];
}
