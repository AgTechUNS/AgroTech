import { Regla, PaginatedResponse } from "@/lib/types";
import { fetchWithAuth } from "@/lib/auth";

export async function listarReglas(page = 1, limit = 50, nombreCampo?: string): Promise<PaginatedResponse<Regla>> {
  const params = new URLSearchParams({ page: String(page), limit: String(limit) });
  if (nombreCampo) params.set("nombreCampo", nombreCampo);
  const res = await fetchWithAuth(`/api/reglas?${params}`);
  if (!res.ok) throw new Error("Error al obtener reglas");
  return res.json();
}

export interface CrearReglaPayload {
  nombre: string;
  descripcion: string;
  metrica: string;
  operador: string;
  umbral: number;
  nombreCampo: string;
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

export async function obtenerRegla(id: string): Promise<Regla> {
  const res = await fetchWithAuth(`/api/reglas/${encodeURIComponent(id)}`);
  if (!res.ok) throw new Error("Error al obtener la regla");
  return res.json();
}

export interface EditarReglaPayload {
  nombre?: string;
  descripcion?: string;
  metrica?: string;
  operador?: string;
  umbral?: number;
  nombreCampo?: string;
  habilitada?: boolean;
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
