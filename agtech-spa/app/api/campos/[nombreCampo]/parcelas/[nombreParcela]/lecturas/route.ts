import { NextRequest, NextResponse } from "next/server";
import { readSensoresPorParcela } from "@/lib/data/store";
import { getUserFromRequest, getAdminEmail } from "@/lib/auth/token";
import { Lectura } from "@/lib/types";

export async function GET(
  request: NextRequest,
  { params }: { params: { nombreCampo: string; nombreParcela: string } }
) {
  const user = getUserFromRequest(request);
  if (!user) {
    return NextResponse.json({ error: { code: "UNAUTHORIZED", message: "No autenticado" } }, { status: 401 });
  }
  const adminEmail = getAdminEmail(user);

  const nombreCampo = decodeURIComponent(params.nombreCampo);
  const nombreParcela = decodeURIComponent(params.nombreParcela);
  const sensores = readSensoresPorParcela(adminEmail, nombreCampo, nombreParcela);
  const activos = sensores.filter((s) => s.activo);

  const now = Date.now();
  const lecturas: Lectura[] = [];

  for (const sensor of activos) {
    for (let i = 48; i >= 1; i--) {
      const ts = new Date(now - i * 30 * 60 * 1000).toISOString();
      lecturas.push({
        sensorId: sensor.deviceId,
        timestamp: ts,
        temperatura: parseFloat((15 + Math.random() * 20).toFixed(2)),
        humedad: parseFloat((30 + Math.random() * 50).toFixed(2)),
      });
    }
  }

  return NextResponse.json({ data: lecturas });
}
