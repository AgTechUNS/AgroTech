import { Parcela, PaginatedResponse } from "@/lib/types";

export async function listarParcelas(
  nombreCampo: string
): Promise<PaginatedResponse<Parcela>> {
  const res = await fetch(`/api/campos/${encodeURIComponent(nombreCampo)}/parcelas`);
  if (!res.ok) throw new Error("Error al obtener parcelas");
  return res.json();
}

export interface CrearParcelaPayload {
  nombreParcela: string;
  descripcionParcela?: string;
  coordenadasParcela: string;
  nombreCultivo?: string;
}

export async function crearParcela(
  nombreCampo: string,
  payload: CrearParcelaPayload
): Promise<void> {
  const res = await fetch(`/api/campos/${encodeURIComponent(nombreCampo)}/parcelas`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new Error(body?.error?.message ?? "Error al crear la parcela");
  }
}
