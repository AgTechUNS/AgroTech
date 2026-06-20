import { AlertaRecomendacion, Prediccion, PaginatedResponse } from "@/lib/types";
import { fetchWithAuth } from "@/lib/auth";

export async function obtenerRecomendaciones(
  nombreCampo: string,
  nombreParcela: string
): Promise<PaginatedResponse<AlertaRecomendacion>> {
  const res = await fetchWithAuth(
    `/api/campos/${encodeURIComponent(nombreCampo)}/parcelas/${encodeURIComponent(nombreParcela)}/recomendaciones`
  );
  if (!res.ok) throw new Error("Error al obtener recomendaciones");
  return res.json();
}

export async function obtenerPredicciones(
  nombreCampo: string,
  nombreParcela: string
): Promise<{ data: Prediccion[] }> {
  const res = await fetchWithAuth(
    `/api/campos/${encodeURIComponent(nombreCampo)}/parcelas/${encodeURIComponent(nombreParcela)}/predicciones`
  );
  if (!res.ok) throw new Error("Error al obtener predicciones");
  return res.json();
}
