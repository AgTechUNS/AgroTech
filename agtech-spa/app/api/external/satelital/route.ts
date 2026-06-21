import { NextRequest, NextResponse } from "next/server";
import { getUserFromRequest } from "@/lib/auth/token";
import { proxyToBackend } from "@/lib/proxy";
import { SatelitalData } from "@/lib/types";
import { mockNdvi, mockHumedadSuelo } from "@/lib/utils/hash";

const BACKEND_URL = process.env.BACKEND_URL;

export async function GET(request: NextRequest) {
  const proxy = await proxyToBackend(request, "/external/satelital", "GET");
  if (proxy && proxy.status < 400) return proxy;
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

  if (BACKEND_URL) {
    try {
      const targetUrl = new URL(`${BACKEND_URL}/external/satelital`);
      targetUrl.search = request.nextUrl.search;
      const headers: Record<string, string> = { "Content-Type": "application/json" };
      const auth = request.headers.get("Authorization");
      if (auth) headers["Authorization"] = auth;
      const res = await fetch(targetUrl.toString(), { headers });
      if (res.ok) {
        const data = await res.json();
        return NextResponse.json(data);
      }
    } catch {
      // fallback a mock si el backend no responde
    }
  }

  const nombreParcela = searchParams.get("nombre_parcela") ?? "";
  const nombreCampo = searchParams.get("nombre_campo") ?? "";
  const seed = nombreParcela ? `${nombreParcela}:${nombreCampo}` : coordenadas;

  const data: SatelitalData = {
    ndvi: mockNdvi(seed),
    humedad_suelo_estimada: mockHumedadSuelo(seed),
  };

  return NextResponse.json(data);
}
