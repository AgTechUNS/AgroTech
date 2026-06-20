import { NextRequest, NextResponse } from "next/server";
import { updateAgricultor, deleteAgricultor, findAgricultor } from "@/lib/data/store";
import { getAdminEmail, requireAdmin } from "@/lib/auth/token";

export async function PUT(
  request: NextRequest,
  { params }: { params: { email: string } }
) {
  const user = requireAdmin(request);
  if (!user) {
    return NextResponse.json({ error: { code: "FORBIDDEN", message: "Solo administradores" } }, { status: 403 });
  }
  const adminEmail = getAdminEmail(user);

  try {
    const email = decodeURIComponent(params.email);
    const body = await request.json();
    const { nombre, password } = body;

    const existe = findAgricultor(email);
    if (!existe) {
      return NextResponse.json(
        { error: { code: "NOT_FOUND", message: "Agricultor no encontrado" } },
        { status: 404 }
      );
    }

    if (existe.adminEmail && existe.adminEmail !== adminEmail) {
      return NextResponse.json(
        { error: { code: "FORBIDDEN", message: "No puedes editar agricultores de otro administrador" } },
        { status: 403 }
      );
    }

    updateAgricultor(email, { nombre, password });
    return NextResponse.json({ message: "Agricultor actualizado exitosamente" });
  } catch {
    return NextResponse.json(
      { error: { code: "UNKNOWN_ERROR", message: "Error al procesar la solicitud" } },
      { status: 500 }
    );
  }
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: { email: string } }
) {
  const user = requireAdmin(request);
  if (!user) {
    return NextResponse.json({ error: { code: "FORBIDDEN", message: "Solo administradores" } }, { status: 403 });
  }
  const adminEmail = getAdminEmail(user);

  try {
    const email = decodeURIComponent(params.email);

    const existe = findAgricultor(email);
    if (!existe) {
      return NextResponse.json(
        { error: { code: "NOT_FOUND", message: "Agricultor no encontrado" } },
        { status: 404 }
      );
    }

    if (existe.rol === "ADMIN") {
      return NextResponse.json(
        { error: { code: "FORBIDDEN", message: "No se puede eliminar al administrador" } },
        { status: 403 }
      );
    }

    if (existe.adminEmail && existe.adminEmail !== adminEmail) {
      return NextResponse.json(
        { error: { code: "FORBIDDEN", message: "No puedes eliminar agricultores de otro administrador" } },
        { status: 403 }
      );
    }

    deleteAgricultor(email);
    return NextResponse.json({ message: "Agricultor eliminado exitosamente" });
  } catch {
    return NextResponse.json(
      { error: { code: "UNKNOWN_ERROR", message: "Error al procesar la solicitud" } },
      { status: 500 }
    );
  }
}
