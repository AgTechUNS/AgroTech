import { Cultivo, CatalogoCultivo, PaginatedResponse } from "@/lib/types";
import { fetchWithAuth } from "@/lib/auth";

export async function listarCultivos(page = 1, limit = 50): Promise<PaginatedResponse<Cultivo>> {
  const res = await fetchWithAuth(`/api/cultivos?page=${page}&limit=${limit}`);
  if (!res.ok) throw new Error("Error al obtener cultivos");
  return res.json();
}

export async function listarCatalogoCultivos(): Promise<CatalogoCultivo[]> {
  const res = await fetchWithAuth("/api/cultivos/catalogo");
  if (!res.ok) throw new Error("Error al obtener catálogo de cultivos");
  return res.json();
}

export interface CrearCultivoPayload {
  nombreCultivo: string;
  variedad: string;
}

export async function crearCultivo(payload: CrearCultivoPayload): Promise<void> {
  const res = await fetchWithAuth("/api/cultivos", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new Error(body?.error?.message ?? "Error al crear el cultivo");
  }
}
