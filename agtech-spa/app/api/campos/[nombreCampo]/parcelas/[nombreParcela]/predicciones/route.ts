import { NextRequest, NextResponse } from "next/server";
import { getUserFromRequest } from "@/lib/auth/token";
import { proxyToBackend } from "@/lib/proxy";
import { Prediccion } from "@/lib/types";

export async function GET(
  request: NextRequest,
  { params }: { params: { nombreCampo: string; nombreParcela: string } }
) {
  const proxy = await proxyToBackend(request, `/api/campos/${params.nombreCampo}/parcelas/${params.nombreParcela}/predicciones`, "GET");
  if (proxy) return proxy;
  const user = getUserFromRequest(request);
  if (!user) {
    return NextResponse.json({ error: { code: "UNAUTHORIZED", message: "No autenticado" } }, { status: 401 });
  }

  const nombreParcela = decodeURIComponent(params.nombreParcela);
  const hoy = new Date();
  const mockPredictions: Prediccion[] = Array.from({ length: 5 }, (_, i) => {
    const fecha = new Date(hoy);
    fecha.setDate(fecha.getDate() + i + 1);
    return {
      nombreParcela,
      fecha: fecha.toISOString().split("T")[0],
      temperatura_estimada: Math.round((18 + Math.random() * 10) * 10) / 10,
      humedad_estimada: Math.round((40 + Math.random() * 40) * 10) / 10,
      probabilidad_lluvia: Math.round(Math.random() * 100),
    };
  });

  return NextResponse.json({ data: mockPredictions });
}
