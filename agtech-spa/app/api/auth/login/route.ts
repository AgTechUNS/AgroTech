import { NextRequest, NextResponse } from "next/server";
import { findUsuario } from "@/lib/data/store";
import { UserRole } from "@/lib/types";

const BACKEND_URL = process.env.BACKEND_URL;

function btoaSafe(s: string): string {
  return Buffer.from(s).toString("base64").replace(/=/g, "").replace(/\+/g, "-").replace(/\//g, "_");
}

function createToken(email: string, role: UserRole, nombre: string, adminEmail?: string) {
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
  const refreshToken = btoaSafe(JSON.stringify({ sub: email, exp: now + 2592000 }));
  return { accessToken, refreshToken, tokenType: "Bearer", expiresIn: 86400 };
}

export async function POST(request: NextRequest) {
  if (BACKEND_URL) {
    try {
      const body = await request.text();
      const res = await fetch(`${BACKEND_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body,
      });
      const data = await res.text();
      return new NextResponse(data, {
        status: res.status,
        headers: { "Content-Type": "application/json" },
      });
    } catch {
      return NextResponse.json(
        { error: { code: "PROXY_ERROR", message: `Error al conectar con backend en ${BACKEND_URL}` } },
        { status: 502 }
      );
    }
  }

  try {
    const { emailUsuario, password } = await request.json();
    if (!emailUsuario || !password) {
      return NextResponse.json({ error: { code: "VALIDATION_ERROR", message: "Email y contraseña son obligatorios" } }, { status: 400 });
    }

    const user = findUsuario(emailUsuario);
    if (!user || user.password !== password) {
      return NextResponse.json({ error: { code: "CREDENTIALS_INVALID", message: "Email o contraseña incorrectos" } }, { status: 401 });
    }

    const tokens = createToken(user.email, user.rol, user.nombre, user.adminEmail);
    return NextResponse.json(tokens);
  } catch {
    return NextResponse.json({ error: { code: "UNKNOWN_ERROR", message: "Error al procesar la solicitud" } }, { status: 500 });
  }
}
