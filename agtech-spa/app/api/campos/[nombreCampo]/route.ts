import { NextRequest, NextResponse } from "next/server";
import { readCampos, updateCampo, deleteCampo, deleteParcelasByCampo } from "@/lib/data/store";
import { getUserFromRequest, getAdminEmail, requireAdmin } from "@/lib/auth/token";

export async function GET(
  request: NextRequest,
  { params }: { params: { nombreCampo: string } }
) {
  const user = getUserFromRequest(request);
  if (!user) {
    return NextResponse.json({ error: { code: "UNAUTHORIZED", message: "No autenticado" } }, { status: 401 });
  }
  const adminEmail = getAdminEmail(user);
  const nombreCampo = decodeURIComponent(params.nombreCampo);
  const campos = readCampos(adminEmail);
  const campo = campos.find((c) => c.nombreCampo === nombreCampo);
  if (!campo) {
    return NextResponse.json({ error: { code: "NOT_FOUND", message: "Campo no encontrado" } }, { status: 404 });
  }
  return NextResponse.json(campo);
}

export async function PUT(
  request: NextRequest,
  { params }: { params: { nombreCampo: string } }
) {
  const user = requireAdmin(request);
  if (!user) {
    return NextResponse.json({ error: { code: "FORBIDDEN", message: "Solo administradores" } }, { status: 403 });
  }
  const adminEmail = getAdminEmail(user);
  const nombreCampo = decodeURIComponent(params.nombreCampo);

  try {
    const campos = readCampos(adminEmail);
    const existe = campos.find((c) => c.nombreCampo === nombreCampo);
    if (!existe) {
      return NextResponse.json({ error: { code: "NOT_FOUND", message: "Campo no encontrado" } }, { status: 404 });
    }

    const body = await request.json();
    const { descripcionCampo, coordenadasCampo } = body;

    updateCampo(nombreCampo, { descripcionCampo, coordenadasCampo, adminEmail });
    return NextResponse.json({ message: "Campo actualizado exitosamente" });
  } catch {
    return NextResponse.json(
      { error: { code: "UNKNOWN_ERROR", message: "Error al procesar la solicitud" } },
      { status: 500 }
    );
  }
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: { nombreCampo: string } }
) {
  const user = requireAdmin(request);
  if (!user) {
    return NextResponse.json({ error: { code: "FORBIDDEN", message: "Solo administradores" } }, { status: 403 });
  }
  const adminEmail = getAdminEmail(user);
  const nombreCampo = decodeURIComponent(params.nombreCampo);

  try {
    const campos = readCampos(adminEmail);
    const existe = campos.find((c) => c.nombreCampo === nombreCampo);
    if (!existe) {
      return NextResponse.json({ error: { code: "NOT_FOUND", message: "Campo no encontrado" } }, { status: 404 });
    }

    deleteCampo(nombreCampo);
    deleteParcelasByCampo(nombreCampo);
    return NextResponse.json({ message: "Campo eliminado exitosamente" });
  } catch {
    return NextResponse.json(
      { error: { code: "UNKNOWN_ERROR", message: "Error al procesar la solicitud" } },
      { status: 500 }
    );
  }
}
