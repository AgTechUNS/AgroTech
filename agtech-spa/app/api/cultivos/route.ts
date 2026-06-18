import { NextRequest, NextResponse } from "next/server";
import { readCultivos, addCultivo } from "@/lib/data/store";

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const page = parseInt(searchParams.get("page") ?? "1", 10);
  const limit = parseInt(searchParams.get("limit") ?? "50", 10);
  const cultivos = readCultivos();
  const total = cultivos.length;
  const totalPages = Math.max(1, Math.ceil(total / limit));
  const start = (page - 1) * limit;

  return NextResponse.json({
    data: cultivos.slice(start, start + limit),
    pagination: { page, limit, total, totalPages },
  });
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { nombreCultivo, umbralHumedadMinima } = body;

    if (!nombreCultivo || umbralHumedadMinima == null) {
      return NextResponse.json(
        { error: { code: "VALIDATION_ERROR", message: "nombreCultivo y umbralHumedadMinima son obligatorios" } },
        { status: 400 }
      );
    }

    const cultivos = readCultivos();
    const existe = cultivos.find((c) => c.nombreCultivo === nombreCultivo);
    if (existe) {
      return NextResponse.json(
        { error: { code: "CONFLICT", message: "Ya existe un cultivo con ese nombre" } },
        { status: 409 }
      );
    }

    addCultivo({ nombreCultivo, umbralHumedadMinima });
    return NextResponse.json({ message: "Cultivo creado exitosamente" }, { status: 201 });
  } catch {
    return NextResponse.json(
      { error: { code: "UNKNOWN_ERROR", message: "Error al procesar la solicitud" } },
      { status: 500 }
    );
  }
}
