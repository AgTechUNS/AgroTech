import { Regla, PaginatedResponse } from "@/lib/types";

export async function listarReglas(page = 1, limit = 50): Promise<PaginatedResponse<Regla>> {
  const res = await fetch(`/api/reglas?page=${page}&limit=${limit}`);
  if (!res.ok) throw new Error("Error al obtener reglas");
  return res.json();
}

export interface CrearReglaPayload {
  metrica: string;
  operador: string;
  valor: number;
}

export async function crearRegla(payload: CrearReglaPayload): Promise<void> {
  const res = await fetch("/api/reglas", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new Error(body?.error?.message ?? "Error al crear la regla");
  }
}
