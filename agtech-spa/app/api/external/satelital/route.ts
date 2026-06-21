import { NextRequest, NextResponse } from "next/server";
import { getUserFromRequest } from "@/lib/auth/token";
import { proxyToBackend } from "@/lib/proxy";
import { SatelitalData } from "@/lib/types";

const BACKEND_URL = process.env.BACKEND_URL;

export async function GET(request: NextRequest) {
  const proxy = await proxyToBackend(request, "/api/external/satelital", "GET");
  if (proxy) return proxy;
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

  const data: SatelitalData = {
    ndvi: Math.round((0.5 + Math.random() * 0.5) * 100) / 100,
    humedad_suelo_estimada: Math.round((20 + Math.random() * 50) * 10) / 10,
  };

  return NextResponse.json(data);
}
