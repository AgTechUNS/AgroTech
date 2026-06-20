import { NextRequest, NextResponse } from "next/server";
import { getRegla, updateRegla, deleteRegla } from "@/lib/data/store";
import { getAdminEmail, requireRole } from "@/lib/auth/token";

export async function GET(
  _request: NextRequest,
  { params }: { params: { id: string } }
) {
  const regla = getRegla(params.id);
  if (!regla) {
    return NextResponse.json({ error: { code: "NOT_FOUND", message: "Regla no encontrada" } }, { status: 404 });
  }
  return NextResponse.json(regla);
}

export async function PUT(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  const user = requireRole(request, ["ADMIN", "AGRONOMO"]);
  if (!user) {
    return NextResponse.json({ error: { code: "FORBIDDEN", message: "No autorizado" } }, { status: 403 });
  }
  const adminEmail = getAdminEmail(user);

  try {
    const regla = getRegla(params.id);
    if (!regla) {
      return NextResponse.json({ error: { code: "NOT_FOUND", message: "Regla no encontrada" } }, { status: 404 });
    }
    if (regla.adminEmail !== adminEmail) {
      return NextResponse.json({ error: { code: "FORBIDDEN", message: "No puedes editar reglas de otro administrador" } }, { status: 403 });
    }

    const body = await request.json();
    const { nombre, descripcion, metrica, operador, valor, camposAsignados } = body;

    const updateData: Record<string, unknown> = {};
    if (nombre !== undefined) updateData.nombre = nombre;
    if (descripcion !== undefined) updateData.descripcion = descripcion;
    if (metrica !== undefined) updateData.metrica = metrica;
    if (operador !== undefined) updateData.operador = operador;
    if (valor !== undefined) updateData.valor = valor;
    if (camposAsignados !== undefined) updateData.camposAsignados = camposAsignados;

    updateRegla(params.id, updateData);
    return NextResponse.json({ message: "Regla actualizada exitosamente" });
  } catch {
    return NextResponse.json(
      { error: { code: "UNKNOWN_ERROR", message: "Error al procesar la solicitud" } },
      { status: 500 }
    );
  }
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  const user = requireRole(request, ["ADMIN", "AGRONOMO"]);
  if (!user) {
    return NextResponse.json({ error: { code: "FORBIDDEN", message: "No autorizado" } }, { status: 403 });
  }
  const adminEmail = getAdminEmail(user);

  try {
    const regla = getRegla(params.id);
    if (!regla) {
      return NextResponse.json({ error: { code: "NOT_FOUND", message: "Regla no encontrada" } }, { status: 404 });
    }
    if (regla.adminEmail !== adminEmail) {
      return NextResponse.json({ error: { code: "FORBIDDEN", message: "No puedes eliminar reglas de otro administrador" } }, { status: 403 });
    }

    deleteRegla(params.id);
    return NextResponse.json({ message: "Regla eliminada exitosamente" });
  } catch {
    return NextResponse.json(
      { error: { code: "UNKNOWN_ERROR", message: "Error al procesar la solicitud" } },
      { status: 500 }
    );
  }
}
