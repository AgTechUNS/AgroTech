import { NextRequest, NextResponse } from "next/server";
import { readCampos, addCampo } from "@/lib/data/store";
import { getUserFromRequest, getAdminEmail, requireAdmin } from "@/lib/auth/token";
import { proxyToBackend } from "@/lib/proxy";

export async function GET(request: NextRequest) {
  const proxy = await proxyToBackend(request, "/api/campos", "GET");
  if (proxy) return proxy;

  const user = getUserFromRequest(request);
  if (!user) {
    return NextResponse.json({ error: { code: "UNAUTHORIZED", message: "No autenticado" } }, { status: 401 });
  }
  const adminEmail = getAdminEmail(user);

  const { searchParams } = new URL(request.url);
  const page = parseInt(searchParams.get("page") ?? "1", 10);
  const limit = parseInt(searchParams.get("limit") ?? "20", 10);

  const campos = readCampos(adminEmail);
  const total = campos.length;
  const totalPages = Math.max(1, Math.ceil(total / limit));
  const start = (page - 1) * limit;
  const data = campos.slice(start, start + limit);

  return NextResponse.json({
    data,
    pagination: { page, limit, total, totalPages },
  });
}

export async function POST(request: NextRequest) {
  const proxy = await proxyToBackend(request, "/api/campos", "POST");
  if (proxy) return proxy;

  const user = requireAdmin(request);
  if (!user) {
    return NextResponse.json({ error: { code: "FORBIDDEN", message: "Solo administradores" } }, { status: 403 });
  }
  const adminEmail = getAdminEmail(user);

  try {
    const body = await request.json();
    const { nombreCampo, descripcionCampo, coordenadasCampo } = body;

    if (!nombreCampo || !coordenadasCampo) {
      return NextResponse.json(
        { error: { code: "VALIDATION_ERROR", message: "nombreCampo y coordenadasCampo son obligatorios" } },
        { status: 400 }
      );
    }

    const campos = readCampos();
    const existe = campos.find((c) => c.nombreCampo === nombreCampo);
    if (existe) {
      return NextResponse.json(
        { error: { code: "CONFLICT", message: "Ya existe un campo con ese nombre" } },
        { status: 409 }
      );
    }

    addCampo({ nombreCampo, descripcionCampo, coordenadasCampo, adminEmail });

    return NextResponse.json(
      { message: "Campo creado exitosamente" },
      { status: 201, headers: { Location: `/campos/${encodeURIComponent(nombreCampo)}` } }
    );
  } catch {
    return NextResponse.json(
      { error: { code: "UNKNOWN_ERROR", message: "Error al procesar la solicitud" } },
      { status: 500 }
    );
  }
}
