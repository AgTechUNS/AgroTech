import { NextRequest, NextResponse } from "next/server";
import { requireRole } from "@/lib/auth/token";
import { proxyToBackend } from "@/lib/proxy";

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  const proxy = await proxyToBackend(request, `/api/reglas/${params.id}`, "GET");
  return proxy ?? NextResponse.json(
    { error: { code: "SERVICE_UNAVAILABLE", message: "Backend no disponible" } },
    { status: 502 }
  );
}

export async function PUT(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  const user = requireRole(request, ["ADMIN", "AGRONOMO"]);
  if (!user) {
    return NextResponse.json({ error: { code: "FORBIDDEN", message: "No autorizado" } }, { status: 403 });
  }

  const proxy = await proxyToBackend(request, `/api/reglas/${params.id}`, "PUT");
  return proxy ?? NextResponse.json(
    { error: { code: "SERVICE_UNAVAILABLE", message: "Backend no disponible" } },
    { status: 502 }
  );
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  const user = requireRole(request, ["ADMIN", "AGRONOMO"]);
  if (!user) {
    return NextResponse.json({ error: { code: "FORBIDDEN", message: "No autorizado" } }, { status: 403 });
  }

  const proxy = await proxyToBackend(request, `/api/reglas/${params.id}`, "DELETE");
  return proxy ?? NextResponse.json(
    { error: { code: "SERVICE_UNAVAILABLE", message: "Backend no disponible" } },
    { status: 502 }
  );
}
