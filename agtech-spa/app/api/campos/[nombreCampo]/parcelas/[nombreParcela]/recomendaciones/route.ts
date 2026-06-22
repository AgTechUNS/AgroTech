import { NextRequest, NextResponse } from "next/server";
import { getUserFromRequest } from "@/lib/auth/token";
import { proxyToBackend } from "@/lib/proxy";
import { AlertaRecomendacion } from "@/lib/types";
import { hash, mockNdvi } from "@/lib/utils/hash";

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
  const seed = `${nombreParcela}:${nombreCampo}`;
  const s = hash(seed);

  const humedad = (12 + (s % 21)).toFixed(1);
  const temperatura = (30 + (s % 13)).toFixed(1);
  const ndvi = mockNdvi(seed).toFixed(3);
  const ahora = Date.now();

  const alertas: AlertaRecomendacion[] = [];

  if (parseFloat(humedad) < 25) {
    alertas.push({
      tipo: "ALERTA_TIEMPO_REAL",
      fechaEmision: new Date(ahora).toISOString(),
      mensaje: `[MOCK] Riesgo de estrés hídrico en ${nombreParcela} (${nombreCampo}): humedad promedio ${humedad}% por debajo del umbral 25.0%. NDVI actual ${ndvi}. Se recomienda ajustar el riego a ${30 + (s % 20)}mm en las próximas 48 horas.`,
      nombreParcela,
      emailUsuario: user.email,
    });
  }

  if (parseFloat(temperatura) > 38) {
    alertas.push({
      tipo: "ALERTA_TIEMPO_REAL",
      fechaEmision: new Date(ahora - 7200000).toISOString(),
      mensaje: `[MOCK] Alerta de calor extremo en ${nombreParcela}: temperatura sostenida de ${temperatura}°C detectada en los últimos 30 minutos. Humedad ${humedad}%. Riesgo de daño foliar. Activar riego por aspersión de emergencia.`,
      nombreParcela,
      emailUsuario: user.email,
    });
  }

  if (parseFloat(ndvi) < 0.3 && parseFloat(humedad) < 25) {
    alertas.push({
      tipo: "ALERTA_TIEMPO_REAL",
      fechaEmision: new Date(ahora - 3600000).toISOString(),
      mensaje: `[MOCK] Estrés combinado detectado en ${nombreParcela}: NDVI bajo (${ndvi}) y humedad crítica (${humedad}%). Posible pérdida de cobertura vegetal. Evaluar emergencia hídrica.`,
      nombreParcela,
      emailUsuario: user.email,
    });
  }

  alertas.push({
    tipo: "RECOMENDACION_BATCH",
    fechaEmision: new Date(ahora - 3600000).toISOString(),
    mensaje: `[MOCK] Reporte diario — ${nombreParcela}: temperatura máxima ${temperatura}°C, humedad mínima ${humedad}%, NDVI ${ndvi}.${parseFloat(temperatura) > 35 ? " Riesgo de estrés térmico en horas pico (12-16h). Monitorear cultivo y considerar cobertura con malla media sombra." : ""}${parseFloat(temperatura) <= 35 ? " Condiciones térmicas dentro del rango esperado. Ventana favorable para labores culturales." : ""}`,
    nombreParcela,
    emailUsuario: user.email,
  });

  return NextResponse.json({
    data: alertas,
    pagination: { page: 1, limit: 20, total: alertas.length, totalPages: 1 },
  });
}
