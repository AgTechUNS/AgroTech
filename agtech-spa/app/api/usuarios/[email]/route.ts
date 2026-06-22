import { NextRequest, NextResponse } from "next/server";
import { requireAdmin } from "@/lib/auth/token";
import { proxyToBackend } from "@/lib/proxy";

export async function PUT(
  request: NextRequest,
  { params }: { params: { email: string } }
) {
  const user = requireAdmin(request);
  if (!user) {
    return NextResponse.json({ error: { code: "FORBIDDEN", message: "Solo administradores" } }, { status: 403 });
  }

  const proxy = await proxyToBackend(request, `/api/usuarios/${params.email}`, "PUT");
  return proxy ?? NextResponse.json(
    { error: { code: "SERVICE_UNAVAILABLE", message: "Backend no disponible" } },
    { status: 502 }
  );
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: { email: string } }
) {
  const user = requireAdmin(request);
  if (!user) {
    return NextResponse.json({ error: { code: "FORBIDDEN", message: "Solo administradores" } }, { status: 403 });
  }

  const proxy = await proxyToBackend(request, `/api/usuarios/${params.email}`, "DELETE");
  return proxy ?? NextResponse.json(
    { error: { code: "SERVICE_UNAVAILABLE", message: "Backend no disponible" } },
    { status: 502 }
  );
}
