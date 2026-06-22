import { NextRequest, NextResponse } from "next/server";
import { proxyToBackend } from "@/lib/proxy";

export async function GET(
  request: NextRequest,
  { params }: { params: { nombreCampo: string; nombreParcela: string } }
) {
  const proxy = await proxyToBackend(request, `/api/campos/${params.nombreCampo}/parcelas/${params.nombreParcela}/predicciones`, "GET");
  if (proxy) return proxy;
  return NextResponse.json({ data: [], pagination: { page: 1, limit: 20, total: 0, totalPages: 1 } });
}
