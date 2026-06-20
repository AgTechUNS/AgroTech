import { NextRequest, NextResponse } from "next/server";
import { readReglas, addRegla } from "@/lib/data/store";
import { getUserFromRequest, getAdminEmail, requireAdmin } from "@/lib/auth/token";
import crypto from "crypto";

const METRICA_UNITS: Record<string, string> = {
  temperatura: "°C",
  humedad_suelo: "%",
  precipitacion: "mm",
  viento: "km/h",
  ndvi: "",
};

const OP_DISPLAY: Record<string, string> = {
  ">=": "≥", "<=": "≤", ">": ">", "<": "<", "==": "=",
};

function generarFormula(metrica: string, operador: string, umbral: number): string {
  const unidad = METRICA_UNITS[metrica] ?? "";
  const op = OP_DISPLAY[operador] ?? operador;
  return `${metrica} ${op} ${umbral}${unidad}`;
}

export async function GET(request: NextRequest) {
  const user = getUserFromRequest(request);
  if (!user) {
    return NextResponse.json({ error: { code: "UNAUTHORIZED", message: "No autenticado" } }, { status: 401 });
  }
  const adminEmail = getAdminEmail(user);

  const { searchParams } = new URL(request.url);
  const page = parseInt(searchParams.get("page") ?? "1", 10);
  const limit = parseInt(searchParams.get("limit") ?? "50", 10);
  const nombreCampo = searchParams.get("nombreCampo") || undefined;

  const reglas = readReglas(adminEmail, nombreCampo);
  const total = reglas.length;
  const totalPages = Math.max(1, Math.ceil(total / limit));
  const start = (page - 1) * limit;

  return NextResponse.json({
    data: reglas.slice(start, start + limit),
    pagination: { page, limit, total, totalPages },
  });
}

export async function POST(request: NextRequest) {
  const user = requireAdmin(request);
  if (!user) {
    return NextResponse.json({ error: { code: "FORBIDDEN", message: "Solo administradores" } }, { status: 403 });
  }
  const adminEmail = getAdminEmail(user);

  try {
    const body = await request.json();
    const { nombre, descripcion, metrica, operador, umbral, nombreCampo } = body;

    if (!nombre || !metrica || !operador || umbral == null || !nombreCampo) {
      return NextResponse.json(
        { error: { code: "VALIDATION_ERROR", message: "nombre, metrica, operador, umbral y nombreCampo son obligatorios" } },
        { status: 400 }
      );
    }

    const formula = generarFormula(metrica, operador, umbral);
    const id = crypto.randomUUID();

    addRegla({ id, nombre, descripcion, metrica, operador, umbral, formula, nombreCampo, habilitada: true, adminEmail });
    return NextResponse.json({ message: "Regla creada exitosamente", id }, { status: 201 });
  } catch {
    return NextResponse.json(
      { error: { code: "UNKNOWN_ERROR", message: "Error al procesar la solicitud" } },
      { status: 500 }
    );
  }
}
