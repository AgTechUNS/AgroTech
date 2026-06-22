import { NextRequest, NextResponse } from "next/server";
import { requireRole } from "@/lib/auth/token";
import { proxyToBackend } from "@/lib/proxy";

export async function GET(request: NextRequest) {
  const proxy = await proxyToBackend(request, "/api/reglas", "GET");
  return proxy ?? NextResponse.json(
    { error: { code: "SERVICE_UNAVAILABLE", message: "Backend no disponible" } },
    { status: 502 }
  );
}

export async function POST(request: NextRequest) {
  const user = requireRole(request, ["ADMIN", "AGRONOMO"]);
  if (!user) {
    return NextResponse.json({ error: { code: "FORBIDDEN", message: "No autorizado" } }, { status: 403 });
  }

  const proxy = await proxyToBackend(request, "/api/reglas", "POST");
  return proxy ?? NextResponse.json(
    { error: { code: "SERVICE_UNAVAILABLE", message: "Backend no disponible" } },
    { status: 502 }
  );
}
