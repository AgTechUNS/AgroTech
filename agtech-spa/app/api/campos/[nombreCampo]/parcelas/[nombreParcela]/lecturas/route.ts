import { NextRequest, NextResponse } from "next/server";
import { proxyToBackend } from "@/lib/proxy";

export async function GET(
  request: NextRequest,
  { params }: { params: { nombreCampo: string; nombreParcela: string } }
) {
  const proxy = await proxyToBackend(request, `/campos/${params.nombreCampo}/parcelas/${params.nombreParcela}/lecturas`, "GET");
  if (proxy && proxy.status < 400) return proxy;
  return NextResponse.json({
    data: [
      {
        temperatura: 999,
        humedad: -1,
        timestamp: new Date().toISOString(),
        deviceId: "[MOCK] SNS-000",
      },
    ],
  });
}
