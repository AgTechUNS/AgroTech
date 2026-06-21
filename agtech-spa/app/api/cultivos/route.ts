import { NextRequest, NextResponse } from "next/server";
import { readCultivos, addCultivo } from "@/lib/data/store";
import { getUserFromRequest, getAdminEmail, requireAdmin } from "@/lib/auth/token";
import { proxyToBackend } from "@/lib/proxy";

export async function GET(request: NextRequest) {
  const proxy = await proxyToBackend(request, "/api/cultivos", "GET");
  if (proxy) return proxy;
  const user = getUserFromRequest(request);
  if (!user) {
    return NextResponse.json({ error: { code: "UNAUTHORIZED", message: "No autenticado" } }, { status: 401 });
  }
  const adminEmail = getAdminEmail(user);

  const { searchParams } = new URL(request.url);
  const page = parseInt(searchParams.get("page") ?? "1", 10);
  const limit = parseInt(searchParams.get("limit") ?? "50", 10);
  const cultivos = readCultivos(adminEmail);
  const total = cultivos.length;
  const totalPages = Math.max(1, Math.ceil(total / limit));
  const start = (page - 1) * limit;

  return NextResponse.json({
    data: cultivos.slice(start, start + limit),
    pagination: { page, limit, total, totalPages },
  });
}

export async function POST(request: NextRequest) {
  const proxy = await proxyToBackend(request, "/api/cultivos", "POST");
  if (proxy) return proxy;
  const user = requireAdmin(request);
  if (!user) {
    return NextResponse.json({ error: { code: "FORBIDDEN", message: "Solo administradores" } }, { status: 403 });
  }
  const adminEmail = getAdminEmail(user);

  try {
    const body = await request.json();
    const { nombreCultivo, variedad } = body;

    if (!nombreCultivo || !variedad) {
      return NextResponse.json(
        { error: { code: "VALIDATION_ERROR", message: "nombreCultivo y variedad son obligatorios" } },
        { status: 400 }
      );
    }

    const cultivos = readCultivos(adminEmail);
    const existe = cultivos.find((c) => c.nombreCultivo === nombreCultivo && c.variedad === variedad);
    if (existe) {
      return NextResponse.json(
        { error: { code: "CONFLICT", message: "Ya existe esa variedad de cultivo" } },
        { status: 409 }
      );
    }

    addCultivo({ nombreCultivo, variedad, adminEmail });
    return NextResponse.json({ message: "Cultivo creado exitosamente" }, { status: 201 });
  } catch {
    return NextResponse.json(
      { error: { code: "UNKNOWN_ERROR", message: "Error al procesar la solicitud" } },
      { status: 500 }
    );
  }
}
