import { NextRequest, NextResponse } from "next/server";
import { getUserFromRequest } from "@/lib/auth/token";
import { proxyToBackend } from "@/lib/proxy";
import { AlertaRecomendacion } from "@/lib/types";

export async function GET(
  request: NextRequest,
  { params }: { params: { nombreCampo: string; nombreParcela: string } }
) {
  const proxy = await proxyToBackend(request, `/campos/${params.nombreCampo}/parcelas/${params.nombreParcela}/recomendaciones`, "GET");
  if (proxy && proxy.status < 400) {
    const body = await proxy.clone().json();
    if (body.data && body.data.length > 0) return proxy;
  }
  const user = getUserFromRequest(request);
  if (!user) {
    return NextResponse.json({ error: { code: "UNAUTHORIZED", message: "No autenticado" } }, { status: 401 });
  }

  const nombreParcela = decodeURIComponent(params.nombreParcela);
  const nombreCampo = decodeURIComponent(params.nombreCampo);
  const mockData: AlertaRecomendacion[] = [
    {
      tipo: "ALERTA_TIEMPO_REAL",
      fechaEmision: new Date().toISOString(),
      mensaje: `Riesgo de estrés hídrico en ${nombreParcela} (${nombreCampo}): humedad promedio 18.3% por debajo del umbral 25.0%. Se recomienda ajustar el riego a 35mm en las próximas 48 horas.`,
      nombreParcela,
      emailUsuario: user.email,
    },
    {
      tipo: "RECOMENDACION_BATCH",
      fechaEmision: new Date(Date.now() - 3600000).toISOString(),
      mensaje: `Reporte diario — ${nombreParcela}: temperatura máxima 34.2°C, humedad mínima 22%. Riesgo de estrés térmico en horas pico (12-16h). Monitorear cultivo y considerar cobertura con malla media sombra.`,
      nombreParcela,
      emailUsuario: user.email,
    },
    {
      tipo: "ALERTA_TIEMPO_REAL",
      fechaEmision: new Date(Date.now() - 7200000).toISOString(),
      mensaje: `Alerta de calor extremo en ${nombreParcela}: temperatura sostenida > 38°C detectada en los últimos 30 minutos. Riesgo de daño foliar. Activar riego por aspersión de emergencia.`,
      nombreParcela,
      emailUsuario: user.email,
    },
  ];

  return NextResponse.json({
    data: mockData,
    pagination: { page: 1, limit: 20, total: mockData.length, totalPages: 1 },
  });
}
