import { NextRequest, NextResponse } from "next/server";
import { readReglas, addRegla } from "@/lib/data/store";

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const page = parseInt(searchParams.get("page") ?? "1", 10);
  const limit = parseInt(searchParams.get("limit") ?? "50", 10);
  const reglas = readReglas();
  const total = reglas.length;
  const totalPages = Math.max(1, Math.ceil(total / limit));
  const start = (page - 1) * limit;

  return NextResponse.json({
    data: reglas.slice(start, start + limit),
    pagination: { page, limit, total, totalPages },
  });
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { metrica, operador, valor } = body;

    if (!metrica || !operador || valor == null) {
      return NextResponse.json(
        { error: { code: "VALIDATION_ERROR", message: "metrica, operador y valor son obligatorios" } },
        { status: 400 }
      );
    }

    addRegla({ metrica, operador, valor });
    return NextResponse.json({ message: "Regla creada exitosamente" }, { status: 201 });
  } catch {
    return NextResponse.json(
      { error: { code: "UNKNOWN_ERROR", message: "Error al procesar la solicitud" } },
      { status: 500 }
    );
  }
}
