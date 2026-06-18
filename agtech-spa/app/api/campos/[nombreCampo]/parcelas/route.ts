import { NextRequest, NextResponse } from "next/server";
import { readParcelas, addParcela, readCampos } from "@/lib/data/store";

export async function GET(
  _request: NextRequest,
  { params }: { params: { nombreCampo: string } }
) {
  const nombreCampo = decodeURIComponent(params.nombreCampo);
  const parcelas = readParcelas(nombreCampo);

  return NextResponse.json({
    data: parcelas,
    pagination: { page: 1, limit: 50, total: parcelas.length, totalPages: 1 },
  });
}

export async function POST(
  request: NextRequest,
  { params }: { params: { nombreCampo: string } }
) {
  try {
    const nombreCampo = decodeURIComponent(params.nombreCampo);
    const body = await request.json();
    const { nombreParcela, descripcionParcela, coordenadasParcela, nombreCultivo } = body;

    if (!nombreParcela || !coordenadasParcela) {
      return NextResponse.json(
        { error: { code: "VALIDATION_ERROR", message: "nombreParcela y coordenadasParcela son obligatorios" } },
        { status: 400 }
      );
    }

    const campos = readCampos();
    const campoExiste = campos.find((c) => c.nombreCampo === nombreCampo);
    if (!campoExiste) {
      return NextResponse.json(
        { error: { code: "NOT_FOUND", message: "El campo no existe" } },
        { status: 404 }
      );
    }

    const parcelas = readParcelas(nombreCampo);
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
