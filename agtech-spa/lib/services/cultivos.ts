import { Cultivo, PaginatedResponse } from "@/lib/types";

export async function listarCultivos(page = 1, limit = 50): Promise<PaginatedResponse<Cultivo>> {
  const res = await fetch(`/api/cultivos?page=${page}&limit=${limit}`);
  if (!res.ok) throw new Error("Error al obtener cultivos");
  return res.json();
}

export interface CrearCultivoPayload {
  nombreCultivo: string;
  umbralHumedadMinima: number;
}

export async function crearCultivo(payload: CrearCultivoPayload): Promise<void> {
  const res = await fetch("/api/cultivos", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new Error(body?.error?.message ?? "Error al crear el cultivo");
  }
}
