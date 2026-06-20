import { NextRequest, NextResponse } from "next/server";
import { readAgricultores, addAgricultor, findAgricultor } from "@/lib/data/store";
import { getAdminEmail, requireAdmin } from "@/lib/auth/token";

export async function GET(request: NextRequest) {
  const user = requireAdmin(request);
  if (!user) {
    return NextResponse.json({ error: { code: "FORBIDDEN", message: "No autorizado" } }, { status: 403 });
  }
  const adminEmail = getAdminEmail(user);
  const data = readAgricultores(adminEmail);
  return NextResponse.json({ data });
}

export async function POST(request: NextRequest) {
  const user = requireAdmin(request);
  if (!user) {
    return NextResponse.json({ error: { code: "FORBIDDEN", message: "Solo administradores" } }, { status: 403 });
  }
  const adminEmail = getAdminEmail(user);

  try {
    const body = await request.json();
    const { email, nombre, password } = body;

    if (!email || !nombre || !password) {
      return NextResponse.json(
        { error: { code: "VALIDATION_ERROR", message: "email, nombre y password son obligatorios" } },
        { status: 400 }
      );
    }

    const existe = findAgricultor(email);
    if (existe) {
      return NextResponse.json(
        { error: { code: "CONFLICT", message: "Ya existe un agricultor con ese email" } },
        { status: 409 }
      );
    }

    addAgricultor({ email, nombre, password, rol: "agricultor", adminEmail });
    return NextResponse.json({ message: "Agricultor creado exitosamente" }, { status: 201 });
  } catch {
    return NextResponse.json(
      { error: { code: "UNKNOWN_ERROR", message: "Error al procesar la solicitud" } },
      { status: 500 }
    );
  }
}
