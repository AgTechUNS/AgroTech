import { Regla } from "@/lib/types";
import { fetchWithAuth } from "@/lib/auth";

export interface CrearReglaPayload {
  nombre: string;
  descripcion?: string;
  metrica: string;
  operador: string;
  valor: number;
  camposAsignados?: string[];
}

export interface EditarReglaPayload {
  nombre?: string;
  descripcion?: string;
  metrica?: string;
  operador?: string;
  valor?: number;
  camposAsignados?: string[];
}

export async function listarReglas(): Promise<Regla[]> {
  const res = await fetchWithAuth("/api/reglas");
  if (!res.ok) throw new Error("Error al obtener reglas");
  const json = await res.json();
  if (Array.isArray(json)) return json as Regla[];
  return json.data as Regla[];
}

export async function obtenerRegla(id: string): Promise<Regla> {
  const res = await fetchWithAuth(`/api/reglas/${encodeURIComponent(id)}`);
  if (!res.ok) throw new Error("Error al obtener la regla");
  return res.json();
}

export async function crearRegla(payload: CrearReglaPayload): Promise<void> {
  const res = await fetchWithAuth("/api/reglas", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new Error(body?.error?.message ?? "Error al crear la regla");
  }
}

export async function editarRegla(id: string, payload: EditarReglaPayload): Promise<void> {
  const res = await fetchWithAuth(`/api/reglas/${encodeURIComponent(id)}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new Error(body?.error?.message ?? "Error al editar la regla");
  }
}

export async function eliminarRegla(id: string): Promise<void> {
  const res = await fetchWithAuth(`/api/reglas/${encodeURIComponent(id)}`, {
    method: "DELETE",
  });
  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new Error(body?.error?.message ?? "Error al eliminar la regla");
  }
}
