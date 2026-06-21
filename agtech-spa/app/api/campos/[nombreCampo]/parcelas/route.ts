import { NextRequest, NextResponse } from "next/server";
import { readParcelas, addParcela, readCampos } from "@/lib/data/store";
import { getUserFromRequest, getAdminEmail, requireAdmin } from "@/lib/auth/token";
import { proxyToBackend } from "@/lib/proxy";

export async function GET(
  request: NextRequest,
  { params }: { params: { nombreCampo: string } }
) {
  const proxy = await proxyToBackend(request, `/api/campos/${params.nombreCampo}/parcelas`, "GET");
  if (proxy && proxy.status < 400) return proxy;
  const user = getUserFromRequest(request);
  if (!user) {
    return NextResponse.json({ error: { code: "UNAUTHORIZED", message: "No autenticado" } }, { status: 401 });
  }
  const adminEmail = getAdminEmail(user);
  const nombreCampo = decodeURIComponent(params.nombreCampo);

  const parcelas = readParcelas(adminEmail, nombreCampo);

  return NextResponse.json({
    data: parcelas,
    pagination: { page: 1, limit: 50, total: parcelas.length, totalPages: 1 },
  });
}

export async function POST(
  request: NextRequest,
  { params }: { params: { nombreCampo: string } }
) {
  const user = requireAdmin(request);
  if (!user) {
    return NextResponse.json({ error: { code: "FORBIDDEN", message: "Solo administradores" } }, { status: 403 });
  }
  const adminEmail = getAdminEmail(user);

  try {
    const nombreCampo = decodeURIComponent(params.nombreCampo);
    const body = await request.json();
    const { nombreParcela, descripcionParcela, coordenadasParcela, nombreCultivo, variedad } = body;

    if (!nombreParcela || !coordenadasParcela) {
      return NextResponse.json(
        { error: { code: "VALIDATION_ERROR", message: "nombreParcela y coordenadasParcela son obligatorios" } },
        { status: 400 }
      );
    }

    const campos = readCampos(adminEmail);
    const campoExiste = campos.find((c) => c.nombreCampo === nombreCampo);
    if (!campoExiste) {
      return NextResponse.json(
        { error: { code: "NOT_FOUND", message: "El campo no existe" } },
        { status: 404 }
      );
    }

    const parcelas = readParcelas(adminEmail, nombreCampo);
    const existe = parcelas.find((p) => p.nombreParcela === nombreParcela);
    if (existe) {
      return NextResponse.json(
        { error: { code: "CONFLICT", message: "Ya existe una parcela con ese nombre en este campo" } },
        { status: 409 }
      );
    }

    addParcela({
      nombreParcela,
      nombreCampo,
      descripcionParcela,
      coordenadasParcela,
      nombreCultivo: nombreCultivo ?? null,
      variedad: variedad ?? null,
      adminEmail,
    });

    return NextResponse.json(
      { message: "Parcela creada exitosamente" },
      { status: 201, headers: { Location: `/campos/${encodeURIComponent(nombreCampo)}` } }
    );
  } catch {
    return NextResponse.json(
      { error: { code: "UNKNOWN_ERROR", message: "Error al procesar la solicitud" } },
      { status: 500 }
    );
  }
}
