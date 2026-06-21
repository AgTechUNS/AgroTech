import { NextRequest, NextResponse } from "next/server";
import { getUserFromRequest } from "@/lib/auth/token";
import { proxyToBackend } from "@/lib/proxy";
import { Prediccion } from "@/lib/types";
import { hash, mockNdvi } from "@/lib/utils/hash";

export async function GET(
  request: NextRequest,
  { params }: { params: { nombreCampo: string; nombreParcela: string } }
) {
  const proxy = await proxyToBackend(request, `/campos/${params.nombreCampo}/parcelas/${params.nombreParcela}/predicciones`, "GET");
  if (proxy && proxy.status < 400) return proxy;
  const user = getUserFromRequest(request);
  if (!user) {
    return NextResponse.json({ error: { code: "UNAUTHORIZED", message: "No autenticado" } }, { status: 401 });
  }

  const nombreParcela = decodeURIComponent(params.nombreParcela);
  const nombreCampo = decodeURIComponent(params.nombreCampo);
  const seed = `${nombreParcela}:${nombreCampo}`;
  const s = hash(seed);
  const ahora = new Date();

  const tendencia = s % 3 === 0 ? "a la baja" : s % 3 === 1 ? "estable" : "al alza";
  const magnitud = ((s % 20) - 10) / 10;
  const signo = magnitud >= 0 ? "+" : "";
  const tempMax = 30 + (s % 12);
  const tempMin = 18 + (s % 8);
  const humedadEst = 30 + (s % 35);
  const probLluvia = s % 101;
  const ndviEst = mockNdvi(seed).toFixed(2);

  const partes: string[] = [];

  partes.push(`Tendencia ${tendencia} detectada (${signo}${magnitud.toFixed(1)})`);

  if (tendencia === "a la baja") {
    partes.push(`descenso de temperatura estimado: min ${tempMin}°C / max ${tempMax}°C`);
  } else if (tendencia === "al alza") {
    partes.push(`aumento térmico progresivo: min ${tempMin}°C / max ${tempMax}°C`);
  } else {
    partes.push(`temperatura estable: min ${tempMin}°C / max ${tempMax}°C`);
  }

  if (ndviEst < "0.30") {
    partes.push(`NDVI bajo (${ndviEst}): posible estrés vegetal, monitorear cultivo`);
  } else if (ndviEst > "0.60") {
    partes.push(`NDVI alto (${ndviEst}): vegetación saludable`);
  } else {
    partes.push(`NDVI dentro de rango normal (${ndviEst})`);
  }

  if (humedadEst < 30) {
    partes.push("ambiente seco, monitorear riego");
  } else if (humedadEst > 70) {
    partes.push("alta humedad ambiental, vigilancia fitosanitaria recomendada");
  } else {
    partes.push("humedad ambiental dentro de parámetros normales");
  }

  if (probLluvia >= 70) {
    partes.push(`probabilidad de lluvia significativa: ${probLluvia}%, considerar postergar labores`);
  } else if (probLluvia >= 40) {
    partes.push(`probabilidad de lluvia moderada: ${probLluvia}%`);
  }

  const fechaFin = new Date(ahora.getTime() + 3 * 86400000);
  partes.push(`para ${nombreParcela} entre ${ahora.toISOString().split("T")[0]} y ${fechaFin.toISOString().split("T")[0]}`);

  const mockPrediction: Prediccion = {
    fechaEmision: ahora.toISOString(),
    resultado: partes.join(". "),
    fechaIni: ahora.toISOString(),
    fechaFin: fechaFin.toISOString(),
  };

  return NextResponse.json({ data: [mockPrediction], pagination: { page: 1, limit: 20, total: 1, totalPages: 1 } });
}
