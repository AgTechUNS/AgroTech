import { NextRequest, NextResponse } from "next/server";
import { getUserFromRequest } from "@/lib/auth/token";
import { SatelitalData } from "@/lib/types";

export async function GET(request: NextRequest) {
  const user = getUserFromRequest(request);
  if (!user) {
    return NextResponse.json({ error: { code: "UNAUTHORIZED", message: "No autenticado" } }, { status: 401 });
  }

  const { searchParams } = new URL(request.url);
  const coordenadas = searchParams.get("coordenadas");
  if (!coordenadas) {
    return NextResponse.json(
      { error: { code: "VALIDATION_ERROR", message: "coordenadas es requerido" } },
      { status: 400 }
    );
  }

  const data: SatelitalData = {
    ndvi: Math.round((0.5 + Math.random() * 0.5) * 100) / 100,
    humedad_suelo_estimada: Math.round((20 + Math.random() * 50) * 10) / 10,
  };

  return NextResponse.json(data);
}
