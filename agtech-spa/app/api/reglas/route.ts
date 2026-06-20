import { NextRequest, NextResponse } from "next/server";
import { readReglas, addRegla } from "@/lib/data/store";
import { getUserFromRequest, getAdminEmail, requireAdmin } from "@/lib/auth/token";

export async function GET(request: NextRequest) {
  const user = getUserFromRequest(request);
  if (!user) {
    return NextResponse.json({ error: { code: "UNAUTHORIZED", message: "No autenticado" } }, { status: 401 });
  }
  const adminEmail = getAdminEmail(user);

  const { searchParams } = new URL(request.url);
  const page = parseInt(searchParams.get("page") ?? "1", 10);
  const limit = parseInt(searchParams.get("limit") ?? "50", 10);
  const reglas = readReglas(adminEmail);
  const total = reglas.length;
  const totalPages = Math.max(1, Math.ceil(total / limit));
  const start = (page - 1) * limit;

  return NextResponse.json({
    data: reglas.slice(start, start + limit),
    pagination: { page, limit, total, totalPages },
  });
}

export async function POST(request: NextRequest) {
  const user = requireAdmin(request);
  if (!user) {
    return NextResponse.json({ error: { code: "FORBIDDEN", message: "Solo administradores" } }, { status: 403 });
  }
  const adminEmail = getAdminEmail(user);

  try {
    const body = await request.json();
    const { metrica, operador, valor } = body;

    if (!metrica || !operador || valor == null) {
      return NextResponse.json(
        { error: { code: "VALIDATION_ERROR", message: "metrica, operador y valor son obligatorios" } },
        { status: 400 }
      );
    }

    addRegla({ metrica, operador, valor, adminEmail });
    return NextResponse.json({ message: "Regla creada exitosamente" }, { status: 201 });
  } catch {
    return NextResponse.json(
      { error: { code: "UNKNOWN_ERROR", message: "Error al procesar la solicitud" } },
      { status: 500 }
    );
  }
}
