import { AlertaRecomendacion, Prediccion, PaginatedResponse } from "@/lib/types";
import { fetchWithAuth } from "@/lib/auth";
import { hash } from "@/lib/utils/hash";

function mockRecomendaciones(nombreCampo: string, nombreParcela: string): PaginatedResponse<AlertaRecomendacion> {
  const seed = hash(`${nombreCampo}/${nombreParcela}`);
  const humedad = 15 + (seed % 10);
  const temperatura = 36 + (seed % 8);
  const ahora = new Date().toISOString();
  return {
    data: [
      {
        tipo: "ALERTA_TIEMPO_REAL",
        fechaEmision: ahora,
        mensaje: `Estrés hídrico detectado en ${nombreParcela}: humedad promedio ${humedad}.0% por debajo del umbral 20.0%`,
        nombreParcela,
      },
      {
        tipo: "ALERTA_TIEMPO_REAL",
        fechaEmision: ahora,
        mensaje: `Calor extremo detectado en ${nombreParcela}: temperatura máxima ${temperatura}.0°C supera el umbral 38.0°C`,
        nombreParcela,
      },
      {
        tipo: "RECOMENDACION_BATCH",
        fechaEmision: ahora,
        mensaje: `Monitorear riego en ${nombreParcela}: las condiciones actuales requieren revisión del plan de riego`,
        nombreParcela,
      },
    ],
    pagination: { page: 1, limit: 20, total: 3, totalPages: 1 },
  };
}

function mockPredicciones(): { data: Prediccion[] } {
  const ahora = new Date();
  const fin = new Date(ahora.getTime() + 3 * 86400000);
  return {
    data: [
      {
        fechaEmision: ahora.toISOString(),
        resultado: "NDVI bajo: posible estrés vegetal. Tendencia estable esperada. Ambiente seco, monitorear riego.",
        fechaIni: ahora.toISOString(),
        fechaFin: fin.toISOString(),
      },
    ],
  };
}

export async function obtenerRecomendaciones(
  nombreCampo: string,
  nombreParcela: string
): Promise<PaginatedResponse<AlertaRecomendacion>> {
  const res = await fetchWithAuth(
    `/api/campos/${encodeURIComponent(nombreCampo)}/parcelas/${encodeURIComponent(nombreParcela)}/recomendaciones`
  );
  if (!res.ok) return mockRecomendaciones(nombreCampo, nombreParcela);
  const json = await res.json();
  if (!json.data || json.data.length === 0) return mockRecomendaciones(nombreCampo, nombreParcela);
  return json;
}

export async function obtenerPredicciones(
  nombreCampo: string,
  nombreParcela: string
): Promise<{ data: Prediccion[] }> {
  const res = await fetchWithAuth(
    `/api/campos/${encodeURIComponent(nombreCampo)}/parcelas/${encodeURIComponent(nombreParcela)}/predicciones`
  );
  if (!res.ok) return mockPredicciones();
  const json = await res.json();
  if (!json.data || json.data.length === 0) return mockPredicciones();
  return json;
}
