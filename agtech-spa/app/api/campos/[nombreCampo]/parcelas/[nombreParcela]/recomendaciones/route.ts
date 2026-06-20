import { NextRequest, NextResponse } from "next/server";
import { getUserFromRequest } from "@/lib/auth/token";
import { AlertaRecomendacion } from "@/lib/types";

export async function GET(
  _request: NextRequest,
  { params }: { params: { nombreCampo: string; nombreParcela: string } }
) {
  const user = getUserFromRequest(_request);
  if (!user) {
    return NextResponse.json({ error: { code: "UNAUTHORIZED", message: "No autenticado" } }, { status: 401 });
  }

  const nombreParcela = decodeURIComponent(params.nombreParcela);
  const mockData: AlertaRecomendacion[] = [
    {
      tipo: "ALERTA_TIEMPO_REAL",
      fechaEmision: new Date().toISOString(),
      mensaje: "Riesgo de estrés hídrico detectado por baja humedad sostenida.",
      nombreParcela,
      emailUsuario: user.email,
    },
    {
      tipo: "RECOMENDACION_BATCH",
      fechaEmision: new Date(Date.now() - 3600000).toISOString(),
      mensaje: "Se recomienda ajustar el riego a 30mm en los próximos 3 días.",
      nombreParcela,
      emailUsuario: user.email,
    },
  ];

  return NextResponse.json({
    data: mockData,
    pagination: { page: 1, limit: 20, total: mockData.length, totalPages: 1 },
  });
}
