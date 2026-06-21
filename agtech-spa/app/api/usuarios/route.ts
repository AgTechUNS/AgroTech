import { NextRequest, NextResponse } from "next/server";
import { readUsuarios, addUsuario, findUsuario } from "@/lib/data/store";
import { getAdminEmail, requireAdmin } from "@/lib/auth/token";
import { proxyToBackend } from "@/lib/proxy";
import { UserRole } from "@/lib/types";

const VALID_ROLES: UserRole[] = ["ADMIN", "AGRONOMO", "PRODUCTOR"];

export async function GET(request: NextRequest) {
  const proxy = await proxyToBackend(request, "/api/usuarios", "GET");
  if (proxy) return proxy;
  const user = requireAdmin(request);
  if (!user) {
    return NextResponse.json({ error: { code: "FORBIDDEN", message: "No autorizado" } }, { status: 403 });
  }
  const adminEmail = getAdminEmail(user);
  const data = readUsuarios(adminEmail);
  return NextResponse.json({ data });
}

export async function POST(request: NextRequest) {
  const proxy = await proxyToBackend(request, "/api/usuarios", "POST");
  if (proxy) return proxy;
  const user = requireAdmin(request);
  if (!user) {
    return NextResponse.json({ error: { code: "FORBIDDEN", message: "Solo administradores" } }, { status: 403 });
  }
  const adminEmail = getAdminEmail(user);

  try {
    const body = await request.json();
    const { email, rol } = body;

    if (!email || !rol) {
      return NextResponse.json(
        { error: { code: "VALIDATION_ERROR", message: "email y rol son obligatorios" } },
        { status: 400 }
      );
    }

    if (!VALID_ROLES.includes(rol)) {
      return NextResponse.json(
        { error: { code: "VALIDATION_ERROR", message: `Rol inválido. Valores: ${VALID_ROLES.join(", ")}` } },
        { status: 400 }
      );
    }

    const existe = findUsuario(email);
    if (existe) {
      return NextResponse.json(
        { error: { code: "CONFLICT", message: "Ya existe un usuario con ese email" } },
        { status: 409 }
      );
    }

    addUsuario({ email, nombre: email, password: "12345678", rol, adminEmail });
    return NextResponse.json({ message: "Usuario creado exitosamente" }, { status: 201 });
  } catch {
    return NextResponse.json(
      { error: { code: "UNKNOWN_ERROR", message: "Error al procesar la solicitud" } },
      { status: 500 }
    );
  }
}
