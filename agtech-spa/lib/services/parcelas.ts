import { Parcela, PaginatedResponse } from "@/lib/types";
import { fetchWithAuth } from "@/lib/auth";

export async function listarParcelas(
  nombreCampo: string
): Promise<PaginatedResponse<Parcela>> {
  const res = await fetchWithAuth(`/api/campos/${encodeURIComponent(nombreCampo)}/parcelas`);
  if (!res.ok) throw new Error("Error al obtener parcelas");
  return res.json();
}

export async function obtenerParcela(nombreCampo: string, nombreParcela: string): Promise<Parcela> {
  const res = await fetchWithAuth(
    `/api/campos/${encodeURIComponent(nombreCampo)}/parcelas/${encodeURIComponent(nombreParcela)}`
  );
  if (!res.ok) throw new Error("Error al obtener la parcela");
  return res.json();
}

export interface CrearParcelaPayload {
  nombreParcela: string;
  descripcionParcela?: string;
  coordenadasParcela: string;
  nombreCultivo?: string;
  variedad?: string;
}

export async function crearParcela(
  nombreCampo: string,
  payload: CrearParcelaPayload
): Promise<void> {
  const res = await fetchWithAuth(`/api/campos/${encodeURIComponent(nombreCampo)}/parcelas`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new Error(body?.error?.message ?? "Error al crear la parcela");
  }
}

export interface EditarParcelaPayload {
  descripcionParcela?: string;
  coordenadasParcela: string;
  nombreCultivo?: string;
  variedad?: string;
}

export async function editarParcela(
  nombreCampo: string,
  nombreParcela: string,
  payload: EditarParcelaPayload
): Promise<void> {
  const res = await fetchWithAuth(
    `/api/campos/${encodeURIComponent(nombreCampo)}/parcelas/${encodeURIComponent(nombreParcela)}`,
    { method: "PUT", body: JSON.stringify(payload) }
  );
  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new Error(body?.error?.message ?? "Error al editar la parcela");
  }
}

export async function eliminarParcela(nombreCampo: string, nombreParcela: string): Promise<void> {
  const res = await fetchWithAuth(
    `/api/campos/${encodeURIComponent(nombreCampo)}/parcelas/${encodeURIComponent(nombreParcela)}`,
    { method: "DELETE" }
  );
  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new Error(body?.error?.message ?? "Error al eliminar la parcela");
  }
}
