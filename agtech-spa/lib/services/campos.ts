import { Campo, PaginatedResponse } from "@/lib/types";
import { fetchWithAuth } from "@/lib/auth";

export async function listarCampos(
  page = 1,
  limit = 20
): Promise<PaginatedResponse<Campo>> {
  const res = await fetchWithAuth(`/api/campos?page=${page}&limit=${limit}`);
  if (!res.ok) throw new Error("Error al obtener campos");
  return res.json();
}

export async function obtenerCampo(nombreCampo: string): Promise<Campo> {
  const res = await fetchWithAuth(`/api/campos/${encodeURIComponent(nombreCampo)}`);
  if (!res.ok) throw new Error("Error al obtener el campo");
  return res.json();
}

export interface CrearCampoPayload {
  nombreCampo: string;
  descripcionCampo?: string;
  coordenadasCampo: string;
}

export async function crearCampo(payload: CrearCampoPayload): Promise<void> {
  const res = await fetchWithAuth("/api/campos", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => null);
    const msg = body?.error?.message ?? "Error al crear el campo";
    throw new Error(msg);
  }
}

export interface EditarCampoPayload {
  descripcionCampo?: string;
  coordenadasCampo: string;
}

export async function editarCampo(nombreCampo: string, payload: EditarCampoPayload): Promise<void> {
  const res = await fetchWithAuth(`/api/campos/${encodeURIComponent(nombreCampo)}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new Error(body?.error?.message ?? "Error al editar el campo");
  }
}

export async function eliminarCampo(nombreCampo: string): Promise<void> {
  const res = await fetchWithAuth(`/api/campos/${encodeURIComponent(nombreCampo)}`, {
    method: "DELETE",
  });
  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new Error(body?.error?.message ?? "Error al eliminar el campo");
  }
}
