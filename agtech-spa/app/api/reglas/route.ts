import { NextRequest, NextResponse } from "next/server";
import { readReglas, addRegla } from "@/lib/data/store";
import { getUserFromRequest, getAdminEmail, requireRole } from "@/lib/auth/token";
import { proxyToBackend } from "@/lib/proxy";
import crypto from "crypto";

export async function GET(request: NextRequest) {
  const proxy = await proxyToBackend(request, "/api/reglas", "GET");
  if (proxy) return proxy;
  const user = getUserFromRequest(request);
  if (!user) {
    return NextResponse.json({ error: { code: "UNAUTHORIZED", message: "No autenticado" } }, { status: 401 });
  }
  const adminEmail = getAdminEmail(user);
  const reglas = readReglas(adminEmail);
  return NextResponse.json({ data: reglas });
}

export async function POST(request: NextRequest) {
  const proxy = await proxyToBackend(request, "/api/reglas", "POST");
  if (proxy) return proxy;
  const user = requireRole(request, ["ADMIN", "AGRONOMO"]);
  if (!user) {
    return NextResponse.json({ error: { code: "FORBIDDEN", message: "No autorizado" } }, { status: 403 });
  }
  const adminEmail = getAdminEmail(user);

  try {
    const body = await request.json();
    const { nombre, descripcion, metrica, operador, valor, camposAsignados } = body;

    if (!nombre || !metrica || !operador || valor == null) {
      return NextResponse.json(
        { error: { code: "VALIDATION_ERROR", message: "nombre, metrica, operador y valor son obligatorios" } },
        { status: 400 }
      );
    }

    const id = crypto.randomUUID();
    addRegla({ id, nombre, descripcion, metrica, operador, valor, adminEmail, camposAsignados: camposAsignados ?? [] });
    return NextResponse.json({ message: "Regla creada exitosamente", id }, { status: 201 });
  } catch {
    return NextResponse.json(
      { error: { code: "UNKNOWN_ERROR", message: "Error al procesar la solicitud" } },
      { status: 500 }
    );
  }
}
