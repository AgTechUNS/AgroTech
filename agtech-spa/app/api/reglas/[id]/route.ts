import { NextRequest, NextResponse } from "next/server";
import { readReglas, updateRegla, deleteRegla } from "@/lib/data/store";
import { getUserFromRequest, getAdminEmail, requireAdmin } from "@/lib/auth/token";

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

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  const user = getUserFromRequest(request);
  if (!user) {
    return NextResponse.json({ error: { code: "UNAUTHORIZED", message: "No autenticado" } }, { status: 401 });
  }
  const adminEmail = getAdminEmail(user);
  const reglas = readReglas(adminEmail);
  const regla = reglas.find((r) => r.id === params.id);
  if (!regla) {
    return NextResponse.json({ error: { code: "NOT_FOUND", message: "Regla no encontrada" } }, { status: 404 });
  }
  return NextResponse.json(regla);
}

export async function PUT(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  const user = requireAdmin(request);
  if (!user) {
    return NextResponse.json({ error: { code: "FORBIDDEN", message: "Solo administradores" } }, { status: 403 });
  }
  const adminEmail = getAdminEmail(user);

  try {
    const reglas = readReglas(adminEmail);
    const existe = reglas.find((r) => r.id === params.id);
    if (!existe) {
      return NextResponse.json({ error: { code: "NOT_FOUND", message: "Regla no encontrada" } }, { status: 404 });
    }

    const body = await request.json();
    const { nombre, descripcion, metrica, operador, umbral, nombreCampo, habilitada } = body;

    const updateData: Partial<typeof existe> = {};
    if (nombre !== undefined) updateData.nombre = nombre;
    if (descripcion !== undefined) updateData.descripcion = descripcion;
    if (metrica !== undefined) updateData.metrica = metrica;
    if (operador !== undefined) updateData.operador = operador;
    if (umbral !== undefined) updateData.umbral = umbral;
    if (nombreCampo !== undefined) updateData.nombreCampo = nombreCampo;
    if (habilitada !== undefined) updateData.habilitada = habilitada;

    const finalMetrica = updateData.metrica ?? existe.metrica;
    const finalOperador = updateData.operador ?? existe.operador;
    const finalUmbral = updateData.umbral ?? existe.umbral;
    updateData.formula = generarFormula(finalMetrica, finalOperador, finalUmbral);

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
  const user = requireAdmin(request);
  if (!user) {
    return NextResponse.json({ error: { code: "FORBIDDEN", message: "Solo administradores" } }, { status: 403 });
  }
  const adminEmail = getAdminEmail(user);

  try {
    const reglas = readReglas(adminEmail);
    const existe = reglas.find((r) => r.id === params.id);
    if (!existe) {
      return NextResponse.json({ error: { code: "NOT_FOUND", message: "Regla no encontrada" } }, { status: 404 });
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
