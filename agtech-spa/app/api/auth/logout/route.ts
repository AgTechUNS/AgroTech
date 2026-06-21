import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.BACKEND_URL;

export async function POST(request: NextRequest) {
  if (BACKEND_URL) {
    try {
      const authHeader = request.headers.get("Authorization");
      const headers: Record<string, string> = { "Content-Type": "application/json" };
      if (authHeader) headers["Authorization"] = authHeader;
      const res = await fetch(`${BACKEND_URL}/auth/logout`, {
        method: "POST",
        headers,
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

  return NextResponse.json(null, { status: 204 });
}
