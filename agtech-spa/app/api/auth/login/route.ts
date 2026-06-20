import { NextResponse } from "next/server";
import { findAgricultor } from "@/lib/data/store";

function btoaSafe(s: string): string {
  return Buffer.from(s).toString("base64").replace(/=/g, "").replace(/\+/g, "-").replace(/\//g, "_");
}

function createToken(email: string, role: "ADMIN" | "agricultor", nombre: string, adminEmail?: string) {
  const header = { alg: "HS256", typ: "JWT" };
  const now = Math.floor(Date.now() / 1000);
  const payload: Record<string, unknown> = {
    sub: email,
    email,
    role,
    name: nombre,
    iat: now,
    exp: now + 86400,
  };
  if (adminEmail) payload.adminEmail = adminEmail;
  const accessToken = [
    btoaSafe(JSON.stringify(header)),
    btoaSafe(JSON.stringify(payload)),
    "mocksignature",
  ].join(".");
  return { accessToken, refreshToken: accessToken, tokenType: "Bearer", expiresIn: 86400 };
}

export async function POST(request: Request) {
  try {
    const { email, password } = await request.json();
    if (!email || !password) {
      return NextResponse.json({ error: { code: "VALIDATION_ERROR", message: "Email y contraseña son obligatorios" } }, { status: 400 });
    }

    const user = findAgricultor(email);
    if (!user || user.password !== password) {
      return NextResponse.json({ error: { code: "CREDENTIALS_INVALID", message: "Email o contraseña incorrectos" } }, { status: 401 });
    }

    const tokens = createToken(user.email, user.rol, user.nombre, user.adminEmail);
    return NextResponse.json(tokens);
  } catch {
    return NextResponse.json({ error: { code: "UNKNOWN_ERROR", message: "Error al procesar la solicitud" } }, { status: 500 });
  }
}
