import { NextRequest, NextResponse } from "next/server";
import { requireAdmin } from "@/lib/auth/token";
import { proxyToBackend } from "@/lib/proxy";

export async function GET(
  request: NextRequest,
  { params }: { params: { nombreCampo: string; nombreParcela: string } }
) {
  const proxy = await proxyToBackend(request, `/api/campos/${params.nombreCampo}/parcelas/${params.nombreParcela}`, "GET");
  return proxy ?? NextResponse.json(
    { error: { code: "SERVICE_UNAVAILABLE", message: "Backend no disponible" } },
    { status: 502 }
  );
}

export async function PUT(
  request: NextRequest,
  { params }: { params: { nombreCampo: string; nombreParcela: string } }
) {
  const user = requireAdmin(request);
  if (!user) {
    return NextResponse.json({ error: { code: "FORBIDDEN", message: "Solo administradores" } }, { status: 403 });
  }

  const proxy = await proxyToBackend(request, `/api/campos/${params.nombreCampo}/parcelas/${params.nombreParcela}`, "PUT");
  return proxy ?? NextResponse.json(
    { error: { code: "SERVICE_UNAVAILABLE", message: "Backend no disponible" } },
    { status: 502 }
  );
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: { nombreCampo: string; nombreParcela: string } }
) {
  const user = requireAdmin(request);
  if (!user) {
    return NextResponse.json({ error: { code: "FORBIDDEN", message: "Solo administradores" } }, { status: 403 });
  }

  const proxy = await proxyToBackend(request, `/api/campos/${params.nombreCampo}/parcelas/${params.nombreParcela}`, "DELETE");
  return proxy ?? NextResponse.json(
    { error: { code: "SERVICE_UNAVAILABLE", message: "Backend no disponible" } },
    { status: 502 }
  );
}
