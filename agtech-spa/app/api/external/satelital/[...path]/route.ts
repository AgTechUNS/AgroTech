import { NextRequest, NextResponse } from "next/server";
import { proxyToBackend } from "@/lib/proxy";

export async function GET(request: NextRequest, { params }: { params: { path: string[] } }) {
  const backendPath = `/external/satelital/${params.path.join("/")}`;
  const proxy = await proxyToBackend(request, backendPath, "GET");
  if (proxy && proxy.status < 400) return proxy;

  const { searchParams } = new URL(request.url);
  const nombreParcela = searchParams.get("nombre_parcela");
  const nombreCampo = searchParams.get("nombre_campo");

  const BACKEND_URL = process.env.BACKEND_URL;
  if (BACKEND_URL) {
    try {
      const targetUrl = new URL(`${BACKEND_URL}${backendPath}`);
      targetUrl.search = request.nextUrl.search;
      const headers: Record<string, string> = { "Content-Type": "application/json" };
      const auth = request.headers.get("Authorization");
      if (auth) headers["Authorization"] = auth;
      const res = await fetch(targetUrl.toString(), { headers });
      if (res.ok) return NextResponse.json(await res.json());
    } catch {
      // fallback
    }
  }

  if (params.path[0] === "historial" && nombreParcela) {
    return NextResponse.json({ data: [{ ndvi: -999, fecha: new Date().toISOString(), nombreParcela }] });
  }
  if (params.path[0] === "campo" && nombreCampo) {
    return NextResponse.json({ data: [{ ndvi: -999, nombreCampo }] });
  }
  return NextResponse.json(
    { error: { code: "NOT_FOUND", message: "Ruta no encontrada" } },
    { status: 404 }
  );
}
