import { NextRequest, NextResponse } from "next/server";
import { readCatalogo } from "@/lib/data/store";
import { getUserFromRequest } from "@/lib/auth/token";
import { proxyToBackend } from "@/lib/proxy";

export async function GET(request: NextRequest) {
  const proxy = await proxyToBackend(request, "/api/cultivos/catalogo", "GET");
  if (proxy) return proxy;
  const user = getUserFromRequest(request);
  if (!user) {
    return NextResponse.json({ error: { code: "UNAUTHORIZED", message: "No autenticado" } }, { status: 401 });
  }
  return NextResponse.json(readCatalogo());
}
