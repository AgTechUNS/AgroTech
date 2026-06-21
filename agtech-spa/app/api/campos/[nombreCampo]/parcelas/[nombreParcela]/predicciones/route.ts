import { NextRequest, NextResponse } from "next/server";
import { getUserFromRequest } from "@/lib/auth/token";
import { proxyToBackend } from "@/lib/proxy";
import { Prediccion } from "@/lib/types";

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
  const ahora = new Date();
  const mockPrediction: Prediccion = {
    fechaEmision: ahora.toISOString(),
    resultado: `Tendencia estable detectada (+0.5), condiciones normales para ${nombreParcela}. NDVI dentro de rango normal. Ambiente seco, monitorear riego. para ${nombreParcela} entre ${ahora.toISOString().split("T")[0]} y ${new Date(ahora.getTime() + 3 * 86400000).toISOString().split("T")[0]}`,
    fechaIni: ahora.toISOString(),
    fechaFin: new Date(ahora.getTime() + 3 * 86400000).toISOString(),
  };

  return NextResponse.json({ data: [mockPrediction], pagination: { page: 1, limit: 20, total: 1, totalPages: 1 } });
}
