import { NextRequest, NextResponse } from "next/server";
import { proxyToBackend } from "@/lib/proxy";

export async function GET(request: NextRequest) {
  const proxy = await proxyToBackend(request, "/api/cultivos/catalogo", "GET");
  return proxy ?? NextResponse.json(
    { error: { code: "SERVICE_UNAVAILABLE", message: "Backend no disponible" } },
    { status: 502 }
  );
}
