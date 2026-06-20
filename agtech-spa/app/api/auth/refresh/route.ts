import { NextResponse } from "next/server";
import { findUsuario } from "@/lib/data/store";

function btoaSafe(s: string): string {
  return Buffer.from(s).toString("base64").replace(/=/g, "").replace(/\+/g, "-").replace(/\//g, "_");
}

export async function POST(request: Request) {
  try {
    const { refreshToken } = await request.json();
    if (!refreshToken) {
      return NextResponse.json({ error: { code: "VALIDATION_ERROR", message: "refreshToken requerido" } }, { status: 400 });
    }

    let payload: { sub: string };
    try {
      const decoded = Buffer.from(refreshToken.replace(/-/g, "+").replace(/_/g, "/"), "base64").toString();
      payload = JSON.parse(decoded);
    } catch {
      return NextResponse.json({ error: { code: "INVALID_TOKEN", message: "Token inválido" } }, { status: 401 });
    }

    const user = findUsuario(payload.sub);
    if (!user) {
      return NextResponse.json({ error: { code: "USER_NOT_FOUND", message: "Usuario no encontrado" } }, { status: 401 });
    }

    const now = Math.floor(Date.now() / 1000);
    const newPayload = {
      sub: user.email,
      email: user.email,
      role: user.rol,
      name: user.nombre,
      iat: now,
      exp: now + 86400,
    };
    if (user.adminEmail) (newPayload as Record<string, unknown>).adminEmail = user.adminEmail;

    const accessToken = [
      btoaSafe(JSON.stringify({ alg: "HS256", typ: "JWT" })),
      btoaSafe(JSON.stringify(newPayload)),
      "mocksignature",
    ].join(".");

    return NextResponse.json({ accessToken, tokenType: "Bearer", expiresIn: 86400 });
  } catch {
    return NextResponse.json({ error: { code: "UNKNOWN_ERROR", message: "Error al procesar la solicitud" } }, { status: 500 });
  }
}
