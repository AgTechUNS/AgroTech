import { Campo, PaginatedResponse } from "@/lib/types";

export async function listarCampos(
  page = 1,
  limit = 20
): Promise<PaginatedResponse<Campo>> {
  const res = await fetch(`/api/campos?page=${page}&limit=${limit}`);
  if (!res.ok) throw new Error("Error al obtener campos");
  return res.json();
}

export interface CrearCampoPayload {
  nombreCampo: string;
  descripcionCampo?: string;
  coordenadasCampo: string;
}

export async function crearCampo(payload: CrearCampoPayload): Promise<void> {
  const res = await fetch("/api/campos", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => null);
    const msg = body?.error?.message ?? "Error al crear el campo";
    throw new Error(msg);
  }
}
