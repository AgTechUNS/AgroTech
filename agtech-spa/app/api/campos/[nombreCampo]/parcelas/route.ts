import { NextRequest, NextResponse } from "next/server";
import { requireAdmin } from "@/lib/auth/token";
import { proxyToBackend } from "@/lib/proxy";

export async function GET(
  request: NextRequest,
  { params }: { params: { nombreCampo: string } }
) {
  const proxy = await proxyToBackend(request, `/api/campos/${params.nombreCampo}/parcelas`, "GET");
  return proxy ?? NextResponse.json(
    { error: { code: "SERVICE_UNAVAILABLE", message: "Backend no disponible" } },
    { status: 502 }
  );
}

export async function POST(
  request: NextRequest,
  { params }: { params: { nombreCampo: string } }
) {
  const user = requireAdmin(request);
  if (!user) {
    return NextResponse.json({ error: { code: "FORBIDDEN", message: "Solo administradores" } }, { status: 403 });
  }

  const proxy = await proxyToBackend(request, `/api/campos/${params.nombreCampo}/parcelas`, "POST");
  return proxy ?? NextResponse.json(
    { error: { code: "SERVICE_UNAVAILABLE", message: "Backend no disponible" } },
    { status: 502 }
  );
}
