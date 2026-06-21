import { NextRequest, NextResponse } from "next/server";
import { readParcelas, updateParcela, deleteParcela } from "@/lib/data/store";
import { getUserFromRequest, getAdminEmail, requireAdmin } from "@/lib/auth/token";
import { proxyToBackend } from "@/lib/proxy";

export async function GET(
  request: NextRequest,
  { params }: { params: { nombreCampo: string; nombreParcela: string } }
) {
  const proxy = await proxyToBackend(request, `/api/campos/${params.nombreCampo}/parcelas/${params.nombreParcela}`, "GET");
  if (proxy) return proxy;
  const user = getUserFromRequest(request);
  if (!user) {
    return NextResponse.json({ error: { code: "UNAUTHORIZED", message: "No autenticado" } }, { status: 401 });
  }
  const adminEmail = getAdminEmail(user);
  const nombreCampo = decodeURIComponent(params.nombreCampo);
  const nombreParcela = decodeURIComponent(params.nombreParcela);

  const parcelas = readParcelas(adminEmail, nombreCampo);
  const parcela = parcelas.find((p) => p.nombreParcela === nombreParcela);
  if (!parcela) {
    return NextResponse.json({ error: { code: "NOT_FOUND", message: "Parcela no encontrada" } }, { status: 404 });
  }
  return NextResponse.json(parcela);
}

export async function PUT(
  request: NextRequest,
  { params }: { params: { nombreCampo: string; nombreParcela: string } }
) {
  const proxy = await proxyToBackend(request, `/api/campos/${params.nombreCampo}/parcelas/${params.nombreParcela}`, "PUT");
  if (proxy) return proxy;
  const user = requireAdmin(request);
  if (!user) {
    return NextResponse.json({ error: { code: "FORBIDDEN", message: "Solo administradores" } }, { status: 403 });
  }
  const adminEmail = getAdminEmail(user);
  const nombreCampo = decodeURIComponent(params.nombreCampo);
  const nombreParcela = decodeURIComponent(params.nombreParcela);

  try {
    const parcelas = readParcelas(adminEmail, nombreCampo);
    const existe = parcelas.find((p) => p.nombreParcela === nombreParcela);
    if (!existe) {
      return NextResponse.json({ error: { code: "NOT_FOUND", message: "Parcela no encontrada" } }, { status: 404 });
    }

    const body = await request.json();
    const { descripcionParcela, coordenadasParcela, nombreCultivo, variedad } = body;

    updateParcela(nombreCampo, nombreParcela, {
      descripcionParcela,
      coordenadasParcela,
      nombreCultivo: nombreCultivo ?? null,
      variedad: variedad ?? null,
    });
    return NextResponse.json({ message: "Parcela actualizada exitosamente" });
  } catch {
    return NextResponse.json(
      { error: { code: "UNKNOWN_ERROR", message: "Error al procesar la solicitud" } },
      { status: 500 }
    );
  }
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: { nombreCampo: string; nombreParcela: string } }
) {
  const proxy = await proxyToBackend(request, `/api/campos/${params.nombreCampo}/parcelas/${params.nombreParcela}`, "DELETE");
  if (proxy) return proxy;
  const user = requireAdmin(request);
  if (!user) {
    return NextResponse.json({ error: { code: "FORBIDDEN", message: "Solo administradores" } }, { status: 403 });
  }
  const adminEmail = getAdminEmail(user);
  const nombreCampo = decodeURIComponent(params.nombreCampo);
  const nombreParcela = decodeURIComponent(params.nombreParcela);

  try {
    const parcelas = readParcelas(adminEmail, nombreCampo);
    const existe = parcelas.find((p) => p.nombreParcela === nombreParcela);
    if (!existe) {
      return NextResponse.json({ error: { code: "NOT_FOUND", message: "Parcela no encontrada" } }, { status: 404 });
    }

    deleteParcela(nombreCampo, nombreParcela);
    return NextResponse.json({ message: "Parcela eliminada exitosamente" });
  } catch {
    return NextResponse.json(
      { error: { code: "UNKNOWN_ERROR", message: "Error al procesar la solicitud" } },
      { status: 500 }
    );
  }
}
